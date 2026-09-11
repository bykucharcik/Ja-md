#!/usr/bin/env python3
"""
Zlúčenie celého kurzu do jedného PDF
====================================

    KURZ/KURZ-CELY.pdf   všetkých 24 lekcií za sebou, s obsahom na preklikanie

Toto je súbor, ktorý posielaš ďalej — aj človeku, aj AI. Vidno v ňom sadzbu
a rozloženie, nie len text.

Volá sa automaticky z generuj.py, keď generuješ celý kurz.
Samostatne: python3 KURZ/build/kniha.py
"""

from pathlib import Path

import generuj as g

KOREN = g.KOREN
PDF_SPOLU = KOREN / "KURZ-CELY.pdf"


# ----------------------------------------------------------------- pdf

def uroby_pdf(lekcie):
    """Zlúči jednotlivé PDF do jedného a doplní obsah na preklikanie."""
    import pymupdf

    spolu = pymupdf.open()
    obsah = []
    posledny_modul = None

    for stem, meta, _ in lekcie:
        zdroj = g.VYSTUP_PDF / f"{stem}.pdf"
        if not zdroj.exists():
            print(f"  !!   chýba {zdroj.name} — preskakujem")
            continue
        prva = spolu.page_count + 1
        modul = meta.get("modul", "")
        if modul != posledny_modul:
            obsah.append([1, modul, prva])
            posledny_modul = modul
        obsah.append([2, f"{meta.get('cislo', '')} {meta.get('titul', '')}".strip(), prva])
        with pymupdf.open(zdroj) as d:
            spolu.insert_pdf(d)

    spolu.set_toc(obsah)
    spolu.set_metadata({"title": "Kurz kuchar.ai", "author": g.AUTOR})
    spolu.save(PDF_SPOLU, garbage=4, deflate=True)
    stran = spolu.page_count
    spolu.close()
    return stran


# ----------------------------------------------------------------- beh

def zlucit():
    lekcie = []
    for subor in sorted(g.OBSAH.glob("*.txt")):
        meta, bloky = g.rozdel_lekciu(subor.read_text(encoding="utf-8"))
        lekcie.append((subor.stem, meta, bloky))

    if not lekcie:
        print("Nenašiel som žiadnu lekciu.")
        return

    stran = uroby_pdf(lekcie)
    print(f"  PDF  {PDF_SPOLU.name} ({stran} strán, "
          f"{PDF_SPOLU.stat().st_size // 1024 // 1024} MB)")


if __name__ == "__main__":
    zlucit()
