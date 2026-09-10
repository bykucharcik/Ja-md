# OmniRoute — kompletný DM funnel pre @kuchar.ai

Celý balík k reelsu o tom, že sa dá kódiť s AI **zadarmo** cez OmniRoute.
Presne ten istý mechanizmus, aký používa Nick Saraev: komentár → ManyChat DM → návod + druhé CTA.

## Čo je v tomto repe

| Súbor | Na čo to je |
| --- | --- |
| `NAVOD/OMNIROUTE_NAVOD_SK.md` | Hlavný návod, ktorý posielaš ľuďom. Kompletný, overený, po slovensky. |
| `NAVOD/omniroute-navod.html` | Tá istá vec ako webová stránka — zdroj pre verejný link do DM. |
| `FUNNEL/MANYCHAT_DM_SEKVENCIA.md` | Hotové texty DM správ. Copy-paste do ManyChatu. |
| `FUNNEL/MANYCHAT_NASTAVENIE.md` | Ako to naklikať v ManyChate krok po kroku. |
| `FUNNEL/REEL_CTA_A_KOMENTARE.md` | CTA do videa, pinned komentár, odpovede pod video. |
| `FUNNEL/FAQ_ODPOVEDE_NA_DM.md` | Odpovede na to, čo ti ľudia napíšu po návode ("mám otázku"). |
| `ZDROJE_A_FAKTY.md` | Čo je overený fakt, čo je marketing projektu, a čo NIKDY netvrdiť. |
| `PDF_STYL/` | Generátor PDF v našom štýle — markdown archív → hotové PDF do kurzu. |

## Poradie, v akom to spustiť

1. Prečítaj `ZDROJE_A_FAKTY.md` — aby si vo videu nepovedal nič, čo neobhájiš.
2. Publikuj návod ako verejný link (HTML verzia) a link si ulož.
3. Naklikaj ManyChat podľa `FUNNEL/MANYCHAT_NASTAVENIE.md`, texty ber z `MANYCHAT_DM_SEKVENCIA.md`.
4. Nahoď reel s CTA z `FUNNEL/REEL_CTA_A_KOMENTARE.md`.
5. Prvý týždeň odpovedaj na DM ručne podľa `FAQ_ODPOVEDE_NA_DM.md` a dopĺňaj otázky, ktoré chodia.

## Dve miesta, kde musíš doplniť svoje veci

V textoch sú dve zástupné hodnoty:

- `https://claude.ai/code/artifact/02988a25-25dc-451f-b5bd-0bc4ea5de0c2` — verejný link na návod
- `{{LINK_CTA2}}` — tvoje druhé CTA (waitlist na kurz alebo AI audit call)

Nájdeš ich cez: `grep -rn "{{LINK" .`
