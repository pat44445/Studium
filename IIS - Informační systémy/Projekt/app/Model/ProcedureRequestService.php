<?php

namespace App\Model;

use InvalidArgumentException;
use Nette\Database\Context;
use stdClass;

class ProcedureRequestService
{
    public const TABLE = 'procedure_payment_request';

    public const STATE_REQUESTED = 'requested';
    public const STATE_ACCEPTED = 'accepted';
    public const STATE_REJECTED = 'rejected';

    /** @var Context */
    private $db;

    public function __construct(Context $db)
    {
        $this->db = $db;
    }

    public function create(int $examinationId, int $doctorId, stdClass $formValues)
    {
        $this->db->table(self::TABLE)->insert([
            'doctor_id' => $doctorId,
            'examination_id' => $examinationId,
            'procedure_id' => $formValues->procedure,
        ]);
    }

    public function delete(int $procedureRequestId)
    {
        $procedureRequest = $this->db->table(self::TABLE)->get($procedureRequestId);

        if (!$procedureRequest) {
            throw new InvalidArgumentException('Examination request not found');
        }

        $procedureRequest->delete();
    }

    public function getAll(): array
    {
        $data = [];

        $procedureRequests = $this->db->table(self::TABLE)->fetchAll();

        /** @var stdClass $procedureRequest */
        foreach ($procedureRequests as $procedureRequest) {
            $data[] = [
                'id' => $procedureRequest->id,
                'state' => self::getStateList()[$procedureRequest->state],
                'doctorName' => $procedureRequest->doctor->Full_name,
                'procedureName' => $procedureRequest->procedure->name,
                'price' => $procedureRequest->procedure->price,
            ];
        }

        return $data;
    }

    public function getByExamination(int $examinationId)
    {
        $data = [];

        $reports = $this->db->table(self::TABLE)->where(['examination_id' => $examinationId]);

        /** @var stdClass $report */
        foreach ($reports as $report) {
            $data[] = [
                'id' => $report->id,
                'state' => self::getStateList()[$report->state],
                'doctorName' => $report->doctor->Full_name,
                'procedureName' => $report->procedure->name,
            ];
        }

        return $data;
    }

    public static function getStateList(): array
    {
        return [
            self::STATE_REQUESTED => 'Zažádáno',
            self::STATE_ACCEPTED => 'Schváleno',
            self::STATE_REJECTED => 'Zamítnuto'
        ];
    }

    public function changeState(int $procedureRequestId, string $state)
    {
        if (!in_array($state, array_keys(self::getStateList()))) {
            throw new InvalidArgumentException('State not valid');
        }

        $procedureRequest = $this->db->table(self::TABLE)->get($procedureRequestId);

        if ($procedureRequest === null) {
            throw new InvalidArgumentException('ProcedureRequest not found');
        }

        $procedureRequest->update(['state' => $state]);
    }
}