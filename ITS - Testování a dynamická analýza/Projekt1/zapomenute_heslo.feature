Feature: Zapomenuté heslo uživatele
	Uživatel zapoměl své heslo a chce si ho obnovit.
	
	Scenario: Obnova hesla
		Given Uživatel je na stránce "Forgot Your Password?".
		When Uživatel zadá svoji E-mailovou adresu
		And klikne na tlačítko continue.
		Then Uživateli byl zaslán E-mail umožňujíci obnovu hesla.