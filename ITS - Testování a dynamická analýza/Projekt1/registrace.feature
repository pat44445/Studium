Feature: Registrace uživatele
	Uživatel si chce vytvořit nový účet.
	
		Background:
			Given Uživatel má před sebou stránku s registračním formulářem.
			
		Scenario: Neplatná E-mailová adresa
			When Uživatel zadá do kolonky E-mail neplatnou adresu 
			And klikne na tlačítko continue.
			Then Ukáže se zpráva "Zadejte prosím platnou e-mailovou adresu"
			
		Scenario: Platná, ale obsazená E-mailová adresa
			When Uživatel zadá do kolonky E-mail platnou, ale již obsazenou E-mailovu adresu
			And klikne na tlačítko continue.
			Then Ukáže se zpráva "Warning: E-Mail Address is already registered!"
			
		Scenario: Nevyplnění povinnké kolonky
			When Uživatel nevyplnil kolonku s povinnými údaji
			And klikne na tlačítko continue.
			Then Ukáže se varovná zpráva
			
		Scenario: Neakceptování Privacy Policy
			When Uživatel vyplnil všechny povinné kolonky 
			But nedal souhlas s přijmutím "Privacy Policy"
			And klikne na tlačítko continue.
			Then Ukáže se zpráva "Warning: You must agree to the Privacy Policy!"
			
		Scenario: Úspěch registrace
			When Uživatel vyplnil všechny povinné kolonky
			And klikne na tlačítko continue.
			Then Ukáže se stránka se zprávou "Your Account Has Been Created!" And Byl vytvořen nový účet.
			
			
			
			