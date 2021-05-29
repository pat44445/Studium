HTTP resolver doménových jmen 
=============================
__jméno__: Tomáš Dvořáček  
__login__: xdvora3d

Popis řešení
---------
### Tato implementace serveru reaguje na dotazy:
1. GET /resolve
2. POST /dns-query  

__Pro verzi HTTP/1.1__

Pokud je zadán jiný typ dotazu, server odpoví hlavičkou __405 Method Not Allowed__  
 
Řádek odpovědi pro metodu GET má tvar:  
__DOTAZ:TYP=ODPOVED__

Řádek pro metodu POST obsahuje v těle seznam dotazů, každý na samostatném řádku:  
__DOTAZ:TYP__ (výstupem je seznam odpovědí)  

Kontroluje se formální správnost dotazu, verze HTTP a platnost IPv4 adresy.  
Jestliže něco z toho neodpovídá, server odpoví hlavičkou __400 Bad Request__  

server se spuští příkazem:  
 
__make run PORT=__<číslo portu>  

## Závěr
Projekt je řešen v jazyce Python3, přičemž server je naprogramován pomocí knihovny __socket__.  
Zpracování URL dotazů je pomocí knihovny __urllib__. Pokud je řádek pro danou metodu správný, pak  
server pošle http hlavičku __200 OK__ s odpovědí a poté se spojení ukončí.
