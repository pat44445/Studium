<?php

declare(strict_types=1);

namespace App\Forms;

use Nette;
use Nette\Application\UI\Form;
use Nette\Security\User;


final class SignInFormFactory
{
	use Nette\SmartObject;

	/** @var User */
	private $user;


	public function __construct(User $user)
	{
		$this->user = $user;
	}


	public function create(callable $onSuccess): Form
	{
		$form = new Form();
		$form->addText('username', 'Uživatelské jméno:')
			->setRequired('Zadejte své uživatelské jméno.');

		$form->addPassword('password', 'Heslo:')
			->setRequired('Prosím zadejte své heslo.');

		$form->addCheckbox('remember', ' Zůstat přihlášen');

		$form->addSubmit('send', 'Přihlásit se')
			->setHtmlAttribute('class', 'submit');
		

		$form->onSuccess[] = function (Form $form, \stdClass $values) use ($onSuccess): void {
			try {
				$this->user->setExpiration($values->remember ? '14 days' : '20 minutes');
				$this->user->login($values->username, $values->password);
			} catch (Nette\Security\AuthenticationException $e) {
				$form->addError('Zadané uživatelské jméno nebo heslo je nesprávné.');
				return;
			}
			$onSuccess();
		};

		return $form;
	}
}
