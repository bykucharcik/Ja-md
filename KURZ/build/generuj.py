#!/usr/bin/env python3
"""
Generátor kurzu AI DO PRAXE
===========================

Číta lekcie z KURZ/obsah/*.txt, vyrobí z nich HTML (KURZ/html/)
a z HTML vytlačí PDF cez Chromium (KURZ/pdf/). Na konci zlepí všetko
do KURZ/KURZ-CELY.pdf.

    python3 KURZ/build/generuj.py            # všetko
    python3 KURZ/build/generuj.py 02-01      # len lekcie, ktorých názov obsahuje "02-01"
    python3 KURZ/build/generuj.py --bez-pdf  # len HTML, PDF preskočí

Formát obsahu je opísaný v KURZ/README.md.
"""

import html as html_mod
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

KOREN = Path(__file__).resolve().parent.parent
OBSAH = KOREN / "obsah"
VYSTUP_HTML = KOREN / "html"
VYSTUP_PDF = KOREN / "pdf"

ZNACKA = "AI DO PRAXE"
AUTOR  = "Tomáš Kucharčík — kuchar.ai"


# ----------------------------------------------------------------- parser

def rozdel_lekciu(text):
    """Rozdelí súbor lekcie na hlavičku (meta) a zoznam blokov."""
    meta, bloky, aktualny = {}, [], None

    for surovy in text.splitlines():
        riadok = surovy.rstrip()

        if riadok.startswith("@"):
            if aktualny:
                bloky.append(aktualny)
            druh, _, argument = riadok[1:].strip().partition(" ")
            aktualny = {"druh": druh.strip(), "argument": argument.strip(), "riadky": []}
            continue

        if aktualny is None:
            if riadok.strip().startswith("#") or not riadok.strip():
                continue
            kluc, oddelovac, hodnota = riadok.partition(":")
            if oddelovac:
                meta[kluc.strip()] = hodnota.strip()
            continue

        aktualny["riadky"].append(riadok)

    if aktualny:
        bloky.append(aktualny)

    for blok in bloky:
        while blok["riadky"] and not blok["riadky"][-1].strip():
            blok["riadky"].pop()

    return meta, bloky


def polia(blok):
    """Riadky typu 'kluc: hodnota' prevedie na slovník (viacnásobné kľúče do zoznamu)."""
    vysledok = {}
    for riadok in blok["riadky"]:
        if not riadok.strip():
            continue
        kluc, oddelovac, hodnota = riadok.partition(":")
        if not oddelovac:
            continue
        kluc, hodnota = kluc.strip(), hodnota.strip()
        if kluc in vysledok:
            if not isinstance(vysledok[kluc], list):
                vysledok[kluc] = [vysledok[kluc]]
            vysledok[kluc].append(hodnota)
        else:
            vysledok[kluc] = hodnota
    return vysledok


def zoznam(hodnota):
    if hodnota is None:
        return []
    return hodnota if isinstance(hodnota, list) else [hodnota]


# ----------------------------------------------------------------- text

VZOR_TUCNE = re.compile(r"\*\*(.+?)\*\*")
VZOR_KOD = re.compile(r"`(.+?)`")
# jednopísmenové predložky a spojky sa v slovenčine nenechávajú na konci riadku
VZOR_PREDLOZKA = re.compile(r"(^|[\s(„])([aiouvszkAIOUVSZK])\s+")
VZOR_UVODZOVKY = re.compile(r"„([^„”“]*?)\"")

SIPKA_VPRAVO = (
    '<svg class="sipka sipka--vpravo" viewBox="0 0 12 10" aria-hidden="true">'
    '<path d="M1 5 L11 5 M7.4 1.4 L11 5 L7.4 8.6" fill="none" '
    'stroke="currentColor" stroke-width="1.3" stroke-linecap="square"/></svg>'
)
SIPKA = (
    '<svg class="sipka" viewBox="0 0 10 10" aria-hidden="true">'
    '<path d="M2 8 L8 2 M3.4 2 L8 2 L8 6.6" fill="none" '
    'stroke="currentColor" stroke-width="1.4" stroke-linecap="square"/></svg>'
)


