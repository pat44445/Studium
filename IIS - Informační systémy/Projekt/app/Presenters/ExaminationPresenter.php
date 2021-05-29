<?php

namespace App\Presenters;

use App\Model\ExaminationService;
use App\Model\HealthProblemService;
use App\Model\ProcedureRequestService;
use App\Model\ReportService;
use App\Model\UserManager;
use App\Model\UserService;
use Exception;
use Nette\Application\AbortException;
use Nette\Application\UI\Form;

final class ExaminationPresenter extends LoggedPresenter
{
    /**
     * @var HealthProblemService
     * @inject
     */
    public $healthProblemService;

    /**
     * @var UserService
     * @inject
     */
    public $userService;

    /**
     * @var ExaminationService
     * @inject
     */
    public $examinationService;

    /**
     * @var ReportService
     * @inject
     */
    public $reportService;

    /**
     * @var ProcedureRequestService
     * @inject
     */
    public $procedureRequestService;

    /**
     * @var int|null
     */
    public $healthProblemId;

    /**
     * @var int|null
     */
    public $examinationId;

    public function startup()
    {
        parent::startup();

        $this->allowedRoles([UserManager::ROLE_ADMIN, UserManager::ROLE_DOCTOR, UserManager::ROLE_PATIENT]);
    }
    
    public function beforeRender()
    {
        parent::beforeRender();

        $this->template->healthProblemId = $this->healthProblemId;
    }

    public function actionList(int $healthProblemId)
    {
        $this->allowedRoles([UserManager::ROLE_ADMIN, UserManager::ROLE_DOCTOR, UserManager::ROLE_PATIENT]);
        
        $this->healthProblemId = $healthProblemId;

        $this->template->healthProblem = $this->healthProblemService->get($healthProblemId);
        $this->template->examinations = $this->examinationService->getAll($healthProblemId);
    }

    public function actionMy()
    {
        $this->allowedRoles([UserManager::ROLE_ADMIN, UserManager::ROLE_DOCTOR, UserManager::ROLE_PATIENT]);
        
        $this->template->examinations = $this->examinationService->getAllByUser($this->user->getId());
    }

    public function actionDetail(int $examinationId)
    {
        $this->allowedRoles([UserManager::ROLE_ADMIN, UserManager::ROLE_DOCTOR, UserManager::ROLE_PATIENT]);
        
        $this->template->stateMapping = ExaminationService::getStateList();
        $this->template->examination = $this->examinationService->get($examinationId);
        $this->template->reports = $this->reportService->getByExamination($examinationId);
        $this->template->procedureRequests = $this->procedureRequestService->getByExamination($examinationId);
    }

    public function actionCreate(int $healthProblemId)
    {
        $this->allowedRoles([UserManager::ROLE_ADMIN, UserManager::ROLE_DOCTOR]);
        
        $this->healthProblemId = $healthProblemId;
    }


    public function actionEdit(int $healthProblemId, int $examinationId)
    {
        $this->allowedRoles([UserManager::ROLE_ADMIN, UserManager::ROLE_DOCTOR]);
        
        $this->healthProblemId = $healthProblemId;
        $this->examinationId = $examinationId;

        $this['form']->setDefaults($this->examinationService->getDefaults($examinationId));
    }

    public function createComponentForm()
    {
        $form = new Form();

        $form->addTextArea('text', 'Text')
            ->addRule(Form::MAX_LENGTH, 'Maximální délka textu je 1000 znaků.', 300)
            ->setRequired('Text je povinný');

        $form->addSelect('doctor', 'Doktor')
            ->setItems($this->userService->getAllByRole(UserManager::ROLE_DOCTOR));

        $form->addSubmit('submit');

        $form->onSuccess[] = [$this, 'formSuccess'];

        return $form;
    }

    /**
     * @param Form $form
     * @throws AbortException
     */
    public function formSuccess(Form $form)
    {
        try {
            $this->examinationService->update($this->healthProblemId, $this->examinationId, $form->getValues());

            if ($this->examinationId !== null) {
                $this->flashMessage('Žádost o vyšetření byla upravena', 'success');
            } else {
                $this->flashMessage('Žádost o vyšetření byla vytvořena', 'success');
            }
        } catch (Exception $e) {
            if ($this->examinationId !== null) {
                $this->flashMessage('Žádost o vyšetření se nepodařilo upravit', 'danger');
            } else {
                $this->flashMessage('Žádost o vyšetření se nepodařilo vytvořit', 'danger');
            }
        }

        $this->redirect('Examination:list', ['healthProblemId' => $this->healthProblemId]);
    }

    /**
     * @param int $healthProblemId
     * @param int $examinationId
     * @throws AbortException
     */
    public function actionDelete(int $healthProblemId, int $examinationId)
    {
        $this->allowedRoles([UserManager::ROLE_ADMIN, UserManager::ROLE_DOCTOR]);
        
        try {
            $this->examinationService->delete($examinationId);

            $this->flashMessage('Žádost o vyšetření byla smazána', 'success');
        } catch (Exception $e) {
            $this->flashMessage('Žádost o vyšetření se nepodařilo vymazat', 'danger');
        }

        $this->redirect('Examination:list', ['healthProblemId' => $healthProblemId]);
    }

    /**
     * @param int $examinationId
     * @param string $state
     * @throws AbortException
     */
    public function actionStateChange(int $examinationId, string $state)
    {
        $this->allowedRoles([UserManager::ROLE_ADMIN, UserManager::ROLE_DOCTOR]);
        
        try {
            $this->examinationService->changeState($examinationId, $state);

            $this->flashMessage('Stav žádosti byl změněn', 'success');
        } catch (Exception $e) {
            $this->flashMessage('Stav žádosti se nepodařilo změnit', 'danger');
        }

        $this->redirect('Examination:detail', ['examinationId' => $examinationId]);
    }

}