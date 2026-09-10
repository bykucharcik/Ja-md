#!/usr/bin/env python3
"""
Prevedie študijný archív (Markdown) na PDF v štýle @kuchar.ai.

Štýl je prekreslený podľa referencie `Kuchar_AI_Student_Kit.pdf` — tmavá navy
plocha s technickým gridom, modrý akcent, zaoblené karty, mono popisky.
Renderuje sa cez Chromium (print-to-PDF), takže výsledok sedí s tým, ako
vyzerajú naše ostatné materiály.

Použitie:
    python3 build_pdf.py --archive /cesta/k/AI_STUDIJNY_ARCHIV
    python3 build_pdf.py --archive ... --only 04_TIPY_A_TRIKY --limit 3 --keep-html
"""
from __future__ import annotations

import argparse
import base64
import html as htmlmod
import io
import re
import sys
from datetime import date
from pathlib import Path

import markdown

HERE = Path(__file__).resolve().parent
STYLE_DIR = HERE / "style"

ZNACKA = "@kuchar.ai"
KIT = "AI študijný archív"
AUTOR = "Tomáš Kucharčík"

CHROME_CANDIDATES = [
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/usr/bin/google-chrome",
]

SEKCIE = {
    "00_PROJEKT": "Projekt",
    "01_START_HERE": "Start here",
    "02_CLAUDE_MANUAL": "Claude manuál",
    "03_CHATGPT_MANUAL": "ChatGPT manuál",
    "04_TIPY_A_TRIKY": "Tipy a triky",
    "05_CHECKLISTY": "Checklisty",
    "06_SABLONY_A_PROMPTY": "Šablóny a prompty",
    "07_NASTROJE_A_ZLAVY": "Nástroje a zľavy",
    "08_INDEX": "Index",
}

# nadpis v zdroji -> modrý kicker nad ním
KICKERS = {
    "Text v tele lekcie": "Zdrojový text",
    "Doslovný text sekcie (pôvodný jazyk)": "Doslovný prepis",
    "Doslovný obsah SKILL.md (pôvodný jazyk)": "Doslovný prepis",
    "Video": "Médium",
    "Prílohy a odkazy v module": "Materiály",
    "Príloha": "Materiály",
    "Workflow": "Postup",
    "Critical Rules": "Pravidlá",
    "Notes": "Poznámky",
    "Stack": "Nástroje",
    "Process": "Postup",
    "Setup Checklist": "Checklist",
}

GAP_SENTENCE = "V dostupnom zdroji sa táto informácia nenachádzala."

MD_EXT = ["tables", "fenced_code", "sane_lists"]

DECO_SVG = (
    '<svg class="deco" viewBox="0 0 430 430" xmlns="http://www.w3.org/2000/svg">'
    '<circle class="r1" cx="215" cy="215" r="212"/>'
    '<circle class="r2" cx="215" cy="215" r="168"/>'
    '<circle class="r3" cx="215" cy="215" r="120"/>'
    "</svg>"
)

def pocet(n: int, one: str, few: str, many: str) -> str:
    """1 modul / 2 moduly / 5 modulov."""
    if n == 1:
        return f"{n} {one}"
    if 2 <= n <= 4:
        return f"{n} {few}"
    return f"{n} {many}"


MESIACE = [
    "januára", "februára", "marca", "apríla", "mája", "júna",
    "júla", "augusta", "septembra", "októbra", "novembra", "decembra",
]


# ---------------------------------------------------------------- pomocné


def fix_mojibake(text: str) -> str:
    """Opraví UTF-8 prečítané ako cp1252 (â€™, Ã¡ …), čo je v pár zdrojoch."""
    if "â€" not in text and "Ã" not in text and "Å" not in text:
        return text
    try:
        return text.encode("cp1252", errors="strict").decode("utf-8", errors="strict")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text


def md(text: str) -> str:
    return markdown.markdown(text, extensions=MD_EXT, output_format="html5")


