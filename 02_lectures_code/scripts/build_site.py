#!/usr/bin/env python3
"""Step 4/4 -- refresh the GitHub Pages site (docs/) from the lecture material.

For every lecture page ``docs/lectures/<NN>-<slug>.html`` this script

1. renders the exported deck ``01_Lectures/<NN>_*.pdf`` page by page into
   ``docs/slides/<NN>/p-XX.svg`` (stale pages are removed) and sets ``PAGES``
   in the page script to the slide count;
2. reads the PowerPoint *sections* from ``01_Lectures/<NN>_*.pptx`` and writes
   them as the ``SUBS`` subchapter list (section name, first slide), so the
   subchapter navigation follows the deck itself;
3. renders one representative PNG per figure folder in
   ``02_lectures_code/<NN>_figures/`` into ``docs/assets/img/gallery/`` and
   rewrites the "Figures from the lecture" block of the page;
4. bumps the ``?v=`` cache-buster on every slide image on the site.

Anything that is missing is skipped with a note (a deck without PDF keeps its
old slide SVGs and takes PAGES from the .pptx; a deck without sections keeps
the SUBS already in the HTML), so the script can run on a partial build.

Usage:  python3 02_lectures_code/scripts/build_site.py [--lecture NN] [--no-slides] [--no-gallery]
Deps:   pip install pymupdf
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import os
import re
import shutil
import sys
import zipfile
from xml.etree import ElementTree as ET

import fitz  # pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
LECTURES = os.path.join(REPO, "01_Lectures")
CODE = os.path.join(REPO, "02_lectures_code")
DOCS = os.path.join(REPO, "docs")
GALLERY = os.path.join(DOCS, "assets", "img", "gallery")
GALLERY_DPI = 150

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "p14": "http://schemas.microsoft.com/office/powerpoint/2010/main",
}


# --------------------------------------------------------------------------- helpers
def find_one(pattern: str) -> str | None:
    """Return the single file matching ``pattern`` (ignoring PowerPoint lock files)."""
    hits = [p for p in sorted(glob.glob(pattern)) if not os.path.basename(p).startswith("~$")]
    return hits[0] if hits else None


def natural_key(s: str) -> list:
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", s)]


def pptx_sections(pptx: str) -> tuple[int, list[tuple[str, int]]]:
    """Return (slide count, [(section name, first slide number), ...]) of a deck."""
    z = zipfile.ZipFile(pptx)
    pres = ET.fromstring(z.read("ppt/presentation.xml"))
    ids = [s.get("id") for s in pres.find("p:sldIdLst", NS)]
    order = {sid: i + 1 for i, sid in enumerate(ids)}
    subs: list[tuple[str, int]] = []
    for lst in pres.iter("{%s}sectionLst" % NS["p14"]):
        for sec in lst:
            members = [order[s.get("id")] for s in sec.iter("{%s}sldId" % NS["p14"]) if s.get("id") in order]
            if not members:
                continue  # empty section (e.g. a "Wrap up" placeholder)
            name = (sec.get("name") or "").splitlines()[0].strip()
            if name.lower() in ("default section", ""):
                name = "Introduction"
            subs.append((name, min(members)))
    return len(ids), subs


def js_subs(subs: list[tuple[str, int]]) -> str:
    return "[" + ", ".join('["%s", %d]' % (n.replace('"', '\\"'), p) for n, p in subs) + "]"


# --------------------------------------------------------------------------- steps
def build_slides(nn: str, pdf: str) -> int:
    """Render every PDF page to docs/slides/<nn>/p-XX.svg; return the page count."""
    out = os.path.join(DOCS, "slides", nn)
    os.makedirs(out, exist_ok=True)
    doc = fitz.open(pdf)
    for i, page in enumerate(doc, 1):
        with open(os.path.join(out, f"p-{i:02d}.svg"), "w", encoding="utf-8") as f:
            f.write(page.get_svg_image(text_as_path=True))
    n = doc.page_count
    for stale in glob.glob(os.path.join(out, "p-*.svg")):
        if int(re.search(r"p-(\d+)\.svg$", stale).group(1)) > n:
            os.remove(stale)
    print(f"  slides : {n} pages -> docs/slides/{nn}/")
    return n


def representative(folder: str) -> str | None:
    """Pick the file that stands for a figure folder: its GIF, the unsuffixed PDF, else the last PDF."""
    gifs = sorted(glob.glob(os.path.join(folder, "*.gif")))
    if gifs:
        return gifs[0]
    pdfs = sorted(glob.glob(os.path.join(folder, "*.pdf")), key=natural_key)
    if not pdfs:
        return None
    plain = os.path.join(folder, os.path.basename(folder) + ".pdf")
    return plain if plain in pdfs else pdfs[-1]


def build_gallery(nn: str) -> list[tuple[str, str, str]]:
    """Render one image per figure folder; return [(fig id, label, gallery file name), ...]."""
    os.makedirs(GALLERY, exist_ok=True)
    folders = sorted(glob.glob(os.path.join(CODE, f"{nn}_figures", "*_*")), key=natural_key)
    for stale in glob.glob(os.path.join(GALLERY, f"{nn}__*")):
        os.remove(stale)
    entries = []
    for folder in folders:
        slug = os.path.basename(folder)                     # e.g. 3.10_constraint_geometry
        m = re.match(r"(\d+\.\d+)_(.+)", slug)
        if not m:
            continue
        src = representative(folder)
        if src is None:
            print(f"  gallery: no PDF/GIF in {slug}, skipped")
            continue
        fig_id, label = m.group(1), m.group(2).replace("_", " ")
        if src.endswith(".gif"):
            name = f"{nn}__{slug}.gif"
            shutil.copyfile(src, os.path.join(GALLERY, name))
        else:
            name = f"{nn}__{slug}.png"
            fitz.open(src)[0].get_pixmap(dpi=GALLERY_DPI, alpha=False).save(os.path.join(GALLERY, name))
        entries.append((fig_id, label, name))
    print(f"  gallery: {len(entries)} figures -> docs/assets/img/gallery/{nn}__*")
    return entries


def figrow_html(entries: list[tuple[str, str, str]]) -> str:
    lines = []
    for fig_id, label, name in entries:
        lines.append(
            f'      <figure><img src="../assets/img/gallery/{name}" alt="{label}" loading="lazy">'
            f"<figcaption>Fig. {fig_id} &middot; {label}</figcaption></figure>"
        )
    return "\n".join(lines)


def update_page(path: str, nn: str, pages: int | None, subs: list[tuple[str, int]] | None,
                entries: list[tuple[str, str, str]] | None, version: str) -> None:
    html = open(path, encoding="utf-8").read()
    m = re.search(r'var NN="(\d+)", PAGES=(\d+), SUBS=(\[.*?\]), pad=', html)
    if not m:
        sys.exit(f"{path}: cannot find the 'var NN=..., PAGES=..., SUBS=...' line")
    new_pages = pages if pages is not None else int(m.group(2))
    new_subs = js_subs(subs) if subs else m.group(3)
    html = html[: m.start()] + f'var NN="{nn}", PAGES={new_pages}, SUBS={new_subs}, pad=' + html[m.end():]
    if entries is not None:
        html, n = re.subn(r'(<div class="figrow">\n).*?(\n    </div>)', lambda mm: mm.group(1) + figrow_html(entries) + mm.group(2), html, count=1, flags=re.S)
        if n != 1:
            sys.exit(f"{path}: cannot find the <div class=\"figrow\"> block")
    html = re.sub(r"\.svg\?v=\d+", f".svg?v={version}", html)
    open(path, "w", encoding="utf-8").write(html)
    print(f"  page   : PAGES={new_pages}, SUBS={new_subs}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lecture", help="only this lecture number, e.g. 03")
    ap.add_argument("--no-slides", action="store_true", help="skip rendering slide SVGs from the PDFs")
    ap.add_argument("--no-gallery", action="store_true", help="skip rendering the figure gallery")
    args = ap.parse_args()
    version = dt.date.today().strftime("%Y%m%d")

    pages = sorted(glob.glob(os.path.join(DOCS, "lectures", "[0-9][0-9]-*.html")))
    for page in pages:
        nn = os.path.basename(page)[:2]
        if args.lecture and nn != args.lecture:
            continue
        print(f"================ Lecture {nn} ================")
        pdf = find_one(os.path.join(LECTURES, f"{nn}_*.pdf"))
        pptx = find_one(os.path.join(LECTURES, f"{nn}_*.pptx"))
        n_pages, subs = None, None
        if pptx:
            n_pages, subs = pptx_sections(pptx)
            if not subs:
                print("  subs   : deck has no PowerPoint sections, keeping the SUBS in the HTML")
        else:
            print("  deck   : no .pptx found, keeping PAGES/SUBS in the HTML")
        if not args.no_slides:
            if pdf:
                n_pages = build_slides(nn, pdf)
            else:
                print(f"  slides : no 01_Lectures/{nn}_*.pdf (run export_pdfs.sh), keeping the old SVGs")
        entries = None if args.no_gallery else build_gallery(nn)
        update_page(page, nn, n_pages, subs, entries, version)

    index = os.path.join(DOCS, "index.html")
    html = open(index, encoding="utf-8").read()
    open(index, "w", encoding="utf-8").write(re.sub(r"\.svg\?v=\d+", f".svg?v={version}", html))
    print("Done. Review `git status docs/` and commit.")


if __name__ == "__main__":
    main()
