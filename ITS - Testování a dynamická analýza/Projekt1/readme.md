Úvod:
-----

Tento testovací plán vznikl jako školní projekt do předmětu ITS v
akademickém roce 2019/2020 na Fakultě informačních technologíí VUT v
Brně.

Předmět testování:
------------------

Testovanou aplikací je instance eCommerce platforma OpenCart.

Testované vlastnosti:
---------------------

Testovány budou následující vlastnosti:

-   Registrace uživatele

    -   Ověření, že povinné položky jsou vyžadovány
    -   Platnost zadaných dat (formát e-mailu)

-   Odhlášení uživatele

-   Obnova zapomentutého hesla

-   Nákup produktu

    -   Správa nákupního košíku
    -   Objednávka

-   Správa produktu

    -   Změna popisku
    -   Filtrace produktů
    -   Správa slev

Přístup:
--------

Testování bude probíhat pomocí nástroje Selenium. Bude spuštěna sada
několika testovacích případů, které se automaticky vyhodnotí.

Kritéria selhání/úspěchu:
-------------------------

Celkové hodnocení se odvíjí od jednotlivých testovacích případů.
Kritériem pro úspěch je, že všechny testovací případy budou úspěšné.

Testovací prostředí:
--------------------

Tato instance E-shopu na platformě Opencart je běží na serveru. Název
serveru je *mys01.fit.vutbr.cz*.