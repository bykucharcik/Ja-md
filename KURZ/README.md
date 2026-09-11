# Kurz kuchar.ai

Kompletný kurz v šiestich moduloch. Každá lekcia je samostatné PDF v tvojom
štýle — titulná strana s gradientom, vnútorné strany s krokmi, tabuľkami
a checklistom.

**Texty sú zdroj. PDF je výstup.** Keď chceš niečo zmeniť, upravuješ `.txt`
súbor v `obsah/` a spustíš generátor. PDF ani HTML nikdy neupravuj ručne —
prepíšu sa.

## Čo je kde

| Priečinok | Čo v ňom je |
| --- | --- |
| `obsah/` | Text lekcií. **Toto upravuješ.** Jeden súbor = jedna lekcia. |
| `pdf/` | Hotové PDF po lekciách. Generované. |
| `KURZ-CELY.pdf` | Celý kurz v jednom súbore, s obsahom na preklikanie. Generované. |
| `html/` | Tie isté lekcie ako webová stránka. Generované. |
| `build/` | Generátor (`generuj.py`), zlučovač (`kniha.py`) a štýl (`styl.css`). |
| `fonts/` | Písmo Inter. Nemaž — bez neho sa PDF vysádže náhradným písmom. |

## Ako to pregenerovať

```bash
python3 KURZ/build/generuj.py            # všetky lekcie
python3 KURZ/build/generuj.py 02-03      # len lekcie s "02-03" v názve
python3 KURZ/build/generuj.py --bez-pdf  # len HTML, rýchla kontrola v prehliadači
```

Potrebuješ Python 3 a Playwright s Chromiom:

```bash
pip install playwright && playwright install chromium
```

Generátor sám upozorní na dve veci:

- `strana X pretiekla` — na stranu sa text nezmestil a orezal by sa. Skráť ho.
- `má naviac h3` — vnútorná strana má len dva riadky nadpisu (titulná tri).
- `nedoplnené {{...}}` — v texte je zástupná hodnota, ktorú treba nahradiť.

## Obsah kurzu

20 lekcií v štyroch otvorených moduloch.

| Modul | Lekcie |
| --- | --- |
| 01 Start Here | Start Here |
| 02 Claude | Na čo je celý Claude · Claude v prehliadači · Claude Code · Claude Cowork · Claude Design · **Ako si postaviť agenta** · Modely a čísla · Ako sa Clauda pýtať · Claude Code cez OmniRoute |
| 03 ChatGPT | Na čo je celý ChatGPT · Modely a čísla · **GPT-6 Astra** · Ako sa ChatGPT pýtať · Projects a Custom GPTs · ChatGPT vs Claude |
| 04 Claude Skills | Čo je skill a na čo slúži · Ako si skill vytvoriť · Poriadok v skills · Ako skills nainštalovať a spustiť |

### Zamknuté moduly

Moduly **05 Checklisty** a **06 Šablóny** sú hotové, ale zatiaľ mimo kurzu.
Ich texty čakajú v `obsah/zamknute/`. Keď ich budeš chcieť otvoriť, presuň
súbory späť do `obsah/` a pregeneruj — nič iné netreba.

**Chýba:** lekcia `Katalóg packu (36 skills)`. Potrebuje skutočné názvy tvojich
skills — pošli zoznam alebo priečinok `SKILLS/` a doplní sa.

## Formát súboru s lekciou

Hore je hlavička `kľúč: hodnota`, pod ňou bloky, ktoré začínajú `@`.
Riadok začínajúci `#` je poznámka a do PDF sa nedostane.

```
modul: 02 Claude
cislo: 02.1
titul: Čo je Claude
stopa: CLAUDE × KUCHAR.AI          # text vpravo hore na každej strane
stitky: Claude | 12 min | Začiatočník

@obal                               # titulná strana, vždy prvá
stitok: ČO JE CLAUDE                # malý text nad nadpisom
h1: Jeden model.                    # tučný riadok
h2: Štyri dvere.                    # svetlý riadok
h3: Nepovinný tretí.
nadstitok: ČO ŤA TÁTO LEKCIA NAUČÍ
hlavne: Veľká veta o tom, čo sa naučíš.
vedlajsie: Menšia veta pod ňou.
karta: HORE | Stred | DOLE          # oranžová karta, môžu byť dve
vysledok: Veta nad pätičkou.
drobne: Drobný text celkom dole — dátum, upozornenie, výhrada.

@strana                             # vnútorná strana, len h1 a h2
stitok: KAM TO DAŤ
h1: Dva priečinky.
h2: Vyber jeden.
```

### Bloky do vnútorných strán

| Blok | Ako sa píše |
| --- | --- |
| `@text` | Odseky. Prázdny riadok = nový odsek. `@text velky` zväčší, `@text drobne` zmenší. |
| `@kroky` | `01 \| ŠTÍTOK \| text` — podfarbené riadky. Štítok sa dá vynechať. |
| `@zoznam` | `01 \| text` — riadky oddelené linkou, bez podfarbenia. |
| `@pojmy` | `ŠTÍTOK \| vysvetlenie`. `@pojmy kod` nechá štítky malými písmenami. |
| `@tabulka Hlavička1 \| Hlavička2` | Riadky pod tým: `bunka \| bunka`. |
| `@terminal NÁZOV` | Kód alebo šablóna. Zachová riadkovanie tak, ako to napíšeš. |
| `@pravidlo ŠTÍTOK` | Zvýraznený odsek so štítkom vľavo. |
| `@checklist` | Jedna položka na riadok, dostane štvorček. |
| `@video ŠTÍTOK` | `Názov videa \| dĺžka \| adresa` — veľká klikateľná oranžová karta. |
| `@odkazy` | `NÁZOV \| https://...` |
| `@zaver` | `hlavne:` a `vedlajsie:` — dve vety na koniec. |

### V texte funguje

- `**tučné**`
- `` `kód` `` — vysádže sa tehlovou farbou
- ` -- ` → pomlčka, ` -> ` → šípka
- `„úvodzovky"` sa samy zatvoria správne
- za jednopísmenovými predložkami sa dopĺňa pevná medzera

## Videá

**Video sa do PDF vložiť nedá.** Technicky to formát umožňuje, ale prehrá sa len
v Adobe Acrobate — v prehliadači, v náhľade na Macu ani v mobile to nikto
neuvidí. Preto video žije na platforme a PDF naň odkazuje blokom `@video`.

```
@video ÚVODNÉ VIDEO
Ako tento kurz použiť | 6 min | https://...
```

Kým adresu nemáš, nechaj tam zástupnú hodnotu v tvare `{{VIDEO_01_01}}`.
Generátor ťa na každú nedoplnenú upozorní pri každom builde, takže sa nestane,
že pošleš PDF s nefunkčným odkazom.

Nájdeš ich aj ručne:

```bash
grep -rn "{{" KURZ/obsah/
```

## Pravidlá obsahu

Rovnaké ako v `ZDROJE_A_FAKTY.md`: hype smie byť v nadpise, fakty musia byť
presné. Kde je údaj pohyblivý (ceny, názvy plánov, dostupnosť modelov), je
v lekcii dátum a odkaz na zdroj. **Keď takú lekciu aktualizuješ, prepíš aj
ten dátum.**
