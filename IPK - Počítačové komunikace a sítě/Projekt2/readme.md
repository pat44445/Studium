Sniffer síťových paketů
=============================
__jméno__: Tomáš Dvořáček  
__login__: xdvora3d

Popis řešení
---------
### Tato implementace analyzátoru síťových paketů podporuje protokoly transportní vrstvy:
1. TCP
2. UDP  

Výstupem analyzátoru je výpis po jednotlivých paketech.  
 

Analyzátor se nejprve musí přeložit příkazem:  
__make__

Poté je možné spuštění příkazem:  
 
__./ipk-sniffer -i rozhraní [-p ­­port] [--tcp|-t] [--udp|-u] [-n num]__  

Kde parametry:  

__-i__ &nbsp; je rozhraní na kterém se bude poslouchat.  
__-p__ &nbsp; je port na kterém se bude poslouchat.  
__--tcp|-t__ &nbsp; budou se analyzovat tcp pakety.  
__--udp|-u__ &nbsp; budou se analyzovat udp pakety.  
__-n__ &nbsp; je počet paketů, které se mají analyzovat.

## Závěr
Projekt je řešen v jazyce __C__, přičemž jsou použity knihovny  jako __libpcap__, __libnet__ a knihovny  
s definicemi struktur (typicky headerů) pro dané síťové protokoly.  
