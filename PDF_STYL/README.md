# PDF štýl kurzu — generátor

Prerobí ktorýkoľvek markdown archív na PDF v našom štýle (`Kuchar_AI_Student_Kit.pdf`):
tmavá navy plocha s technickým gridom, modrý akcent, zaoblené karty, mono popisky,
hlavička `@kuchar.ai` a pätka s číslovaním na každej strane.

Postavené na AI študijnom archíve (`AI_STUDIJNY_ARCHIV`), ale funguje na akomkoľvek
priečinku s rovnakou štruktúrou.

## Čo v tomto priečinku je

| Súbor | Na čo to je |
| --- | --- |
| `build_pdf.py` | Generátor. Markdown → HTML v našom štýle → PDF cez Chromium. |
| `style/kurz.css` | Dizajn systém pre print. Farby, typografia, komponenty. |
| `style/pozadie.html` | Podkladová vrstva — plnoplošné tmavé pozadie s gridom. |
| `style/fonts.css` + `style/fonts/` | IBM Plex Sans / Mono, latin + latin-ext (slovenská diakritika). |

## Spustenie

```bash
pip install markdown playwright pypdf
python3 build_pdf.py --archive /cesta/k/AI_STUDIJNY_ARCHIV
```

Prepínače:

- `--only 04_TIPY_A_TRIKY` — len časť archívu (filtruje podľa cesty)
- `--limit 3` — len prvých N dokumentov, na rýchly náhľad
- `--keep-html` — uloží aj HTML vedľa PDF, keď ladíš štýl
- `--chrome /cesta/k/chrome` — keď si Chromium nenájde sám

## Čo generuje

- pre každý modul `03_STUDIJNE_POZNAMKY_SK.md` → `PDF/<nazov_modulu>.pdf`
- pre samostatné dokumenty (`INDEX.md`, `TABULKA.md`, …) → PDF vedľa zdroja
- `00_OBSAH_ARCHIVU.pdf` — obsah celého archívu, sekcia po sekcii

Pôvodné prílohy zo zdroja (priečinky `PRILOHY/`) sa nikdy neprepisujú.

## Ako sa markdown mapuje na dizajn

| V zdroji | Vo výstupe |
| --- | --- |
| `# Nadpis` | veľký titulok na obálke; časť za `:` alebo `—` sa vysádza tenkým rezom |
| prvý odstavec pod ním | lede pod titulkom |
| `## Odkiaľ to je` | zvýraznená modrá karta so zdrojom (kurz, lekcia, URL) |
| `## Ako čítať túto lekciu`, `## Čo v zdroji nie je` | callouty na konci dokumentu |
| ostatné `##` | sekcia s modrým kickerom (mapovanie je v `KICKERS`) |
| ` ```kód``` ` | tmavý blok s popiskom jazyka |
| tabuľky | zaoblená karta s hlavičkovým pásom |
| `---` hlavička v SKILL.md | karta „Hlavička skillu“ |
| veta o chýbajúcej informácii | prerušovaný chip, aby bolo na prvý pohľad vidieť medzeru v zdroji |

Navyše sa cestou opravuje rozsypaná diakritika (`â€™` → `’`) a vyhadzujú sa vzdialené
obrázky zo Skoolu a Drive, ktoré sa do PDF aj tak nenačítajú — ich odkaz v texte ostáva.

## Prečo je pozadie zvláštne riešené

Chromium pri tlači do PDF nikdy nevykreslí pozadie do okrajov strany — ostal by biely
rám. Preto sa `style/pozadie.html` vyrenderuje zvlášť ako plnoplošná A4 strana a cez
`pypdf` sa podloží pod každú stranu obsahu. Hlavička a pätka idú cez Chromium šablóny,
takže majú k dispozícii číslo strany a celkový počet.
