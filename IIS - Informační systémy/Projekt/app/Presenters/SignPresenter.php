<?php

declare(strict_types=1);

namespace App\Presenters;

use App\Forms;
use Nette\Application\UI\Form;
use Nette;


final class SignPresenter extends Nette\Application\UI\Presenter
{
	/** @persistent */
	public $backlink = '';

	/** @var Forms\SignInFormFactory */
	private $signInFactory;


	public function __construct(Forms\SignInFormFactory $signInFactory)
	{
		$this->signInFactory = $signInFactory;
	}


	/**
	 * Sign-in form factory.
	 */
	protected function createComponentSignInForm(): Form
	{
		return $this->signInFactory->create(function (): void {
			$this->restoreRequest($this->backlink);
			$this->redirect('Homepage:');
		});
	}

	public function actionOut(): void
	{
		$this->getUser()->logout();
	}
}
