<?php

namespace App\Model;

use InvalidArgumentException;
use Nette\Database\Context;
use stdClass;

class ProcedureService
{
    private const PROCEDURE_TABLE = 'procedure';

    /** @var Context */
    private $db;

    public function __construct(Context $db)
    {
        $this->db = $db;
    }

    public function getAll(): array
    {
        $data = [];

        $procedures = $this->db->table(self::PROCEDURE_TABLE)->fetchAll();

        foreach ($procedures as $procedure) {
            $data[] = [
                'id' => $procedure->id,
                'name' => $procedure->name,
                'price' => $procedure->price
            ];
        }

        return $data;
    }

    public function getList(): array
    {
        $data = [];

        $procedures = $this->db->table(self::PROCEDURE_TABLE)->fetchAll();

        foreach ($procedures as $procedure) {
            $data[$procedure->id] = $procedure->name;
        }

        return $data;
    }

    public function delete(int $procedureId): void
    {
        $procedure = $this->db->table(self::PROCEDURE_TABLE)->get($procedureId);

        if ($procedure === null) {
            throw new InvalidArgumentException('Procedure not found');
        }

        $procedure->delete();
    }

    public function update(?int $procedureId, stdClass $values)
    {
        $tableValues = [
            'name' => $values->name,
            'price' => $values->price,
        ];

        if ($procedureId === null) {
            $this->db->table(self::PROCEDURE_TABLE)->insert($tableValues);
        } else {
            $procedure = $this->db->table(self::PROCEDURE_TABLE)->get($procedureId);

            if ($procedure === null) {
                throw new InvalidArgumentException('Procedure not found');
            }

            $procedure->update($tableValues);
        }
    }

    public function getDefaults(?int $procedureId): array
    {
        if ($procedureId === null) {
            return [];
        }

        /** @var object $procedure */
        $procedure = $this->db->table(self::PROCEDURE_TABLE)->get($procedureId);

        if ($procedure === null) {
            return [];
        }

        return [
            'name' => $procedure->name,
            'price' => $procedure->price,
        ];
    }
}