def t(surovy):
    """Escapne HTML a povolí **tučné**, `kód`, šípku " -> " a pomlčku " -- ".

    Navyše dorába slovenskú typografiu: pevná medzera za jednopísmenovými
    predložkami a správne zatvorené úvodzovky.
    """
    text = surovy or ""
    for _ in range(2):  # dva prechody kvôli prekrývajúcim sa zhodám
        text = VZOR_PREDLOZKA.sub("\\1\\2 ", text)
    bezpecny = html_mod.escape(text, quote=False)
    bezpecny = VZOR_TUCNE.sub(r"<strong>\1</strong>", bezpecny)
    bezpecny = VZOR_KOD.sub(r"<code>\1</code>", bezpecny)
    bezpecny = bezpecny.replace(" -&gt; ", f" {SIPKA_VPRAVO} ").replace(" -- ", " — ")
    bezpecny = VZOR_UVODZOVKY.sub("„\\1“", bezpecny)
    return bezpecny


def rozsek(riadok, pocet=None):
    casti = [c.strip() for c in riadok.split("|")]
    if pocet is not None:
        while len(casti) < pocet:
            casti.append("")
    return casti


def odseky(riadky):
    """Zlúči riadky na odseky oddelené prázdnym riadkom."""
    von, aktualny = [], []
    for riadok in riadky:
        if riadok.strip():
            aktualny.append(riadok.strip())
        elif aktualny:
            von.append(" ".join(aktualny))
            aktualny = []
    if aktualny:
        von.append(" ".join(aktualny))
    return von


# ----------------------------------------------------------------- bloky

def blok_kroky(blok):
    """@kroky -- riadky 'NN | Nadpis kroku | vysvetlenie'."""
    von = []
    for riadok in blok["riadky"]:
        if not riadok.strip():
            continue
        cislo, nazov, text = rozsek(riadok, 3)[:3]
        popis = f'<div class="krok__text">{t(text)}</div>' if text else ""
        von.append(
            f'<div class="krok"><div class="krok__cislo">{t(cislo)}</div>'
            f'<div><div class="krok__nazov">{t(nazov)}</div>{popis}</div></div>'
        )
    return '<div class="blok">' + "".join(von) + "</div>"


def blok_box(blok):
    """@box ŠTÍTOK -- mäkký rámček so štítkom. Zachová riadkovanie."""
    stitok = blok["argument"] or "POZNÁMKA"
    kod = "kod" in stitok.lower() or blok["riadky"] and blok["riadky"][0].startswith("#")
    riadky = [t(r) if r.strip() else "" for r in blok["riadky"]]
    trieda = " box--kod" if kod else ""
    return (f'<div class="blok"><div class="box{trieda}">'
            f'<div class="box__stitok">{t(stitok)}</div>'
            f'<div class="box__text">{chr(10).join(riadky)}</div></div></div>')


def blok_kod(blok):
    """@kod ŠTÍTOK -- to isté ako box, ale vždy s hustejšou sadzbou a bez úprav textu."""
    stitok = blok["argument"] or "SKOPÍRUJ"
    kod = html_mod.escape("\n".join(blok["riadky"]), quote=False)
    return (f'<div class="blok"><div class="box box--kod">'
            f'<div class="box__stitok">{t(stitok)}</div>'
            f'<div class="box__text">{kod}</div></div></div>')


def blok_tabulka(blok):
    hlavicky = rozsek(blok["argument"])
    uzka = " tabulka--uzka" if len(hlavicky) >= 4 else ""
    von = [f'<table class="tabulka{uzka}"><thead><tr>']
    von += [f"<th>{t(h)}</th>" for h in hlavicky]
    von.append("</tr></thead><tbody>")
    for riadok in blok["riadky"]:
        if not riadok.strip():
            continue
        bunky = rozsek(riadok, len(hlavicky))
        von.append("<tr>" + "".join(f"<td>{t(b)}</td>" for b in bunky) + "</tr>")
    von.append("</tbody></table>")
    return '<div class="blok">' + "".join(von) + "</div>"


def blok_pojmy(blok):
    """@pojmy -- dvojice 'ŠTÍTOK | vysvetlenie'. Argument "kod" nechá štítky malými."""
    trieda = " pojem__stitok--kod" if "kod" in blok["argument"] else ""
    von = []
    for riadok in blok["riadky"]:
        if not riadok.strip():
            continue
        stitok, text = rozsek(riadok, 2)[:2]
        von.append(f'<div class="pojem"><div class="pojem__stitok{trieda}">{t(stitok)}</div>'
                   f'<div class="pojem__text">{t(text)}</div></div>')
    return '<div class="blok">' + "".join(von) + "</div>"


def blok_text(blok):
    trieda = "drobne" if "drobne" in blok["argument"] else "odsek"
    von = [f'<p class="{trieda}">{t(o)}</p>' for o in odseky(blok["riadky"])]
    return '<div class="blok">' + "".join(von) + "</div>"


