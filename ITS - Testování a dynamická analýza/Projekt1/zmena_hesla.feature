Feature: Změna hesla
	Uživatel si chce změnit heslo.
	
	Scenario: Změna hesla
		Given Uživatel je na stránce "Change password"
		When Uživatel zadal do kolonky "Password" nové heslo
		And do kolonky "Password confirm" jej napsal znovu
		And Hesla se rovnají
		Then Uživatelské heslo bylo změněno.