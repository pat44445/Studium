<?php

namespace App\Model;

use InvalidArgumentException;
use Nette\Database\Context;
use stdClass;

class ExaminationService
{
    public const STATE_WAITING = 'waiting';
    public const STATE_IN_PROGRESS = 'in_progress';
    public const STATE_CLOSED = 'closed';

    public const EXAMINATION_TABLE = 'Examination_request';

    /** @var Context */
    private $db;

    public function __construct(Context $db)
    {
        $this->db = $db;
    }

    public function getAll(int $healthProblemId): array
    {
        $data = [];

        $reports = $this->db->table(self::EXAMINATION_TABLE)->where(['Health_problem_id' => $healthProblemId]);

        /** @var stdClass $report */
        foreach ($reports as $report) {
            $data[] = [
                'datetime' => $report->DateTime,
                'id' => $report->id,
                'state' => self::getStateList()[$report->State],
                'text' => $report->Text,
                'doctorName' => $report->doctor ? $report->doctor->Full_name : '',
            ];
        }

        return $data;
    }

    public function getAllByUser(int $doctorId): array
    {
        $data = [];

        $reports = $this->db->table(self::EXAMINATION_TABLE)->where(['doctor_id' => $doctorId]);

        /** @var stdClass $report */
        foreach ($reports as $report) {
            $data[] = [
                'datetime' => $report->DateTime,
                'id' => $report->id,
                'state' => self::getStateList()[$report->State],
                'text' => $report->Text,
            ];
        }

        return $data;
    }

    public function get(int $examinationId)
    {
        return $this->db->table(self::EXAMINATION_TABLE)->get($examinationId);
    }

    public function getDefaults(?int $examinationId): array
    {
        if ($examinationId === null) {
            return [];
        }

        /** @var stdClass $examination */
        $examination = $this->db->table(self::EXAMINATION_TABLE)->get($examinationId);

        if ($examination === null) {
            return [];
        }

        return [
            'datetime' => $examination->DateTime,
            'state' => $examination->State,
            'text' => $examination->Text,
            'doctor' => $examination->doctor_id,
        ];
    }

    public function update(int $healthProblemId, ?int $examinationId, stdClass $values)
    {
        //tyhle hodnoty se vkládají vždy
        $tableValues = [
            'Text' => $values->text,
            'State' => 'waiting',
            'doctor_id' => $values->doctor,
        ];

        if ($examinationId === null) {
            $tableValues['DateTime'] = date('Y-m-d H:i:s');
            $tableValues['health_problem_id'] = $healthProblemId;

            $this->db->table(self::EXAMINATION_TABLE)->insert($tableValues);
        } else {
            $examination = $this->db->table(self::EXAMINATION_TABLE)->get($examinationId);

            if (!$examination) {
                throw new InvalidArgumentException('Examination request not found');
            }

            $examination->update($tableValues);
        }
    }

    public function delete(int $examinationId)
    {
        $examination = $this->db->table(self::EXAMINATION_TABLE)->get($examinationId);

        if (!$examination) {
            throw new InvalidArgumentException('Examination request not found');
        }

        $examination->delete();
    }

    public static function getStateList()
    {
        return [
            self::STATE_WAITING => 'Čeká na vyřízení',
            self::STATE_IN_PROGRESS => 'Vyřizuje se',
            self::STATE_CLOSED => 'Dokončeno',
        ];
    }

    public function changeState(int $examinationId, string $state)
    {
        if (!in_array($state, array_keys(self::getStateList()))) {
            throw new InvalidArgumentException('State not valid');
        }

        $examination = $this->db->table(self::EXAMINATION_TABLE)->get($examinationId);

        if ($examination === null) {
            throw new InvalidArgumentException('Examination not found');
        }

        $examination->update(['state' => $state]);
    }

}