def blok_checklist(blok):
    von = ['<div class="odrazka"><div class="odrazka__box"></div>'
           f'<div class="odrazka__text">{t(r.strip())}</div></div>'
           for r in blok["riadky"] if r.strip()]
    return '<div class="blok">' + "".join(von) + "</div>"


def blok_video(blok):
    von = []
    for riadok in blok["riadky"]:
        if not riadok.strip():
            continue
        nazov, dlzka, adresa = rozsek(riadok, 3)[:3]
        von.append(
            f'<a class="video" href="{html_mod.escape(adresa, quote=True)}">'
            f'<div><div class="video__stitok">{t(blok["argument"] or "VIDEO")}</div>'
            f'<div class="video__nazov">{t(nazov)}</div></div>'
            f'<div><div class="video__dlzka">{t(dlzka)}</div>'
            f'<div class="video__akcia">POZRI{SIPKA}</div></div></a>')
    return '<div class="blok">' + "".join(von) + "</div>"


def blok_terazty(blok):
    text = " ".join(r.strip() for r in blok["riadky"] if r.strip())
    return ('<div class="blok terazty">'
            f'<div class="terazty__stitok">{t(blok["argument"] or "TERAZ TY")}</div>'
            f'<div class="terazty__text">{t(text)}</div></div>')


def blok_zdroje(blok):
    von = []
    for riadok in blok["riadky"]:
        if not riadok.strip():
            continue
        nazov, adresa = rozsek(riadok, 2)[:2]
        von.append(f'<a href="{html_mod.escape(adresa, quote=True)}">{t(nazov)}</a>')
    return ('<div class="blok zdroje">'
            f'<div class="zdroje__stitok">{t(blok["argument"] or "OFICIÁLNE ZDROJE")}</div>'
            f'<div class="zdroje__zoznam">{"".join(von)}</div></div>')


BLOKY = {
    "kroky": blok_kroky,
    "box": blok_box,
    "kod": blok_kod,
    "tabulka": blok_tabulka,
    "pojmy": blok_pojmy,
    "text": blok_text,
    "checklist": blok_checklist,
    "video": blok_video,
    "terazty": blok_terazty,
    "zdroje": blok_zdroje,
}


# ----------------------------------------------------------------- strany

def hlavicka(meta):
    return (f'<div class="hlavicka"><span>{t(ZNACKA)}</span>'
            f'<span>LEKCIA {t(meta.get("cislo", ""))}</span></div>')


def paticka(meta, cislo):
    return (f'<div class="paticka"><span class="paticka__nazov">{t(meta.get("titul", ""))}</span>'
            f'<span class="paticka__cislo">{cislo:02d}</span></div>')


def strana_obal(blok, meta, cislo):
    pole = polia(blok)
    varianta = (pole.get("varianta") or meta.get("varianta") or "a").lower()

    casy = "".join(
        f'<div class="cas"><div class="cas__cislo">{t(c.split("|")[0].strip())}</div>'
        f'<div class="cas__popis">{t(c.split("|")[1].strip() if "|" in c else "")}</div></div>'
        for c in zoznam(pole.get("cas")))

    body = "".join(
        f'<div class="body__riadok"><div class="body__cislo">{i:02d}</div>'
        f'<div class="body__text">{t(b)}</div></div>'
        for i, b in enumerate(zoznam(pole.get("bod")), start=1))

    priprav = ""
    if pole.get("priprav"):
        priprav = (f'<div class="obal__pripravLabel">ČO SI PRIPRAV</div>'
                   f'<div class="obal__priprav">{t(pole["priprav"])}</div>')

    return f"""<section class="strana obal obal--{varianta}">
  <div class="pas"></div>
  {hlavicka(meta)}
  <div class="obal__hlava">
    <div class="obal__cislo">{t(pole.get('cislo', meta.get('cislo', '')))}</div>
    <div class="obal__stitok">{t(pole.get('stitok', ''))}</div>
    {'<div class="obal__nadpis">' + t(pole.get('h1', '')) + '</div>' if varianta != 'b' else ''}
  </div>
  {'<div class="obal__nadpis">' + t(pole.get('h1', '')) + '</div>' if varianta == 'b' else ''}
  <div class="obal__spodok">
    <div class="obal__slub">{t(pole.get('slub', ''))}</div>
    <div class="casy">{casy}</div>
    {priprav}
    <div class="body">{body}</div>
  </div>
  {paticka(meta, cislo)}
</section>"""


