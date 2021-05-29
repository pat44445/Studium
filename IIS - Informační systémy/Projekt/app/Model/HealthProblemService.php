<?php

namespace App\Model;

use InvalidArgumentException;
use Nette\Database\Context;
use stdClass;

class HealthProblemService
{
    public const STATE_NEW = 'new';
    public const STATE_ONGOING = 'ongoing';
    public const STATE_WAITING = 'waiting';
    public const STATE_CLOSED = 'closed';

    public const HEALTH_PROBLEM_TABLE = 'Health_problem';

    /** @var Context */
    private $db;

    public function __construct(Context $db)
    {
        $this->db = $db;
    }

    public function getAll(): array
    {
        $data = [];

        $healthProblems = $this->db->table(self::HEALTH_PROBLEM_TABLE)->fetchAll();

        foreach ($healthProblems as $healthProblem) {
            $data[] = [
                'id' => $healthProblem->id,
                'name' => $healthProblem->Name,
                'description' => $healthProblem->Description,
                'state' => self::getStateList()[$healthProblem->state],
                'patientName' => $healthProblem->patient->Full_name,
                'doctorName' => $healthProblem->doctor->Full_name,
            ];
        }

        return $data;
    }

    public function getForUser(int $userId)
    {
        /** @var stdClass $user */
        $user = $this->db->table('User')->get($userId);

        if ($user === null) {
            throw new InvalidArgumentException('User not found');
        }

        if ($user->role === UserManager::ROLE_ADMIN) {
            $healthProblems = $this->db->table(self::HEALTH_PROBLEM_TABLE)->fetchAll();
        } else if ($user->role === UserManager::ROLE_DOCTOR) {
            $healthProblems = $this->db->table(self::HEALTH_PROBLEM_TABLE)->where(['doctor_id' => $user->id])->fetchAll();
        } else {
            $healthProblems = $this->db->table(self::HEALTH_PROBLEM_TABLE)->where(['patient_id' => $user->id])->fetchAll();
        }

        $data = [];

        foreach ($healthProblems as $healthProblem) {
            $data[] = [
                'id' => $healthProblem->id,
                'name' => $healthProblem->Name,
                'description' => $healthProblem->Description,
                'state' => self::getStateList()[$healthProblem->state],
                'patientName' => $healthProblem->patient->Full_name,
                'doctorName' => $healthProblem->doctor->Full_name,
            ];
        }

        return $data;
    }

    public function get(int $healthProblemId)
    {
        return $this->db->table(self::HEALTH_PROBLEM_TABLE)->get($healthProblemId);
    }

    public function getDefaults(?int $healthProblemId)
    {
        if ($healthProblemId === null) {
            return [];
        }

        /** @var stdClass|null $healthProblem */
        $healthProblem = $this->db->table(self::HEALTH_PROBLEM_TABLE)->get($healthProblemId);

        if ($healthProblem === null) {
            return [];
        }

        return [
            'name' => $healthProblem->Name,
            'description' => $healthProblem->Description,
            'state' => $healthProblem->state,
            'doctor' => $healthProblem->doctor_id,
        ];
    }

    public function update(?int $healthProblemId, stdClass $values, int $doctorId)
    {
        $tableValues = [
            'Name' =>  $values->name,
            'Description' => $values->description,
            'state' => $values->state,
            'patient_id' => $values->patient,
        ];

        if ($healthProblemId === null) {
            $tableValues['doctor_id'] = $doctorId;

            $this->db->table(self::HEALTH_PROBLEM_TABLE)->insert($tableValues);
        } else {
            $tableValues['doctor_id'] = $values->doctor;

            $healthProblem = $this->db->table(self::HEALTH_PROBLEM_TABLE)->get($healthProblemId);

            if (!$healthProblem) {
                throw new InvalidArgumentException('Health problem not found');
            }

            $healthProblem->update($tableValues);
        }
    }

    public function delete(int $healthProblemId)
    {
        $healthProblem = $this->db->table(self::HEALTH_PROBLEM_TABLE)->get($healthProblemId);

        if (!$healthProblem) {
            throw new InvalidArgumentException('Health problem not found');
        }

        $healthProblem->delete();
    }

    public static function getStateList()
    {
        return [
            self::STATE_NEW => 'Nový',
            self::STATE_ONGOING => 'Probíhající',
            self::STATE_WAITING => 'Čekající na vyšetření',
            self::STATE_CLOSED => 'Ukončený',
        ];
    }

    public function getExaminationWithoutDoctor(int $userId): ?string
    {
        $result = $this->db->query('select Hp.Name from Examination_request er
            left join Health_problem Hp on er.health_problem_id = Hp.id
            left join User U on Hp.doctor_id = U.id
            where U.id=? and er.doctor_id IS NULL and er.State != \'closed\'',$userId)->fetchAll();

        if (!empty($result)) {
            return $result[0]->Name;
        }

        return null;
    }
}