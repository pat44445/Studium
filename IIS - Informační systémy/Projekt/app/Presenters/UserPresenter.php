<?php

namespace App\Presenters;

use App\Model\HealthProblemService;
use App\Model\UserManager;
use App\Model\UserService;
use Exception;
use Nette\Application\AbortException;
use Nette\Application\UI\Form;
use Nette\Forms\Controls\HiddenField;
use Nette\Forms\Controls\SelectBox;
use Nette\Forms\Controls\TextInput;

class UserPresenter extends LoggedPresenter
{
    /**
     * @var UserService
     * @inject
     */
    public $userService;

    /**
     * @var HealthProblemService
     * @inject
     */
    public $healthProblemService;

    /** @var int|null */
    public $userId;

    public function renderList(): void
    {
        $this->allowedRoles([UserManager::ROLE_ADMIN]);
        
        $this->template->users = $this->userService->getAll();
    }

    public function createComponentCreateForm()
    {
        $form = new Form();

        $form->addHidden('backlink');

        $form->addText('username', 'Uživatelské jméno')
            ->addRule(Form::MAX_LENGTH, 'Maximální délka uživatelského jména je 45 znaků.', 45)
            ->setRequired('Pole uživatelské jméno je povinné');

        $form->addPassword('password', 'Heslo')
            ->setRequired('Pole heslo je povinne');

        $form->addSelect('role', 'Role')
            ->setItems(UserService::roles())
            ->setRequired('Výběr role je povinný');

        $form->addText('fullName', 'Celé jméno')
            ->addRule(Form::MAX_LENGTH, 'Maximální délka jména je 255 znaků', 255);

        $form->addText('date', 'Datum narození')
            ->setHtmlType('date');

        $form->addText('function', 'Funkce')
            ->addRule(Form::MAX_LENGTH, 'Maximální délka funkce je 45 znaků', 45);

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

    public function actionCreatePatient()
    {
        /** @var Form $form */
        $form = $this['createForm'];

        /** @var SelectBox $role */
        $role = $form['role'];
        $role->setItems([UserManager::ROLE_PATIENT => 'Pacient']);

        /** @var TextInput $function */
        $function = $form['function'];
        $function->setDisabled(true);

        /** @var HiddenField $backlink */
        $backlink = $form['backlink'];
        $backlink->setDefaultValue('HealthProblem:create');
    }

    public function actionEdit(int $userId, ?string $backLink = null)
    {
        $this->template->backLink = $backLink;
        $this->userId = $userId;

        /** @var Form $form */
        $form = $this['createForm'];

        $form['password']->setRequired(false);
        $form->setDefaults($this->userService->getDefaults($userId));

        /** @var SelectBox $role */
        $role = $form['role'];
        $form->removeComponent($role);

        /** @var HiddenField $backlink */
        $backlinkInput = $form['backlink'];
        if ($backLink !== null) {
            $backlinkInput->setDefaultValue($backLink);
        }
    }

    /**
     * @param Form $form
     * @throws AbortException
     */
    public function formSuccess(Form $form)
    {
        try {
            $this->userService->update($this->userId, $form->getValues());

            if ($this->userId !== null) {
                $this->flashMessage('Uživatel byl upraven', 'success');
            } else {
                $this->flashMessage('Uživatel byl vytvořen', 'success');
            }

        } catch (Exception $e) {
            if ($this->userId !== null) {
                $this->flashMessage('Uživatele se nepodařilo vytvořit', 'danger');
            } else {
                $this->flashMessage('Uživatele se nepodařilo upravit', 'danger');
            }
        }

        if (!empty($form->getValues()->backlink)) {
            $this->redirect($form->getValues()->backlink);
        }

        $this->redirect('User:list');
    }

    public function createComponentDeleteForm()
    {
        $form = new Form();

        $doctors = $this->userService->getAllByRole(UserManager::ROLE_DOCTOR);
        unset($doctors[$this->userId]);

        $admins = $this->userService->getAllByRole(UserManager::ROLE_ADMIN);

        $form->addSelect('doctor', 'Nový spravující lékař:')
            ->setItems($doctors + $admins);

        $form->onSuccess[] = [$this, 'deleteFormSuccess'];

        $form->addSubmit('submit', 'Odstranit');

        $form->onSuccess[] = [$this, 'formSuccess'];

        return $form;
    }

    public function deleteFormSuccess(Form $form)
    {
        $this->userService->deleteDoctor($this->userId, $form->getValues()->doctor);
        try {

            $this->flashMessage('Lékař byl odstraněn', 'success');
        } catch (Exception $e) {
            $this->flashMessage('Lékaře se nepodařilo odstranit', 'danger');
        }

        $this->redirect('User:list');
    }

    /**
     * @param int $userId
     * @throws AbortException
     */
    public function actionDelete(int $userId): void
    {
        $this->allowedRoles([UserManager::ROLE_ADMIN]);

        $user = $this->userService->get($userId);

        if ($user->role !== UserManager::ROLE_DOCTOR) {
            try {
                $this->userService->delete($userId);

                $this->flashMessage('Uživatel byl smazán', 'success');
            } catch (Exception $e) {
                $this->flashMessage('Uživatele se nepodařilo vymazat', 'danger');
            }

            $this->redirect('User:list');
        } else {
            $this->userId = $userId;

            $this->template->userToDelete = $this->userService->get($userId);
            $this->template->healthProblems = $this->healthProblemService->getForUser($userId);
        }
    }

    public function renderProfile()
    {
        $this->template->currentUser = $this->userService->get($this->user->getId());
    }

    public function actionActive(int $userId)
    {
        try {
            $this->userService->flipState($userId);

            $this->flashMessage('Stav uživatele byl změněn', 'success');
        } catch (Exception $e) {
            $this->flashMessage('Stav uživatele se nepodařilo změnit', 'danger');
        }

        $this->redirect('User:list');
    }
}