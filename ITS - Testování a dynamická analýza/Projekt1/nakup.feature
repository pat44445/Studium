Feature: Zakoupení produktu
	Uživatel si chce koupit produkt
	
	Scenario: Přidání produktu do košíku
		Given Uživatel je na stránce s nabídkou produktů.
		When Uživatel klikne na tlačítko "ADD TO CART"
		Then Příslušný produkt byl přidán do košíku.
		
	Scenario: Zobrazení nákupního košíku
		Given Uživatel je na jakékoliv stránce E-shopu
		When Uživatel klikne na velké černé tlačítko v pravé horní části
		And klikne na tlačítko "View Cart"
		And v košíku se nachází alespoň 1 produkt
		Then Zobrazí se obsah nákupního košíku.
		
	Scenario: Odebrání produktu z košíku
		Given Uživatel je na stránce "Shopping Cart".
		When Uživatel klikne u příslušného produktu na červené tlačítko "Remove"
		Then Příslušný produkt byl odebrán z košíku.
			
	Scenario: Dokončení objednávky
		Given Uživatel je na stránce "Shopping Cart".
		When Uživatel klikne na tlačítko "Checkout"
		And Vyplní sekci "Billing details"
		And Vyplní sekci "Payment method"
		And Klikne na tlačítko "Confirm Order"
		Then Zobrazí se zpráva "Your order has been placed!"