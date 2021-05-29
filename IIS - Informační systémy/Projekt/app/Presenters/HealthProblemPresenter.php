<?php

namespace App\Presenters;

use App\Model\HealthProblemService;
use App\Model\UserManager;
use App\Model\UserService;
use Exception;
use Nette\Application\AbortException;
use Nette\Application\UI\Form;

class HealthProblemPresenter extends LoggedPresenter
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

    /** @var int|null */
    public $healthProblemId;

    public function startup()
    {
        parent::startup();

        $this->allowedRoles([UserManager::ROLE_ADMIN, UserManager::ROLE_DOCTOR, UserManager::ROLE_PATIENT]);
    }

    public function renderList(): void
    {
        $this->allowedRoles([UserManager::ROLE_ADMIN, UserManager::ROLE_DOCTOR, UserManager::ROLE_PATIENT]);
        
        $this->template->healthProblems = $this->healthProblemService->getForUser($this->user->getId());
        $this->template->examinationWithnoutDoctor = $this->healthProblemService->getExaminationWithoutDoctor($this->user->getId());
    }

    public function createComponentForm()
    {
        $form = new Form();

        $form->addSelect('patient', 'Pacient')
            ->setItems($this->userService->getAllByRole(UserManager::ROLE_PATIENT));

        $form->addText('name', 'Jméno')
            ->addRule(Form::MAX_LENGTH, 'Maximální délka jména je 100 znaků.', 100)
            ->setRequired('Jméno problému je povinné');

        $form->addText('description', 'Popis')
            ->addRule(Form::MAX_LENGTH, 'Maximální délka popisu je 300 znaků.', 100)
            ->setRequired(false);

        $form->addSelect('state', 'Stav')
            ->setItems(HealthProblemService::getStateList());

        $form->addSubmit('submit', 'Uložit');

        $form->onSuccess[] = [$this, 'formSuccess'];

        return $form;
    }

    /**
     * @throws AbortException
     */
    public function actionCreate()
    {
        $this->allowedRoles([UserManager::ROLE_ADMIN, UserManager::ROLE_DOCTOR]);
    }

    /**
     * @param int $healthProblemId
     * @throws AbortException
     */
    public function actionEdit(int $healthProblemId)
    {
        $this->allowedRoles([UserManager::ROLE_ADMIN, UserManager::ROLE_DOCTOR]);

        $this->healthProblemId = $healthProblemId;

        /** @var Form $form */
        $form = $this['form'];
        
        $form->removeComponent($form->getComponent('submit'));
        
        $form->addSelect('doctor', 'Odpovědný lékař')
            ->setItems($this->userService->getAllByRole(UserManager::ROLE_DOCTOR));
        
        $form->addSubmit('submit');

        $form->setDefaults($this->healthProblemService->getDefaults($healthProblemId));
    }

    /**
     * @param Form $form
     * @throws AbortException
     */
    public function formSuccess(Form $form)
    {
        try {
            $doctorId = $this->user->getId();
            $this->healthProblemService->update($this->healthProblemId, $form->getValues(), $doctorId);

            if ($this->healthProblemId !== null) {
                $this->flashMessage('Zdravotní problém byl upraven', 'success');
            } else {
                $this->flashMessage('Zdravotní problém byl vytvořen', 'success');
            }
        } catch (Exception $e) {
            if ($this->healthProblemId !== null) {
                $this->flashMessage('Zdravotní problém se nepodařilo upravit', 'danger');
            } else {
                $this->flashMessage('Zdravotní problém se nepodařilo vytvořit', 'danger');
            }
        }

        $this->redirect('HealthProblem:list');
    }

    /**
     * @param int $healthProblemId
     * @throws AbortException
     */
    public function actionDelete(int $healthProblemId): void
    {
        $this->allowedRoles([UserManager::ROLE_ADMIN, UserManager::ROLE_DOCTOR]);

        try {
            $this->healthProblemService->delete($healthProblemId);

            $this->flashMessage('Zdravotní problém byl smazán', 'success');
        } catch (Exception $e) {
            $this->flashMessage('Zdravotní problém se nepodařilo vymazat', 'danger');
        }

        $this->redirect('HealthProblem:list');
    }
}