def inline_md(text: str) -> str:
    """Markdown pre jeden riadok — bez obaľujúceho <p>."""
    out = md(text).strip()
    if out.startswith("<p>") and out.endswith("</p>"):
        out = out[3:-4]
    return out


def sk_date(iso: str) -> str:
    try:
        y, m, d = (int(x) for x in iso.split("-"))
        return f"{d}. {MESIACE[m - 1]} {y}"
    except (ValueError, IndexError):
        return iso


def style_html(frag: str) -> str:
    """Prepíše holé HTML na naše komponenty (terminál, tabuľky, chýbajúci obsah)."""

    def term(m: re.Match) -> str:
        lang = (m.group("lang") or "").strip().lower()
        body = m.group("body")
        label = {
            "": "kód",
            "bash": "terminál",
            "sh": "terminál",
            "shell": "terminál",
            "console": "terminál",
            "zsh": "terminál",
            "text": "kód",
        }.get(lang, lang or "kód")
        long = " long" if body.count("\n") > 24 else ""
        return (
            f'<div class="term{long}"><div class="term-bar">'
            f'<span class="term-label">{htmlmod.escape(label)}</span></div>'
            f"<pre>{body}</pre></div>"
        )

    frag = re.sub(
        r'<pre><code(?: class="language-(?P<lang>[^"]*)")?>(?P<body>.*?)</code></pre>',
        term,
        frag,
        flags=re.S,
    )
    frag = re.sub(
        r"<table>(.*?)</table>", r'<div class="tw"><table>\1</table></div>', frag, flags=re.S
    )

    # vzdialené obrázky (skool/drive assety) sa do PDF nenačítajú — odkaz na ne
    # aj tak ostáva v texte, takže samotné <img> zahodíme
    frag = re.sub(r"<img[^>]*>", "", frag)

    gap = htmlmod.escape(GAP_SENTENCE)
    frag = frag.replace(f"<code>{gap}</code>", f'<span class="gap">{gap}</span>')
    frag = frag.replace(f"<p>{gap}</p>", f'<p><span class="gap">{gap}</span></p>')
    return frag


def note(body_html: str, label: str = "", kind: str = "") -> str:
    cls = f"note {kind}".strip()
    lbl = f'<span class="lbl">{htmlmod.escape(label)}</span>' if label else ""
    return f'<div class="{cls}">{lbl}{body_html}</div>'


# ---------------------------------------------------------------- parsovanie


def split_sections(body: str) -> list[tuple[str, str]]:
    """Rozdelí telo na (nadpis H2, text). Prvý blok má prázdny nadpis."""
    parts: list[tuple[str, list[str]]] = [("", [])]
    fence = False
    for line in body.splitlines():
        if line.lstrip().startswith("```"):
            fence = not fence
        if not fence and line.startswith("## "):
            parts.append((line[3:].strip(), []))
        else:
            parts[-1][1].append(line)
    return [(h, "\n".join(b).strip()) for h, b in parts]


def parse_kv_bullets(text: str) -> list[tuple[str, str]]:
    """`- Kľúč: hodnota` -> [(kľúč, hodnota)]; ak sa nedá, prázdny zoznam."""
    rows: list[tuple[str, str]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if not line.startswith("- "):
            return []
        m = re.match(r"^(?:\*\*)?([^:*]{2,40}?)(?:\*\*)?:\s+(.+)$", line[2:].strip())
        if not m:
            return []
        rows.append((m.group(1).strip(), m.group(2).strip()))
    return rows


def kv_card(rows: list[tuple[str, str]], label: str) -> str:
    out = []
    for k, v in rows:
        val = (
            f'<a href="{htmlmod.escape(v)}">{htmlmod.escape(v)}</a>'
            if v.startswith("http")
            else inline_md(v)
        )
        out.append(f"<dt>{htmlmod.escape(k)}</dt><dd>{val}</dd>")
    lbl = f'<span class="lbl">{htmlmod.escape(label)}</span>' if label else ""
    return f'<div class="hilite">{lbl}<dl>{"".join(out)}</dl></div>'


def extract_frontmatter(text: str) -> tuple[list[tuple[str, str]], str]:
    """Vytiahne `---\\nkey: value\\n---` hlavičku (SKILL.md) zo začiatku textu."""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.S)
    if not m:
        return [], text
    rows: list[tuple[str, str]] = []
    for line in m.group(1).splitlines():
        kv = re.match(r"^([A-Za-z_][\w-]{0,30}):\s*(.*)$", line)
        if not kv:
            if rows and line.startswith((" ", "\t")):
                rows[-1] = (rows[-1][0], f"{rows[-1][1]} {line.strip()}")
                continue
            return [], text
        rows.append((kv.group(1), kv.group(2).strip()))
    return rows, text[m.end():]


