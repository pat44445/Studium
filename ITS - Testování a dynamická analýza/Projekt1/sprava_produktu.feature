Feature: Správa produktů

	Scenario Administrátor chce vyhledat všechny produkty určité ceny
		Given Administrátor se nachází ve správcovské části v sekci "Catalog", podsekci "Products"
		When Admin zadá požadovanou částku
		And klikne na tlačítko "Filter"
		Then Ukážou se všechny produkty zadané částky.
		
	Scenario Administrátor chce změnit popisek u produktu
		Given Administrátor se nachází ve správcovské části v sekci "Catalog", podsekci "Products" v okně "Edit Product" v části "General"
		When Admin upraví popisek
		And klikne na tlačítko "Save"
		Then U příslušného produktu je nově upravený popisek.
		
	Scenario Administrátor chce nastavit slevu na produkt
		Given Administrátor se nachází ve správcovské části v sekci "Catalog", podsekci "Products" v okně "Edit Product" v části "Discount"
		When Admin nastaví parametry slevové akce
		And klikne na tlačítko "Save"
		Then U příslušného produktu je nastavena sleva.