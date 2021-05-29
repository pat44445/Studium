Feature: Odhlášení uživatele
	Uživatel se chce odhlásit.
	
	Scenario: Odhlášení uživatele
		Given Uživatel je přihlášen.
		When Uživatel klikne na tlačítko "Logout"
		Then Zobrazí se stránka "Account Logout" And Uživatel byl odhlášen.
