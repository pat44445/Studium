<?php

namespace App\Model;

use InvalidArgumentException;
use Nette\Database\Context;
use Nette\Http\FileUpload;
use stdClass;

class ReportService
{
    private const REPORT_TABLE = 'Health_report';

    /** @var Context */
    private $db;

    public function __construct(Context $db)
    {
        $this->db = $db;
    }


    public function getAll(int $healthProblemId): array
    {
        $data = [];

        $reports = $this->db->table(self::REPORT_TABLE)->where(['Health_problem_id' => $healthProblemId]);

        /** @var stdClass $report */
        foreach ($reports as $report) {
            $data[] = [
                'id' => $report->id,
                'subject' => $report->Subject,
                'text' => $report->Text,
            ];
        }

        return $data;
    }

    public function getByExamination(int $examinationId): array
    {
        $data = [];

        $reports = $this->db->table(self::REPORT_TABLE)->where(['examination_id' => $examinationId]);

        /** @var stdClass $report */
        foreach ($reports as $report) {
            $data[] = [
                'id' => $report->id,
                'subject' => $report->Subject,
                'text' => $report->Text,
            ];
        }

        return $data;
    }

    public function getDefaults(?int $reportId): array
    {
        if ($reportId === null) {
            return [];
        }

        /** @var stdClass $report */
        $report = $this->db->table(self::REPORT_TABLE)->get($reportId);

        if ($report === null) {
            return [];
        }

        return [
            'subject' => $report->Subject,
            'text' => $report->Text,
            
        ];
    }

    public function update(?int $healthProblemId, ?int $examinationId, ?int $reportId, stdClass $values, int $doctorId)
    {
        //tyhle hodnoty se vkládají vždy
        $tableValues = [
            'Subject' => $values->subject,
            'Text' => $values->text,
            'DateTime'=> date('Y-m-d H:i:s'),
        ];

        //pokud byl vložen obrázek, vkládá se i obrázek (jinak se nepřepisuje)
        /** @var FileUpload $picture */
        $picture = $values->picture;
        if ($picture->isImage() && $picture->isOk()) {
            $tableValues['Picture'] = file_get_contents($picture->getTemporaryFile());
        }

        if ($examinationId !== null) {
            /** @var stdClass $examination */
            $examination = $this->db->table('Examination_request')->get($examinationId);
            $healthProblemId = $examination->health_problem_id;
        }

        if ($reportId === null) {
            //hodnota se vkládá jen při vytváření
            $tableValues['doctor_id'] = $doctorId;
            $tableValues['health_problem_id'] = $healthProblemId;
            $tableValues['examination_id'] = $examinationId;

            $this->db->table(self::REPORT_TABLE)->insert($tableValues);
        } else {
            $report = $this->db->table(self::REPORT_TABLE)->get($reportId);

            if (!$report) {
                throw new InvalidArgumentException('Health report not found');
            }

            $report->update($tableValues);
        }
    }

    public function delete(int $healthReportId)
    {
        $healthReport = $this->db->table(self::REPORT_TABLE)->get($healthReportId);

        if (!$healthReport) {
            throw new InvalidArgumentException('Health report not found');
        }

        $healthReport->delete();
    }

    public function get(int $healthReportId)
    {
        return $this->db->table(self::REPORT_TABLE)->get($healthReportId);
    }
}
