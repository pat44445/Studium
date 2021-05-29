<?php

declare(strict_types=1);

namespace App\Router;

use Nette;
use Nette\Application\Routers\RouteList;


final class RouterFactory
{
	use Nette\StaticClass;

	public static function createRouter(): RouteList
	{
		$router = new RouteList;

		$router->addRoute('sign/in', 'Sign:in');

		$router->addRoute('users/list', 'User:list');
		$router->addRoute('users/delete/<userId>', 'User:delete');
		$router->addRoute('users/create', 'User:create');
		$router->addRoute('users/create-patient', 'User:createPatient');
		$router->addRoute('users/edit/<userId>', 'User:edit');
		$router->addRoute('users/active/<userId>', 'User:active');

		$router->addRoute('/health-problems/list', 'HealthProblem:list');

		$router->addRoute('/reports/<healthProblemId>/list', 'Report:list');
		$router->addRoute('/reports/<healthProblemId>/create', 'Report:create');
        $router->addRoute('/reports/<healthProblemId>/edit/<reportId>', 'Report:edit');
        $router->addRoute('/reports/<healthProblemId>/delete/<reportId>', 'Report:delete');
		$router->addRoute('/reports/<healthProblemId>/detail/<reportId>', 'Report:detail');
		$router->addRoute('/reports/image/<reportId>', 'Report:image');

		$router->addRoute('/reports/create-for-examination/<examinationId>', 'Report:createForExamination');

        $router->addRoute('/examinations/<healthProblemId>/list', 'Examination:list');
        $router->addRoute('/examinations/<healthProblemId>/create', 'Examination:create');
        $router->addRoute('/examinations/<healthProblemId>/edit/<examinationId>', 'Examination:edit');
        $router->addRoute('/examinations/<healthProblemId>/delete/<examinationId>', 'Examination:delete');

        $router->addRoute('/examinations/<examinationId>/reports/create', 'Report:createExamination');
        $router->addRoute('/examinations/<examinationId>/reports/<reportId>/edit/', 'Report:editExamination');
        $router->addRoute('/examinations/<examinationId>/reports/<reportId>/delete/', 'Report:deleteExamination');
        $router->addRoute('/examinations/<examinationId>/reports/<reportId>/detail/', 'Report:detailExamination');

        $router->addRoute('/examinations/my', 'Examination:my');
        $router->addRoute('/examinations/<examinationId>/detail/', 'Examination:detail');
        $router->addRoute('/examinations/<examinationId>/state-change/<state>', 'Examination:stateChange');

        $router->addRoute('/procedure-request/list', 'ProcedureRequest:list');
        $router->addRoute('/procedure-request/<procedureRequestId>/changeState/<state>', 'ProcedureRequest:list');
        $router->addRoute('/examinations/<examinationId>/procedure-request/create', 'ProcedureRequest:create');
        $router->addRoute('/examinations/<examinationId>/procedure-request/delete/<procedureRequestId>', 'ProcedureRequest:delete');

        $router->addRoute('procedures/list', 'Procedure:list');
        $router->addRoute('procedures/delete/<procedureId>', 'Procedure:delete');
        $router->addRoute('procedures/create', 'Procedure:create');
        $router->addRoute('procedures/edit/<procedureId>', 'Procedure:edit');

		$router->addRoute('<presenter>/<action>', 'Homepage:default');
		return $router;
	}
}
