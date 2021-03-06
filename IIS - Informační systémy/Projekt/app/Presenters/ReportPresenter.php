<?php

namespace App\Presenters;

use App\Model\HealthProblemService;
use App\Model\ReportService;
use App\Model\UserManager;
use Exception;
use Nette\Application\AbortException;
use Nette\Application\UI\Form;
use stdClass;

class ReportPresenter extends LoggedPresenter
{
    /**
     * @var ReportService
     * @inject
     */
    public $reportService;

    /**
     * @var HealthProblemService
     * @inject
     */
    public $healthProblemService;

    /**
     * @var int|null
     */
    public $healthProblemId;

    /**
     * @var int|null
     */
    public $examinationId;

    /**
     * @var int|null
     */
    public $reportId;
    
    public $DateTime;

    public function startup()
    {
        parent::startup();

        $this->allowedRoles([UserManager::ROLE_ADMIN, UserManager::ROLE_DOCTOR, UserManager::ROLE_PATIENT]);
    }
    
    
    public function beforeRender()
    {
        parent::beforeRender();

        $this->template->examinationId = $this->examinationId;
        $this->template->healthProblemId = $this->healthProblemId;
    }

    public function actionList(int $healthProblemId)
    {
        $this->allowedRoles([UserManager::ROLE_ADMIN, UserManager::ROLE_DOCTOR, UserManager::ROLE_PATIENT]);
         
        $this->healthProblemId = $healthProblemId;

        $this->template->healthProblem = $this->healthProblemService->get($healthProblemId);
        $this->template->reports = $this->reportService->getAll($healthProblemId);
    }

    public function actionCreate(int $healthProblemId)
    {
        $this->allowedRoles([UserManager::ROLE_ADMIN, UserManager::ROLE_DOCTOR]);
        
        $this->healthProblemId = $healthProblemId;
    }

    public function actionCreateExamination(int $examinationId)
    {
        $this->allowedRoles([UserManager::ROLE_ADMIN, UserManager::ROLE_DOCTOR]);
        
        $this->examinationId = $examinationId;
    }

    public function actionEditExamination(int $examinationId, int $reportId)
    {
        $this->allowedRoles([UserManager::ROLE_ADMIN, UserManager::ROLE_DOCTOR]);
        
        $this->examinationId = $examinationId;
        $this->reportId = $reportId;

        $this['form']->setDefaults($this->reportService->getDefaults($reportId));
    }

    public function actionEdit(int $healthProblemId, int $reportId)
    {
        $this->allowedRoles([UserManager::ROLE_ADMIN, UserManager::ROLE_DOCTOR]);
        
        $this->healthProblemId = $healthProblemId;
        $this->reportId = $reportId;

        $this['form']->setDefaults($this->reportService->getDefaults($reportId));
    }

    public function createComponentForm()
    {
        $form = new Form();

        $form->addHidden('healthProblemId');
        $form->addHidden('reportId');

        $form->addText('subject', 'P??edm??t')
            ->addRule(Form::MAX_LENGTH, 'Maxim??ln?? d??lka textu je 50 znak??.', 50)
            ->setRequired('P??edm??t je povinn??');
        
        $form->addTextArea('text', 'Text')
            ->addRule(Form::MAX_LENGTH, 'Maxim??ln?? d??lka textu je 1000 znak??.', 1000)
            ->setRequired('Text je povinn??');

        $form->addUpload('picture', 'Obr??zek')
            ->setRequired(false);

        $form->addSubmit('submit', 'Ulo??i??');

        $form->onSuccess[] = [$this, 'formSuccess'];

        return $form;
    }

    /**
     * @param Form $form
     * @throws AbortException
     */
    public function formSuccess(Form $form)
    {
        $this->reportService->update($this->healthProblemId, $this->examinationId, $this->reportId, $form->getValues(), $this->user->getId());
        try {

            if ($this->reportId !== null) {
                $this->flashMessage('Zdravotn?? zpr??va byla upravena', 'success');
            } else {
                $this->flashMessage('Zdravotn?? zpr??va byla vytvo??ena', 'success');
            }
        } catch (Exception $e) {
            if ($this->reportId !== null) {
                $this->flashMessage('Zdravotn?? zpr??vu se nepoda??ilo upravit', 'danger');
            } else {
                $this->flashMessage('Zdravotn?? zpr??vu se nepoda??ilo vytvo??it', 'danger');
            }
        }

        if ($this->examinationId !== null) {
            $this->redirect('Examination:detail', ['examinationId' => $this->examinationId]);
        } else {
            $this->redirect('Report:list', ['healthProblemId' => $this->healthProblemId]);
        }
    }

    /**
     * @param int $healthProblemId
     * @param int $reportId
     * @throws AbortException
     */
    public function actionDelete(int $healthProblemId, int $reportId)
    {
        $this->allowedRoles([UserManager::ROLE_ADMIN, UserManager::ROLE_DOCTOR]);
        
        try {
            $this->reportService->delete($reportId);

            $this->flashMessage('Zdravotn?? zpr??va byla smaz??na', 'success');
        } catch (Exception $e) {
            $this->flashMessage('Zdravotn?? zpr??vu se nepoda??ilo vymazat', 'danger');
        }

        $this->redirect('Report:list', ['healthProblemId' => $healthProblemId]);
    }

    /**
     * @param int $examinationId
     * @param int $reportId
     * @throws AbortException
     */
    public function actionDeleteExamination(int $examinationId, int $reportId)
    {
        $this->allowedRoles([UserManager::ROLE_ADMIN, UserManager::ROLE_DOCTOR]);
        
        try {
            $this->reportService->delete($reportId);

            $this->flashMessage('Zdravotn?? zpr??va byla smaz??na', 'success');
        } catch (Exception $e) {
            $this->flashMessage('Zdravotn?? zpr??vu se nepoda??ilo vymazat', 'danger');
        }

        $this->redirect('Examination:detail', ['examinationId' => $examinationId]);
    }

    public function actionDetail(int $healthProblemId, int $reportId)
    {
        $this->allowedRoles([UserManager::ROLE_ADMIN, UserManager::ROLE_DOCTOR, UserManager::ROLE_PATIENT]);
        
        $this->healthProblemId = $healthProblemId;
        $this->template->report = $this->reportService->get($reportId);
    }

    public function actionDetailExamination(int $examinationId, int $reportId)
    {
        $this->allowedRoles([UserManager::ROLE_ADMIN, UserManager::ROLE_DOCTOR, UserManager::ROLE_PATIENT]);
        
        $this->examinationId = $examinationId;
        $this->template->report = $this->reportService->get($reportId);
    }

    public function actionImage(int $reportId)
    {
        $this->allowedRoles([UserManager::ROLE_ADMIN, UserManager::ROLE_DOCTOR]);
        
        /** @var stdClass $report */
        $report = $this->reportService->get($reportId);

        header('Content-type: image/png');
        echo $report->Picture;
    }
    
}
