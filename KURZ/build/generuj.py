#!/usr/bin/env python3
"""
Generátor kurzu kuchar.ai
=========================

Číta lekcie z KURZ/obsah/*.txt, vyrobí z nich HTML (KURZ/html/)
a z HTML vytlačí PDF cez Chromium (KURZ/pdf/).

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

AUTOR = "TOMÁŠ KUCHARČÍK"
ZNACKA = "@kuchar.ai"


# ----------------------------------------------------------------- parser

def rozdel_lekciu(text):
    """Rozdelí súbor lekcie na hlavičku (meta) a zoznam blokov."""
    meta = {}
    bloky = []
    aktualny = None

    for surovy in text.splitlines():
        riadok = surovy.rstrip()

        if riadok.startswith("@"):
            if aktualny:
                bloky.append(aktualny)
            hlava = riadok[1:].strip()
            druh, _, argument = hlava.partition(" ")
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
    """Riadky typu 'kluc: hodnota' v bloku prevedie na slovník (viacnásobné kľúče do zoznamu)."""
    vysledok = {}
    for riadok in blok["riadky"]:
        if not riadok.strip():
            continue
        kluc, oddelovac, hodnota = riadok.partition(":")
        if not oddelovac:
            continue
        kluc = kluc.strip()
        hodnota = hodnota.strip()
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
# „úvodzovky" -> „úvodzovky“
VZOR_UVODZOVKY = re.compile(r"„([^„”“]*?)\"")


def t(surovy):
    """Escapne HTML a povolí **tučné**, `kód`, šípku " -> " a pomlčku " -- ".

    Navyše dorába slovenskú typografiu: pevná medzera za jednopísmenovými
    predložkami a správne zatvorené úvodzovky.
    """
    text = surovy or ""
    for _ in range(2):  # dva prechody kvôli prekrývajúcim sa zhodám
        text = VZOR_PREDLOZKA.sub("\\1\\2\u00a0", text)
    bezpecny = html_mod.escape(text, quote=False)
    bezpecny = VZOR_TUCNE.sub(r"<strong>\1</strong>", bezpecny)
    bezpecny = VZOR_KOD.sub(r"<code>\1</code>", bezpecny)
    bezpecny = bezpecny.replace(" -&gt; ", f" {SIPKA_VPRAVO} ").replace(" -- ", " — ")
    bezpecny = VZOR_UVODZOVKY.sub("„\\1”", bezpecny)
    return bezpecny


def rozsek(riadok, pocet=None):
    casti = [c.strip() for c in riadok.split("|")]
    if pocet is not None:
        while len(casti) < pocet:
            casti.append("")
    return casti


# ----------------------------------------------------------------- bloky

def blok_kroky(blok):
    von = []
    for riadok in blok["riadky"]:
        if not riadok.strip():
            continue
        casti = rozsek(riadok)
        if len(casti) >= 3:
            cislo, stitok, text = casti[0], casti[1], " | ".join(casti[2:])
            trieda = ""
        else:
            cislo, stitok, text = casti[0], "", " | ".join(casti[1:])
            trieda = " krok--bez"
        von.append(
            f'<div class="krok{trieda}">'
            f'<div class="krok__cislo">{t(cislo)}</div>'
            f'<div class="krok__stitok">{t(stitok)}</div>'
            f'<div class="krok__text">{t(text)}</div></div>'
        )
    return '<div class="blok">' + "".join(von) + "</div>"


def blok_zoznam(blok):
    von = []
    for index, riadok in enumerate(r for r in blok["riadky"] if r.strip()):
        casti = rozsek(riadok, 2)
        cislo = casti[0] if len(casti) > 1 else f"{index + 1:02d}"
        text = casti[1] if len(casti) > 1 else casti[0]
        von.append(
            f'<div class="riadok"><div class="riadok__cislo">{t(cislo)}</div>'
            f'<div class="riadok__text">{t(text)}</div></div>'
        )
    return '<div class="blok">' + "".join(von) + "</div>"


def blok_pojmy(blok):
    """@pojmy -- dvojice štítok | vysvetlenie. S argumentom "kod" ostanú
    štítky tak, ako sú napísané (pre názvy polí a príkazov)."""
    von = []
    trieda = " pojem__stitok--kod" if "kod" in blok["argument"] else ""
    for riadok in blok["riadky"]:
        if not riadok.strip():
            continue
        stitok, text = rozsek(riadok, 2)[:2]
        von.append(
            f'<div class="pojem"><div class="pojem__stitok{trieda}">{t(stitok)}</div>'
            f'<div class="pojem__text">{t(text)}</div></div>'
        )
    return '<div class="blok">' + "".join(von) + "</div>"


def blok_terminal(blok):
    stitok = blok["argument"] or "TERMINAL"
    kod = html_mod.escape("\n".join(blok["riadky"]), quote=False)
    return (
        f'<div class="blok"><div class="terminal__stitok">{t(stitok)}</div>'
        f'<div class="terminal">{kod}</div></div>'
    )


def blok_pravidlo(blok):
    stitok = blok["argument"] or "PRAVIDLO"
    text = " ".join(r.strip() for r in blok["riadky"] if r.strip())
    return (
        f'<div class="blok pravidlo"><div class="pravidlo__stitok">{t(stitok)}</div>'
        f'<div class="pravidlo__text">{t(text)}</div></div>'
    )


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


def blok_checklist(blok):
    von = []
    for riadok in blok["riadky"]:
        if not riadok.strip():
            continue
        von.append(
            '<div class="odrazka"><div class="odrazka__box"></div>'
            f'<div class="odrazka__text">{t(riadok.strip())}</div></div>'
        )
    return '<div class="blok">' + "".join(von) + "</div>"


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


def blok_video(blok):
    """@video NÁZOV | dĺžka | adresa -- veľká klikateľná karta na video.

    Video sa do PDF vložiť nedá (prehralo by sa len v Adobe Acrobate).
    Karta preto odkazuje tam, kde video naozaj beží.
    """
    von = []
    for riadok in blok["riadky"]:
        if not riadok.strip():
            continue
        nazov, dlzka, adresa = rozsek(riadok, 3)[:3]
        von.append(
            f'<a class="video" href="{html_mod.escape(adresa, quote=True)}">'
            f'<div class="video__vlavo">'
            f'<div class="video__stitok">{t(blok["argument"] or "VIDEO")}</div>'
            f'<div class="video__nazov">{t(nazov)}</div></div>'
            f'<div class="video__vpravo">'
            f'<div class="video__dlzka">{t(dlzka)}</div>'
            f'<div class="video__akcia">POZRI{SIPKA}</div></div></a>'
        )
    return '<div class="blok">' + "".join(von) + "</div>"


def blok_odkazy(blok):
    von = []
    for riadok in blok["riadky"]:
        if not riadok.strip():
            continue
        nazov, adresa = rozsek(riadok, 2)[:2]
        von.append(
            f'<a class="odkaz" href="{html_mod.escape(adresa, quote=True)}">'
            f'<span class="odkaz__nazov">{t(nazov)}</span>'
            f'<span class="odkaz__akcia">OTVOR{SIPKA}</span></a>'
        )
    return '<div class="blok odkazy">' + "".join(von) + "</div>"


def blok_text(blok):
    von = []
    velky = "velky" in blok["argument"]
    drobne = "drobne" in blok["argument"]
    trieda = "odsek odsek--velky" if velky else ("drobne" if drobne else "odsek")
    odsek = []
    for riadok in blok["riadky"]:
        if riadok.strip():
            odsek.append(riadok.strip())
        elif odsek:
            von.append(f'<p class="{trieda}">{t(" ".join(odsek))}</p>')
            odsek = []
    if odsek:
        von.append(f'<p class="{trieda}">{t(" ".join(odsek))}</p>')
    return '<div class="blok">' + "".join(von) + "</div>"


def blok_zaver(blok):
    pole = polia(blok)
    return (
        '<div class="blok odkaz-na-koniec">'
        f'<div class="odkaz-na-koniec__hlavne">{t(pole.get("hlavne", ""))}</div>'
        f'<div class="odkaz-na-koniec__vedlajsie">{t(pole.get("vedlajsie", ""))}</div></div>'
    )


BLOKY = {
    "kroky": blok_kroky,
    "zoznam": blok_zoznam,
    "pojmy": blok_pojmy,
    "terminal": blok_terminal,
    "pravidlo": blok_pravidlo,
    "tabulka": blok_tabulka,
    "checklist": blok_checklist,
    "video": blok_video,
    "odkazy": blok_odkazy,
    "text": blok_text,
    "zaver": blok_zaver,
}


# ----------------------------------------------------------------- strany

def hlavicka(stopa, titulna=False):
    return (
        '<div class="hlavicka">'
        f'<div class="hlavicka__znacka">{t(ZNACKA)}</div>'
        f'<div class="hlavicka__stopa">{t(stopa)}</div></div>'
    )


def paticka(cislo, celkom):
    return (
        f'<div class="paticka"><span>{t(AUTOR)}</span>'
        f"<span>{cislo:02d} / {celkom}</span></div>"
    )


def strana_obal(blok, meta, stopa, cislo, celkom):
    pole = polia(blok)
    stitky = "".join(
        f'<div class="stitok">{t(s)}</div>'
        for s in [c.strip() for c in meta.get("stitky", "").split("|")] if s
    )
    karty = []
    for surova in zoznam(pole.get("karta")):
        hore, stred, dole = rozsek(surova, 3)[:3]
        karty.append(
            '<div class="karta">'
            f'<div class="karta__hore">{t(hore)}</div>'
            f'<div class="karta__stred">{t(stred)}</div>'
            f'<div class="karta__dole">{t(dole)}</div></div>'
        )
    return f"""<section class="strana strana--titulna">
  <div class="obal"></div>
  {hlavicka(stopa, titulna=True)}
  <div class="obal__telo">
    <div class="obal__stitok">{t(pole.get('stitok', ''))}</div>
    <div class="obal__nadpis"><b>{t(pole.get('h1', ''))}</b><span>{t(pole.get('h2', ''))}</span>{'<span>' + t(pole.get('h3', '')) + '</span>' if pole.get('h3') else ''}</div>
  </div>
  <div class="uvod dvojstlpec">
    <div class="dvojstlpec__stitok">{t(pole.get('nadstitok', 'ČO ŤA TÁTO LEKCIA NAUČÍ'))}</div>
    <div class="dvojstlpec__telo">
      <div class="uvod__hlavne">{t(pole.get('hlavne', ''))}</div>
      <div class="uvod__vedlajsie">{t(pole.get('vedlajsie', ''))}</div>
    </div>
  </div>
  <div class="stitky">{stitky}</div>
  <div class="karty">{''.join(karty)}</div>
  <div class="zaver">
    <div class="zaver__veta">{t(pole.get('vysledok', ''))}</div>
    <div class="zaver__drobne">{t(pole.get('drobne', ''))}</div>
  </div>
  {paticka(cislo, celkom)}