def title_html(title: str) -> tuple[str, str]:
    """Dvojtónový titulok: prvá časť tučná, zvyšok tenký (ako v referencii)."""
    n = len(title)
    cls = "" if n <= 26 else (" class=\"small\"" if n <= 56 else " class=\"xsmall\"")
    for sep in (": ", " — ", " – ", " - "):
        if sep in title:
            head, _, tail = title.partition(sep)
            return cls, (
                f"{htmlmod.escape(head.rstrip(':'))}"
                f'<span class="thin">{htmlmod.escape(tail)}</span>'
            )
    return cls, htmlmod.escape(title)


# ---------------------------------------------------------------- dokument


def render_document(
    *,
    title: str,
    lede: str,
    eyebrow: str,
    body: str,
    pills: list[str],
    stamp: str,
    foot: str,
) -> str:
    cls, ttl = title_html(title)
    cover = [
        '<header class="cover">',
        f'<div class="eyebrow">{htmlmod.escape(eyebrow)}</div>',
        f"<h1{cls}>{ttl}</h1>",
    ]
    if lede:
        cover.append(f'<p class="lede">{inline_md(lede)}</p>')

    chunks: list[str] = []
    tail: list[str] = []

    for heading, text in split_sections(body):
        if not heading and not text:
            continue

        # zdroj lekcie -> zvýraznená karta hneď pod titulkom
        if heading == "Odkiaľ to je":
            rows = parse_kv_bullets(text)
            cover.append(kv_card(rows, "Odkiaľ to je") if rows else style_html(md(text)))
            continue

        # vysvetlivky k rozsahu -> callout na koniec dokumentu
        if heading in ("Ako čítať túto lekciu", "Čo v zdroji nie je"):
            tail.append(note(style_html(md(text)), label=heading))
            continue

        head = ""
        if heading:
            kicker = KICKERS.get(heading, "")
            head = (
                f'<div class="kicker">{htmlmod.escape(kicker)}</div>' if kicker else ""
            ) + f"<h2>{inline_md(heading)}</h2>"

        fm, rest = extract_frontmatter(text)
        fm_html = ""
        if fm:
            dl = "".join(
                f"<dt>{htmlmod.escape(k)}</dt><dd>{htmlmod.escape(v)}</dd>" for k, v in fm
            )
            fm_html = f'<div class="hilite"><span class="lbl">Hlavička skillu</span><dl>{dl}</dl></div>'

        chunks.append(f"<section>{head}{fm_html}{style_html(md(rest))}</section>")

    if pills:
        cover.append(
            '<div class="pills">'
            + "".join(f'<span class="pill">{htmlmod.escape(p)}</span>' for p in pills)
            + "</div>"
        )
    if stamp:
        cover.append(f'<div class="stamp">{htmlmod.escape(stamp)}</div>')
    cover.append("</header>")

    return (
        DECO_SVG
        + "".join(cover)
        + "".join(chunks)
        + "".join(tail)
        + f'<div class="docfoot">{foot}</div>'
    )


