<?php

namespace App\Model;

use InvalidArgumentException;
use Nette\Database\Context;
use Nette\Database\Table\ActiveRow;
use Nette\Security\Passwords;
use stdClass;

class UserService
{
    /** @var Context */
    private $db;

    /** @var Passwords */
    private $passwords;

    private const STATES = [
        0 => 'Dekativovaný',
        1 => 'Aktivní',
    ];

    public function __construct(Context $db, Passwords $passwords)
    {
        $this->db = $db;
        $this->passwords = $passwords;
    }

    public function getAll(): array
    {
        $data = [];

        $users = $this->db->table('User')->where(['is_deleted' => false])->fetchAll();

        foreach ($users as $user) {
            $data[] = [
                'id' => $user->id,
                'username' => $user->username,
                'role' => self::roles()[$user->role],
                'fullName' => $user->Full_name,
                'dateOfBirth' => $user->Date_of_birth,
                'function' => $user->Function,
                'is_active' => $user->is_active,
                'state' => self::STATES[$user->is_active],
            ];
        }

        return $data;
    }

    public function get(int $userId)
    {
        $user = $this->db->table('User')->get($userId);

        if ($user === null) {
            throw new InvalidArgumentException('User not found');
        }

        return $user;

    }

    public function delete(int $userId): void
    {
        $user = $this->db->table('User')->get($userId);

        if ($user === null) {
            throw new InvalidArgumentException('User not found');
        }
        
        if($user['role'] === 'patient')
        {
             $this->db->table('Health_problem')->where('patient_id', $userId)->delete();
        }

        $this->db->table('User')
            ->where('id', $userId)
            ->update(['is_deleted' => true]);
    }

    public function update(?int $id, stdClass $values)
    {
        $tableValues = [
            'username' => $values->username,
            'Full_name' => $values->fullName ?: null,
            'Date_of_birth' => Utils::dateStringToObject($values->date),
        ];

        if (isset($values->role)) {
            $tableValues['role'] = $values->role;
        }

        if (isset($values->function)) {
            $tableValues['Function'] = $values->function;
        }

        if (!empty($values->password)) {
            $tableValues['password'] = $this->passwords->hash($values->password);
        }

        if ($id === null) {
            $this->db->table('User')->insert($tableValues);
        } else {
            $user = $this->db->table('User')->get($id);

            if ($user === null) {
                throw new InvalidArgumentException('User not found');
            }

            $user->update($tableValues);
        }
    }

    public function getDefaults(?int $userId): array
    {
        if ($userId === null) {
            return [];
        }

        /** @var object $user */
        $user = $this->db->table('User')->get($userId);

        if ($user === null) {
            return [];
        }

        return [
            'username' => $user->username,
            'role' => $user->role,
            'fullName' => $user->Full_name,
            'date' => $user->Date_of_birth ? $user->Date_of_birth->format('Y-m-d') : null,
            'function' => $user->Function,
        ];
    }

    public static function roles(): array
    {
        return [
            UserManager::ROLE_PATIENT => 'Pacient',
            UserManager::ROLE_DOCTOR => 'Doktor',
            UserManager::ROLE_INSURANCE_WORKER => 'Pracovník zdravotní pojišťovny',
            UserManager::ROLE_ADMIN => 'Administrátor',
        ];
    }

    public function getAllByRole(string $role)
    {
        $data = [];

        $users = $this->db->table('User')->where(['role' => $role, 'is_deleted' => false])->fetchAll();

        foreach ($users as $user) {
            $data[$user->id] = $user->Full_name;
        }

        return $data;
    }

    public function flipState(int $userId)
    {
        /** @var ActiveRow $user */
        $user = $this->db->table('User')->get($userId);

        if ($user->is_active === 1) {
            $user->update(['is_active' => 0]);
        } else {
            $user->update(['is_active' => 1]);
        }
    }

    public function deleteDoctor(int $doctorId, int $newDoctorId)
    {
        $doctor = $this->db->table('User')->get($doctorId);

        //change responsible doctor
        $this->db->table(HealthProblemService::HEALTH_PROBLEM_TABLE)
            ->where(['doctor_id' => $doctorId])
            ->update(['doctor_id' => $newDoctorId]);

        $this->db->table(ExaminationService::EXAMINATION_TABLE)
            ->where(['doctor_id' => $doctorId])
            ->update(['doctor_id' => null]);

        $doctor->update(['is_deleted' => true]);
    }
}