def strana_vnutorna(hlava, obsahove_bloky, meta, cislo):
    pole = polia(hlava)
    telo = "".join(BLOKY[b["druh"]](b) for b in obsahove_bloky if b["druh"] in BLOKY)
    return f"""<section class="strana">
  {hlavicka(meta)}
  <div class="telo">
    <div class="nadpis__stitok">{t(pole.get('stitok', 'POSTUP'))}</div>
    <div class="nadpis">{t(pole.get('h1', ''))}</div>
    {telo}
  </div>
  {paticka(meta, cislo)}
</section>"""


def zostav_html(meta, bloky, prve_cislo=1):
    strany, aktualna = [], None
    for blok in bloky:
        if blok["druh"] in ("obal", "strana"):
            if aktualna:
                strany.append(aktualna)
            aktualna = {"typ": blok["druh"], "hlava": blok, "bloky": []}
        elif aktualna:
            aktualna["bloky"].append(blok)
    if aktualna:
        strany.append(aktualna)

    kusy = []
    for index, strana in enumerate(strany):
        cislo = prve_cislo + index
        if strana["typ"] == "obal":
            kusy.append(strana_obal(strana["hlava"], meta, cislo))
        else:
            kusy.append(strana_vnutorna(strana["hlava"], strana["bloky"], meta, cislo))

    nazov = html_mod.escape(f"{meta.get('cislo', '')} {meta.get('titul', 'Lekcia')}".strip())
    return f"""<!doctype html>
<html lang="sk">
<head>
<meta charset="utf-8">
<title>{nazov}</title>
<link rel="stylesheet" href="../build/styl.css">
</head>
<body>
{chr(10).join(kusy)}
</body>
</html>""", len(strany)



# ----------------------------------------------------------------- plán kurzu

PLAN_STRANY = [
    {
        "cislo": "01",
        "stitok": "ZAČNI VÝSLEDKOM",
        "h1": "Menej skúšania.\nViac hotovej práce.",
        "poznamka": "Časy sú odhady čítania a samostatnej praxe, nie dĺžka videí. "
                    "Najprv prejdi lekciu. Potom sprav úlohu. Až potom pokračuj.",
        "moduly": ["01 Štart", "02 Claude"],
    },
    {
        "cislo": "02",
        "stitok": "ZAČNI VÝSLEDKOM",
        "h1": "Od dobrého zadania\nk vlastnému postupu.",
        "poznamka": "Na konci každej lekcie nájdeš kontrolu výsledku, tip navyše "
                    "a ďalší konkrétny krok.",
        "moduly": ["03 ChatGPT", "04 Skills"],
    },
]


def zostav_plan(lekcie):
    """Dve úvodné strany s obsahom kurzu. `lekcie` = [(meta, prva_strana), ...]."""
    kusy = []
    for strana in PLAN_STRANY:
        telo = []
        for modul in strana["moduly"]:
            riadky = [(m, c) for m, c in lekcie if m.get("modul") == modul]
            if not riadky:
                continue
            telo.append(f'<div class="plan__modul">{t(modul)}</div>')
            for meta, cislo in riadky:
                telo.append(
                    f'<div class="riadok">'
                    f'<div class="riadok__cislo">{t(meta.get("cislo", ""))}</div>'
                    f'<div class="riadok__nazov">{t(meta.get("titul", ""))}</div>'
                    f'<div class="riadok__strana">{cislo}</div></div>')
        nadpis = t(strana["h1"]).replace("\n", "<br>")
        kusy.append(f"""<section class="strana plan">
  <div class="pas"></div>
  <div class="hlavicka"><span>{t(ZNACKA)}</span><span>TVOJ PLÁN KURZU</span></div>
  <div class="plan__cislo">{t(strana['cislo'])}</div>
  <div class="plan__hlava">
    <div class="plan__stitok">{t(strana['stitok'])}</div>
    <div class="plan__nadpis">{nadpis}</div>
  </div>
  <div class="plan__spodok">
    <div class="plan__poznamka">{t(strana['poznamka'])}</div>
    {"".join(telo)}
  </div>
  <div class="paticka"><span class="paticka__nazov">Tvoj plán kurzu</span>
    <span class="paticka__cislo">{len(kusy) + 1:02d}</span></div>
</section>""")

    return f"""<!doctype html>
<html lang="sk">
<head>
<meta charset="utf-8">
<title>Tvoj plán kurzu</title>
<link rel="stylesheet" href="../build/styl.css">
</head>
<body>
{chr(10).join(kusy)}
</body>
</html>"""