def page_html(inner: str, title: str) -> str:
    css = (STYLE_DIR / "kurz.css").read_text(encoding="utf-8")
    fonts = (STYLE_DIR / "fonts.css").read_text(encoding="utf-8")

    def embed(m: re.Match) -> str:
        b64 = base64.b64encode((STYLE_DIR / "fonts" / m.group(1)).read_bytes()).decode()
        return f"url(data:font/woff2;base64,{b64})"

    css = css.replace('@import url("fonts.css");', re.sub(r"url\(fonts/([^)]+)\)", embed, fonts))
    return (
        '<!doctype html><html lang="sk" class="pdf"><head><meta charset="utf-8">'
        f"<title>{htmlmod.escape(title)}</title><style>{css}</style></head>"
        f"<body>{inner}</body></html>"
    )


HEADER_TPL = (
    '<div style="width:100%;padding:0 15mm;font-family:Arial,Helvetica,sans-serif;'
    'display:flex;justify-content:space-between;align-items:baseline;">'
    '<span style="font-size:8pt;font-weight:700;color:#F7F9FC;">__ZNACKA__</span>'
    '<span style="font-size:6.4pt;letter-spacing:.13em;text-transform:uppercase;'
    'color:#737D8D;">__KIT__</span></div>'
)

FOOTER_TPL = (
    '<div style="width:100%;padding:0 15mm;font-family:Arial,Helvetica,sans-serif;'
    'display:flex;justify-content:space-between;align-items:baseline;">'
    '<span style="font-size:6.4pt;letter-spacing:.13em;text-transform:uppercase;'
    'color:#5B6577;">__AUTOR__</span>'
    '<span style="font-size:6.6pt;color:#5B6577;letter-spacing:.08em;">'
    '<span class="pageNumber"></span> / <span class="totalPages"></span></span></div>'
)


# ---------------------------------------------------------------- vstupy


def module_doc(md_path: Path, archive: Path) -> str:
    raw = fix_mojibake(md_path.read_text(encoding="utf-8"))
    lines = raw.splitlines()

    title = md_path.parent.name
    i = 0
    if lines and lines[0].startswith("# "):
        title = lines[0][2:].strip()
        i = 1

    lede_lines: list[str] = []
    while i < len(lines) and not lines[i].startswith("## "):
        lede_lines.append(lines[i])
        i += 1
    lede = "\n".join(lede_lines).strip()
    body = "\n".join(lines[i:])

    section_key = md_path.parent.relative_to(archive).parts[0]
    module = md_path.parent.name
    num = module.split("_")[0]

    pills = []
    if num.isdigit():
        pills.append(f"modul {int(num):02d}")
    low = raw.lower()
    if "skool.com" in low:
        pills.append("skool")
    if "drive.google.com" in low:
        pills.append("google drive")
    if "docs.google.com" in low:
        pills.append("google docs")
    if not pills:
        pills.append(SEKCIE.get(section_key, section_key))

    dm = re.search(r"(20\d\d-\d\d-\d\d)", lede)
    stamp = f"Zdroj otvorený: {sk_date(dm.group(1))}" if dm else ""

    foot = (
        f"<b>{htmlmod.escape(KIT)}</b> · {htmlmod.escape(SEKCIE.get(section_key, section_key))} "
        f"· {htmlmod.escape(module)}<br>"
        "Študijné spracovanie pre interný kurz. Obsahuje iba to, čo bolo v zdroji reálne otvorené."
    )
    inner = render_document(
        title=title,
        lede=lede,
        eyebrow=SEKCIE.get(section_key, section_key),
        body=body,
        pills=pills,
        stamp=stamp,
        foot=foot,
    )
    return page_html(inner, title)


