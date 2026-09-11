# Kurz AI DO PRAXE

Kompletný kurz. Každá lekcia je samostatné PDF — titulná strana s gradientom,
vnútorné strany s krokmi, tabuľkami, boxami a checklistom. Na začiatku sú dve
strany s plánom kurzu, ktoré sa generujú samy z lekcií.

**Texty sú zdroj. PDF je výstup.** Keď chceš niečo zmeniť, upravuješ `.txt`
súbor v `obsah/` a spustíš generátor. PDF ani HTML nikdy neupravuj ručne —
pri ďalšom builde sa prepíšu.

## Čo je kde

| Priečinok | Čo v ňom je |
| --- | --- |
| `obsah/` | Text lekcií. **Toto upravuješ.** Jeden súbor = jedna lekcia. |
| `obsah/zamknute/` | Lekcie mimo tohto vydania. Negenerujú sa. |
| `pdf/` | Hotové PDF po lekciách. Generované. |
| `KURZ-CELY.pdf` | Celý kurz v jednom súbore, s obsahom na preklikanie. Generované. |
| `html/` | Tie isté lekcie ako webová stránka. Generované. |
| `build/` | Generátor (`generuj.py`), zlučovač (`kniha.py`) a štýl (`styl.css`). |
| `fonts/` | Písmo Inter. Nemaž — bez neho sa PDF vysádže náhradným písmom. |

## Ako to pregenerovať

```bash
python3 KURZ/build/generuj.py            # všetko vrátane plánu a KURZ-CELY.pdf
python3 KURZ/build/generuj.py 03-02      # len lekcie s "03-02" v názve
python3 KURZ/build/generuj.py --bez-pdf  # len HTML, rýchla kontrola v prehliadači
```

Potrebuješ Python 3, Playwright s Chromiom a pymupdf:

```bash
pip install playwright pymupdf && playwright install chromium
```

Generátor sám upozorní na dve veci:

- `blok N pretiekol o ~X px` — na stranu N sa text nezmestil a orezal by sa.
  Skráť ho, alebo stranu rozdeľ na dve.
- `nedoplnené {{...}}` — v texte je zástupná hodnota, ktorú treba nahradiť.

Čísla strán bežia priebežne cez celý kurz, takže po pridaní lekcie **vždy
pregeneruj všetko**, nie len tú jednu. Inak sa rozídu čísla v pláne aj v pätičkách.

## Obsah kurzu

25 lekcií v štyroch otvorených moduloch.

| Modul | Lekcie |
| --- | --- |
| 01 Štart | Začni tu |
| 02 Claude | Ktorého Clauda otvoriť · Nauč Clauda, kto si · Projects: Claudov pracovný stôl · Claude v Chrome · Claude Code: prvý štart · Cowork: deleguj prvú úlohu · Claude Design · Vlastný AI agent · Modely, cena a limity · Prompt, ktorý sa dá použiť · OmniRoute (voliteľná) |
| 03 ChatGPT | Čo dnes vie ChatGPT · Nauč ChatGPT, kto si · Šesť režimov · Konektory a naplánované úlohy · Model a uvažovanie · GPT-6 Astra v praxi · Zadávaj presne · Projects a vlastné GPT · ChatGPT alebo Claude? |
| 04 Skills | Čo je skill · Vytvor svoj prvý skill · Poriadok v skills · Nainštaluj, spusti a over skill |

### Zamknuté moduly

Moduly **05 Checklisty** a **06 Šablóny** sú hotové, ale zatiaľ mimo kurzu.
Ich texty čakajú v `obsah/zamknute/`. Keď ich budeš chcieť otvoriť, presuň
súbory späť do `obsah/` a pregeneruj — nič iné netreba. Pozor: sú písané
v staršom formáte, pred otvorením ich treba prepísať podľa tohto návodu.

## Formát súboru s lekciou

Hore je hlavička `kľúč: hodnota`, pod ňou bloky, ktoré začínajú `@`.
Riadok začínajúci `#` je poznámka a do PDF sa nedostane.