# ----------------------------------------------------------------- beh

def najdi_chromium():
    """Nájde nainštalovaný Chromium, aj keď nesedí verzia zabalená v Playwrighte."""
    import os

    zadany = os.environ.get("CHROMIUM_PATH")
    if zadany and Path(zadany).exists():
        return zadany
    zaklad = Path(os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers"))
    if zaklad.exists():
        najdene = sorted(zaklad.glob("chromium-*/chrome-linux/chrome"))
        if najdene:
            return str(najdene[-1])
    return None


def vytlac_pdf(dvojice):
    from playwright.sync_api import sync_playwright

    cesta_prehliadaca = najdi_chromium()
    with sync_playwright() as p:
        prehliadac = (p.chromium.launch(executable_path=cesta_prehliadaca)
                      if cesta_prehliadaca else p.chromium.launch())
        strana = prehliadac.new_page()
        for cesta_html, cesta_pdf in dvojice:
            strana.goto(cesta_html.as_uri())
            strana.emulate_media(media="print")
            strana.wait_for_timeout(220)

            pretecene = strana.evaluate("""() => {
                const zle = [];
                document.querySelectorAll('.telo, .obal__spodok, .plan__spodok').forEach((telo, i) => {
                    const presah = telo.scrollHeight - telo.clientHeight;
                    if (presah > 2) zle.push([i + 1, Math.round(presah)]);
                });
                return zle;
            }""")
            for index, presah in pretecene:
                print(f"  !!   {cesta_pdf.stem}: blok {index} pretiekol o ~{presah} px — skráť text")

            # 720 × 900 pt = 10 × 12.5 palca
            strana.pdf(path=str(cesta_pdf), width="10in", height="12.5in",
                       print_background=True, prefer_css_page_size=True,
                       margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
            print(f"  PDF  {cesta_pdf.name}")
        prehliadac.close()


def main():
    argumenty = [a for a in sys.argv[1:] if not a.startswith("--")]
    bez_pdf = "--bez-pdf" in sys.argv

    VYSTUP_HTML.mkdir(parents=True, exist_ok=True)
    VYSTUP_PDF.mkdir(parents=True, exist_ok=True)

    vsetky = sorted(OBSAH.glob("*.txt"))
    # priebežné číslovanie strán naprieč celým kurzom
    cisla, dalsie = {}, 3
    for subor in vsetky:
        meta, bloky = rozdel_lekciu(subor.read_text(encoding="utf-8"))
        cisla[subor] = dalsie
        dalsie += sum(1 for b in bloky if b["druh"] in ("obal", "strana"))

    if not argumenty:
        zoznam_lekcii = []
        for subor in vsetky:
            meta, _ = rozdel_lekciu(subor.read_text(encoding="utf-8"))
            zoznam_lekcii.append((meta, cisla[subor]))
        cesta_plan = VYSTUP_HTML / "00-plan.html"
        cesta_plan.write_text(zostav_plan(zoznam_lekcii), encoding="utf-8")
        print(f"  HTML {cesta_plan.name}")
        plan_dvojica = [(cesta_plan, VYSTUP_PDF / "00-plan.pdf")]
    else:
        plan_dvojica = []

    subory = [s for s in vsetky if not argumenty or any(a in s.name for a in argumenty)]
    if not subory:
        print("Nenašiel som žiadny súbor v KURZ/obsah/.")
        return 1

    dvojice = []
    for subor in subory:
        surovy = subor.read_text(encoding="utf-8")
        zastupne = sorted(set(re.findall(r"\{\{[A-Z0-9_]+\}\}", surovy)))
        if zastupne:
            print(f"  !!   {subor.stem}: nedoplnené {', '.join(zastupne)}")

        meta, bloky = rozdel_lekciu(surovy)
        html, _ = zostav_html(meta, bloky, cisla[subor])
        cesta_html = VYSTUP_HTML / (subor.stem + ".html")
        cesta_html.write_text(html, encoding="utf-8")
        print(f"  HTML {cesta_html.name}")
        dvojice.append((cesta_html, VYSTUP_PDF / (subor.stem + ".pdf")))

    if not bez_pdf:
        vytlac_pdf(plan_dvojica + dvojice)
        if not argumenty:
            import kniha
            kniha.zlucit()

    print(f"\nHotovo: {len(dvojice)} lekcií.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