def standalone_doc(md_path: Path, archive: Path) -> str:
    raw = fix_mojibake(md_path.read_text(encoding="utf-8"))
    lines = raw.splitlines()

    title = md_path.stem
    i = 0
    if lines and lines[0].startswith("# "):
        title = lines[0][2:].strip()
        i = 1

    lede_lines: list[str] = []
    while i < len(lines) and not lines[i].startswith(("## ", "|")):
        lede_lines.append(lines[i])
        i += 1
    body = "\n".join(lines[i:])

    paras = [p.strip() for p in "\n".join(lede_lines).strip().split("\n\n") if p.strip()]
    lede = paras[0] if paras else ""
    pills: list[str] = []
    rest_paras: list[str] = []
    for p in paras[1:]:
        m = re.match(r"^([^:]{3,22}):\s*(.+)$", p.replace("\n", " "))
        if m and len(m.group(2)) <= 24:
            pills.append(f"{m.group(1).strip().lower()} {m.group(2).strip()}")
        else:
            rest_paras.append(p)
    if rest_paras:
        body = "\n\n".join(rest_paras) + "\n\n" + body

    rel = md_path.relative_to(archive)
    section_key = rel.parts[0] if len(rel.parts) > 1 else "00_PROJEKT"
    if not pills:
        pills.append(SEKCIE.get(section_key, section_key))

    dm = re.search(r"(20\d\d-\d\d-\d\d)", lede)
    stamp = f"Zdroj otvorený: {sk_date(dm.group(1))}" if dm else ""

    foot = (
        f"<b>{htmlmod.escape(KIT)}</b> · {htmlmod.escape(SEKCIE.get(section_key, section_key))}<br>"
        "Študijné spracovanie pre interný kurz."
    )
    inner = render_document(
        title=title,
        lede=lede,
        eyebrow=SEKCIE.get(section_key, section_key),
        body=body,
        pills=pills[:4],
        stamp=stamp,
        foot=foot,
    )
    return page_html(inner, title)


def contents_doc(archive: Path, modules: list[Path]) -> str:
    by_sec: dict[str, list[tuple[str, str]]] = {}
    for m in modules:
        sec = m.relative_to(archive).parts[0]
        num, _, rest = m.parent.name.partition("_")
        first = fix_mojibake(m.read_text(encoding="utf-8")).splitlines()[0]
        title = first[2:].strip() if first.startswith("# ") else rest.replace("_", " ")
        by_sec.setdefault(sec, []).append((num, title))

    blocks = []
    for sec in sorted(by_sec):
        items = "".join(
            f'<li><span class="n">{htmlmod.escape(n)}</span>'
            f'<span class="t">{htmlmod.escape(t)}</span></li>'
            for n, t in sorted(by_sec[sec], key=lambda x: x[0])
        )
        blocks.append(
            f'<div class="toc-sec"><div class="kicker">{pocet(len(by_sec[sec]), "modul", "moduly", "modulov")}</div>'
            f"<h2>{htmlmod.escape(SEKCIE.get(sec, sec))}</h2><ol>{items}</ol></div>"
        )

    total = sum(len(v) for v in by_sec.values())
    pills = [
        pocet(total, "modul", "moduly", "modulov"),
        pocet(len(by_sec), "sekcia", "sekcie", "sekcií"),
        "pdf kit",
    ]
    cover = (
        '<header class="cover">'
        '<div class="eyebrow">Obsah archívu</div>'
        '<h1>AI študijný<span class="thin">archív.</span></h1>'
        '<p class="lede">Kompletný zoznam modulov pripravených ako študijné PDF. '
        "Každý modul má vlastný súbor v priečinku <code>PDF/</code> vedľa svojich zdrojov.</p>"
        + '<div class="pills">'
        + "".join(f'<span class="pill">{htmlmod.escape(p)}</span>' for p in pills)
        + "</div>"
        + f'<div class="stamp">Zostavené: {sk_date(date.today().isoformat())}</div>'
        "</header>"
    )
    foot = f"<b>{htmlmod.escape(KIT)}</b> · obsah<br>Študijné spracovanie pre interný kurz."
    inner = (
        DECO_SVG
        + cover
        + f'<div class="toc">{"".join(blocks)}</div>'
        + f'<div class="docfoot">{foot}</div>'
    )
    return page_html(inner, f"{KIT} — obsah")


# ---------------------------------------------------------------- beh


