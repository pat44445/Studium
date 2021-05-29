<?php

declare(strict_types=1);

namespace App\Presenters;


final class HomepagePresenter extends LoggedPresenter
{
	public function renderDefault(): void
	{
		$this->template->anyVariable = 'any value';
	}
}