</section>"""


def strana_vnutorna(hlava, obsahove_bloky, stopa, cislo, celkom):
    pole = polia(hlava)
    telo = "".join(BLOKY[b["druh"]](b) for b in obsahove_bloky if b["druh"] in BLOKY)
    druhy_riadok = f'<span>{t(pole.get("h2", ""))}</span>' if pole.get("h2") else ""
    return f"""<section class="strana strana--vnutorna">
  {hlavicka(stopa)}
  <div class="telo">
    <div class="nadpis__stitok">{t(pole.get('stitok', ''))}</div>
    <div class="nadpis"><b>{t(pole.get('h1', ''))}</b>{druhy_riadok}</div>
    {telo}
  </div>
  {paticka(cislo, celkom)}
</section>"""


def zostav_html(meta, bloky):
    stopa = meta.get("stopa", "KUCHAR.AI")
    strany = []
    aktualna = None
    for blok in bloky:
        if blok["druh"] in ("obal", "strana"):
            if aktualna:
                strany.append(aktualna)
            aktualna = {"typ": blok["druh"], "hlava": blok, "bloky": []}
        elif aktualna:
            aktualna["bloky"].append(blok)
    if aktualna:
        strany.append(aktualna)

    # vnútorné strany majú len dva riadky nadpisu, obal tri
    for strana in strany:
        pole = polia(strana["hlava"])
        nadbytocne = [k for k in ("h3", "h4") if k in pole]
        if strana["typ"] == "obal":
            nadbytocne = [k for k in ("h4",) if k in pole]
        if nadbytocne:
            print(f"  !!   {meta.get('titul', '?')}: strana \"{pole.get('stitok', '')}\" "
                  f"má naviac {', '.join(nadbytocne)} — nezobrazí sa")

    celkom = len(strany)
    kusy = []
    for index, strana in enumerate(strany, start=1):
        if strana["typ"] == "obal":
            kusy.append(strana_obal(strana["hlava"], meta, stopa, index, celkom))
        else:
            kusy.append(strana_vnutorna(strana["hlava"], strana["bloky"], stopa, index, celkom))

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
        prehliadac = p.chromium.launch(executable_path=cesta_prehliadaca) if cesta_prehliadaca else p.chromium.launch()
        strana = prehliadac.new_page()
        for cesta_html, cesta_pdf in dvojice:
            strana.goto(cesta_html.as_uri())
            strana.emulate_media(media="print")
            strana.wait_for_timeout(220)

            # varovanie, ak sa obsah nezmestí na stranu (orezalo by sa to)
            pretecene = strana.evaluate("""() => {
                const zle = [];
                document.querySelectorAll('.telo').forEach((telo, i) => {
                    const presah = telo.scrollHeight - telo.clientHeight;
                    if (presah > 2) zle.push([i + 2, Math.round(presah)]);
                });
                return zle;
            }""")
            for cislo_strany, presah in pretecene:
                print(f"  !!   {cesta_pdf.stem}: strana {cislo_strany} pretekla o ~{presah} px — skráť text")

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

    subory = sorted(OBSAH.glob("*.txt"))
    if argumenty:
        subory = [s for s in subory if any(a in s.name for a in argumenty)]
    if not subory:
        print("Nenašiel som žiadny súbor v KURZ/obsah/.")
        return 1

    dvojice = []
    for subor in subory:
        meta, bloky = rozdel_lekciu(subor.read_text(encoding="utf-8"))
        zastupne = sorted(set(re.findall(r"\{\{[A-Z0-9_]+\}\}", subor.read_text(encoding="utf-8"))))
        if zastupne:
            print(f"  !!   {subor.stem}: nedoplnené {', '.join(zastupne)}")

        cesta_html = VYSTUP_HTML / (subor.stem + ".html")
        cesta_html.write_text(zostav_html(meta, bloky), encoding="utf-8")
        print(f"  HTML {cesta_html.name}")
        dvojice.append((cesta_html, VYSTUP_PDF / (subor.stem + ".pdf")))

    if not bez_pdf:
        vytlac_pdf(dvojice)
        # celý kurz v jednom PDF — len keď sme generovali všetko
        if not argumenty:
            import kniha
            kniha.zlucit()

    print(f"\nHotovo: {len(dvojice)} lekcií.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