def compose(content: bytes, backdrop: bytes) -> bytes:
    """Podloží každú stranu obsahu tmavým podkladom s gridom."""
    from pypdf import PdfReader, PdfWriter

    src = PdfReader(io.BytesIO(content))
    writer = PdfWriter()
    for i in range(len(src.pages)):
        base = PdfReader(io.BytesIO(backdrop)).pages[0]
        base.merge_page(src.pages[i])
        writer.add_page(base)
    # podklad je na každej strane rovnaký — bez deduplikácie by sa jeho
    # objekty uložili toľkokrát, koľko má dokument strán
    writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def chrome_path() -> str:
    for c in CHROME_CANDIDATES:
        if Path(c).exists():
            return c
    hits = sorted(Path("/opt/pw-browsers").glob("chromium-*/chrome-linux/chrome"))
    if hits:
        return str(hits[-1])
    raise SystemExit("Nenašiel som Chromium — zadaj cestu cez --chrome.")


def collect(archive: Path) -> tuple[list[Path], list[Path]]:
    modules = sorted(
        p for p in archive.rglob("03_STUDIJNE_POZNAMKY_SK.md") if "_raw" not in p.parts
    )
    standalone = [
        p
        for p in sorted(archive.rglob("*.md"))
        if p.name != "03_STUDIJNE_POZNAMKY_SK.md"
        and "_raw" not in p.parts
        and "00_PROJEKT" not in p.parts
        and p.name != "README.md"
        and p.with_suffix(".pdf").exists()
    ]
    return modules, standalone


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive", required=True, type=Path)
    ap.add_argument("--only", default="", help="filtruj podľa cesty, napr. 04_TIPY_A_TRIKY")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--chrome", default="")
    ap.add_argument("--keep-html", action="store_true", help="ulož aj HTML vedľa PDF")
    args = ap.parse_args()

    archive = args.archive.resolve()
    if not archive.is_dir():
        raise SystemExit(f"Archív neexistuje: {archive}")

    modules, standalone = collect(archive)
    jobs: list[tuple[str, Path]] = [("module", m) for m in modules]
    jobs += [("standalone", s) for s in standalone]
    if args.only:
        jobs = [j for j in jobs if args.only in str(j[1])]
    if args.limit:
        jobs = jobs[: args.limit]

    from playwright.sync_api import sync_playwright

    ok = fail = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=args.chrome or chrome_path(),
            args=["--no-sandbox", "--font-render-hinting=none"],
        )
        page = browser.new_page()
        page.emulate_media(media="print")

        # Podklad: plnoplošná tmavá strana s gridom. Chromium pozadie do okrajov
        # strany nevykreslí, takže ho vyrobíme zvlášť a zlúčime pod obsah.
        page.set_content(
            (STYLE_DIR / "pozadie.html").read_text(encoding="utf-8"), wait_until="load"
        )
        backdrop = page.pdf(format="A4", print_background=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})

        def emit(html: str, out: Path) -> None:
            out.parent.mkdir(parents=True, exist_ok=True)
            if args.keep_html:
                out.with_suffix(".html").write_text(html, encoding="utf-8")
            page.set_content(html, wait_until="load")
            content = page.pdf(
                format="A4",
                print_background=True,
                display_header_footer=True,
                header_template=HEADER_TPL.replace("__ZNACKA__", ZNACKA).replace("__KIT__", KIT),
                footer_template=FOOTER_TPL.replace("__AUTOR__", AUTOR),
                margin={"top": "18mm", "bottom": "16mm", "left": "15mm", "right": "15mm"},
            )
            out.write_bytes(compose(content, backdrop))

        for kind, src in jobs:
            try:
                if kind == "module":
                    emit(module_doc(src, archive), src.parent / "PDF" / f"{src.parent.name}.pdf")
                else:
                    emit(standalone_doc(src, archive), src.with_suffix(".pdf"))
                ok += 1
                if ok % 25 == 0:
                    print(f"  … {ok}/{len(jobs)}", flush=True)
            except Exception as e:  # noqa: BLE001
                fail += 1
                print(f"CHYBA {src}: {e}", file=sys.stderr, flush=True)

        if not args.only and not args.limit:
            emit(contents_doc(archive, modules), archive / "00_OBSAH_ARCHIVU.pdf")
            ok += 1

        browser.close()

    print(f"Hotovo: {ok} PDF, {fail} chýb.")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
