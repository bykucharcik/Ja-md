# FAQ — čo ti napíšu do DM a čo odpísať

Na obrázku od Nicka vidíš, že hneď po návode prišlo „I have a question". Presne to sa stane aj tebe.
Toto je pripravená zásoba odpovedí, aby si nepísal každú od nuly — ale **prepíš si ich vlastnými slovami**, ľudia cítia copy-paste.

---

## Technické

**„Nefunguje mi to / hádže to chybu"**
> Pošli screenshot celej chyby. Najčastejšie je to Node.js — napíš mi, čo ti vypíše `node --version`. Potrebuješ 24-ku, na starších to padá na bielu stránku.

**„Hádže mi to 401"**
> Klasika. Claude Code chce base URL **bez** `/v1` na konci — teda `http://localhost:20128`. Ostatné nástroje ho naopak chcú. A po zmene musíš Claude Code reštartovať, premenné sa čítajú len pri štarte.

**„Hádže mi to 429"**
> To znamená, že free kvóta providera je vyčerpaná. Buď počkaj minútu, alebo — a to je lepšie riešenie — pripoj si ďalších providerov. S jedným narazíš na limit rýchlo, s tromi ťa fallback prepne a ani si to nevšimneš.

**„Musím to mať stále zapnuté?"**
> Áno, je to server, ktorý beží u teba. Keď ho vypneš, nástroje sa nemajú kam pripojiť. Dá sa to hodiť do Dockera alebo na VPS a mať to stále.

**„Ide to na Windowse / Macu / Linuxe?"**
> Všade. Je to npm balík. Existuje aj Docker, desktop appka a beží to aj na Androide cez Termux.

**„Ako viem, koľko mi ešte zostáva?"**
> V dashboarde na `/dashboard/free-tiers` máš živý stav — koľko z každej kvóty si minul a koľko zostáva.

---

## Nedôvera

**„Naozaj je to zadarmo?"**
> Áno, appka je open-source pod MIT. Zadarmo sú aj kvóty providerov, ktoré cez ňu využívaš. Čo ti negarantujem je, že to tak zostane navždy — free tiery sa menia oboma smermi, dnes ich provider pridá, zajtra zruší.

**„Kde je háčik?"**
> Že tvoje prompty idú cez servery providerov, ktorých free tier používaš. Nie každý garantuje, že to nepoužije na tréning. Na učenie a vlastné projekty úplne v pohode. Na klientsky kód a firemné dáta nie — tam si nechaj platený model.

**„Nie je to nebezpečné?"**
> Samotná appka beží u teba lokálne, kľúče má šifrované na disku a telemetriu vypnutú. Riziko nie je v nej, ale v tom, cez ktorých providerov púšťaš dáta. Preto o tom píšem aj v návode.

**„Prečo mi to dávaš zadarmo, čo z toho máš?"**
> Nič priamo, toto nie je môj projekt. Robím obsah o AI nástrojoch a takéto veci ma bavia. Keď ťa neskôr bude zaujímať niečo väčšie, uvidíš to u mňa v profile.

---

## Kvalifikačné (toto sú tvoje peniaze)

**Keď človek napíše, že má biznis / e-shop:**
> Pekné. Na čom to máš postavené a čo ti dnes berie najviac ručnej roboty? Väčšinou sa dá presne to odpáliť do AI a viem ti povedať, či sa to u teba oplatí alebo nie.

Odtiaľ ideš: pain → približný obrat → či to už riešili → call.

**Keď píše, že sa učí:**
> V pohode, začni tým návodom a rozbehni si na tom jeden vlastný projekt. Až to pobeží, napíš mi, čo si postavil — zaujíma ma to.

Tento človek nie je lead dnes. Je to lead o pol roka a bude si pamätať, že si mu odpísal.

**Keď sa pýta na cenu / spoluprácu:**
> Záleží, čo riešiš. Napíš mi v skratke firmu, čo robíte a kde vás to najviac tlačí, a poviem ti rovno, či to viem posunúť alebo nie.

---

## Čo nikdy nepíš

- „Je to úplne zadarmo navždy" — nie je, a keď to prestane platiť, si klamár.
- „Nahradí ti to platený Claude" — nenahradí, kvalitou modelov ani limitmi.
- Vymyslené čísla úspor. Ak nemáš vlastné meranie, nehovor percentá.
- Dlhé odseky. V DM funguje 2–3 riadky a otázka na konci.