```
modul: 03 ChatGPT            # názov modulu, podľa neho sa radí obsah
cislo: 03.2                  # číslo lekcie
titul: Nauč ChatGPT, kto si  # názov v pätičke a v obsahu
varianta: b                  # vzhľad titulnej strany: a, b, c alebo d

@obal                        # titulná strana, vždy prvá
cislo: 03.2
stitok: NAUČ CHATGPT, KTO SI      # malý text nad nadpisom
h1: Každé ráno sa zobudí a nevie o tebe nič.
slub: Nastavíš vlastné inštrukcie a zapneš pamäť.
cas: 5 min | ČÍTANIE              # dva riadky cas: vedľa seba
cas: 20–25 min | PRAX
priprav: ChatGPT účet a 10 minút.
bod: Inštrukcie verzus pamäť      # tri riadky bod:, očíslujú sa samy
bod: Rozhovor, ktorý to vyplní
bod: Upratanie zlých spomienok

@strana                      # vnútorná strana
stitok: POSTUP
h1: Nadpis strany.
```

**Štyri varianty titulnej strany** (`varianta: a` až `d`) menia rozloženie
gradientu a umiestnenie čísla. Farby a vzhľad sú vždy rovnaké. Strieda ich,
aby po sebe nešli dve rovnaké.

### Bloky do vnútorných strán

| Blok | Ako sa píše |
| --- | --- |
| `@text` | Odseky. Prázdny riadok = nový odsek. `@text drobne` zmenší. |
| `@kroky` | `01 \| Nadpis kroku \| text` — veľké tehlové číslo vľavo. |
| `@box ŠTÍTOK` | Podfarbený box so štítkom. Najpoužívanejší blok. |
| `@kod ŠTÍTOK` | Prompt, príkaz alebo šablóna. **Zachová riadkovanie a nič v ňom neupravuje** — žiadne úvodzovky, šípky ani pevné medzery. |
| `@tabulka H1 \| H2 \| H3` | Riadky pod tým: `bunka \| bunka \| bunka`. |
| `@pojmy` | `ŠTÍTOK \| vysvetlenie`. `@pojmy kod` nechá štítky malými písmenami. |
| `@checklist` | Jedna položka na riadok, dostane štvorček. |
| `@terazty TERAZ TY` | Tehlový blok na koniec lekcie. CTA a odkaz na ďalšiu lekciu. |
| `@zdroje ŠTÍTOK` | `NÁZOV \| https://...` — riadok odkazov na spodku strany. |
| `@video ŠTÍTOK` | `Názov \| dĺžka \| adresa` — veľká klikateľná karta. |

### V texte funguje

- `**tučné**`
- `` `kód` `` — vysádže sa tehlovou farbou
- ` -- ` → pomlčka, ` -> ` → šípka (obklopená medzerami, inak sa nepremení)
- `„úvodzovky"` — otvor `„`, zavri obyčajným `"`, generátor doplní `“`
- za jednopísmenovými predložkami sa dopĺňa pevná medzera

## Ako má vyzerať dobrá lekcia

- Titulná strana, dve až štyri strany postupu, posledná strana s kontrolou.
- Aspoň jedna strana má `@kroky`. Bez číslovaného postupu to nie je lekcia.
- Posledná strana má `@checklist`, `@terazty` a `@zdroje`.
- V checkliste sú **overiteľné** body („súčet vyšiel 130 EUR"), nie pocitové
  („rozumiem tomu").
- Každá lekcia má aspoň jeden `@box PRE POKROČILÝCH`.
- `h1` na obale je hook — konkrétny problém, nie opis témy. A nesmie sľúbiť
  viac, než lekcia dodá.
- `@terazty` odkazuje na nasledujúcu lekciu, žiadnu nepreskakuje.

## Kontrola pred odovzdaním

V repozitári je agent `kontrola-kurzu` (`.claude/agents/kontrola-kurzu.md`).
Prejde všetky lekcie a nahlási chyby v jazyku, copywritingu, faktoch
a štruktúre. Nič neopravuje — len nahlási a dá verdikt.

Spustíš ho v Claude Code na tomto priečinku. Overuj jeho nálezy: pri faktoch
vie prehliadnuť zdroj, ktorý je v inom súbore dokumentácie než v README.

## Pravidlá obsahu

Rovnaké ako v `ZDROJE_A_FAKTY.md`: hype smie byť v nadpise, fakty musia byť
presné. Kde je údaj pohyblivý (ceny, názvy plánov, dostupnosť modelov), je
v lekcii dátum a odkaz na zdroj. **Keď takú lekciu aktualizuješ, prepíš aj
ten dátum.**
