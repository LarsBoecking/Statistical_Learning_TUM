#!/usr/bin/env python3
"""Restore lossless vector figures in a PowerPoint-exported lecture PDF.

PowerPoint for Mac rasterises SVG figures when it saves a PDF, softening them.
This tool takes the deck (``.pptx``) and that exported PDF, and stamps every
SVG-embedded figure back on top as true vector, at its exact frame position.
Everything else PowerPoint rendered -- text, boxes, animation final states --
is left untouched, because the deck already resolved it.

Each embedded figure is identified against the source figures in
``02_lectures_code/**_figures/`` in two ways:

1. by content hash (exact byte match) -- for figures inserted via
   Insert / Change Picture from file, which PowerPoint stores verbatim; then
2. by rendered appearance -- for figures PowerPoint re-encoded on insert
   (e.g. drag-and-drop from Finder), whose bytes differ but whose drawing is
   identical. Same-size candidates are rasterised and the closest match wins.

Either way the matching source ``.pdf`` (vector) is stamped and the figure is
named in the report as ``lecture / slide N / figure``. Only if a figure matches
nothing is it rebuilt from its own embedded SVG and reported as ``unnamed``.

Only top-level pictures stored with an ``svgBlip`` are considered; raster
pictures and small grouped icons are left alone. Slides map to pages in order,
skipping hidden slides.

Usage
-----
    python overlay_vector_figures.py deck.pptx exported.pdf out.pdf

Dependencies: ``pypdf`` (required). For naming/rebuilding re-encoded figures:
``svglib``, ``pymupdf``, ``Pillow``, ``numpy`` (recommended). All pure-Python
wheels -- no cairo / native build tools. Install::

    pip install pypdf svglib pymupdf pillow numpy
"""
from __future__ import annotations

import glob
import hashlib
import os
import re
import sys
import tempfile
import zipfile
from typing import Iterator, Optional
from xml.dom import minidom

EMU = 914400.0
_CODE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _lazy_pypdf():
    try:
        from pypdf import PdfReader, PdfWriter, Transformation
    except Exception as exc:  # pragma: no cover
        sys.exit(f"Missing dependency: {exc}\nInstall with:  pip install pypdf")
    return PdfReader, PdfWriter, Transformation


def _import_fitz():
    """Return the PyMuPDF module (``pymupdf`` or legacy ``fitz``), or None."""
    try:
        import pymupdf
        return pymupdf
    except Exception:
        try:
            import fitz
            return fitz
        except Exception:
            return None


# ----------------------------------------------------------------------------
# SVG -> vector PDF (svglib/reportlab renderPDF -- pure Python, works on macOS)
# ----------------------------------------------------------------------------
def _svg_to_pdf(svg_bytes: bytes, out_path: str) -> bool:
    """Convert a figure's embedded SVG to a vector PDF. Returns True on success."""
    try:
        from svglib.svglib import svg2rlg
        from reportlab.graphics import renderPDF
    except Exception:
        return False
    tmp_svg = out_path + ".svg"
    try:
        with open(tmp_svg, "wb") as f:
            f.write(svg_bytes)
        drawing = svg2rlg(tmp_svg)
        if drawing is None:
            return False
        renderPDF.drawToFile(drawing, out_path)
        return True
    except Exception:
        return False
    finally:
        try:
            os.remove(tmp_svg)
        except OSError:
            pass


# ----------------------------------------------------------------------------
# Rasterisation for appearance matching (PyMuPDF -- reliable on macOS arm64)
# ----------------------------------------------------------------------------
def _pdf_to_thumb(pdf_path: str, px: int = 110):
    """Rasterise page 1 of a PDF to a px*px grayscale numpy array, or None."""
    fitz = _import_fitz()
    if fitz is None:
        return None
    try:
        import numpy as np
        from PIL import Image
        doc = fitz.open(pdf_path)
        page = doc[0]
        z = px / max(page.rect.width, page.rect.height, 1)
        pix = page.get_pixmap(matrix=fitz.Matrix(z, z),
                              colorspace=fitz.csGRAY, alpha=False)
        im = Image.frombytes("L", [pix.width, pix.height], pix.samples).resize((px, px))
        doc.close()
        return np.asarray(im, dtype=float)
    except Exception:
        return None


def _svg_dims_pt(data: bytes) -> Optional[tuple[float, float]]:
    """Drawing size in points from an SVG header (width/height or viewBox)."""
    s = data[:3000].decode("utf-8", "ignore")
    w = re.search(r'width="([\d.]+)pt"', s)
    h = re.search(r'height="([\d.]+)pt"', s)
    if w and h:
        return (round(float(w[1]), 1), round(float(h[1]), 1))
    vb = re.search(r'viewBox="[\d.\-]+ [\d.\-]+ ([\d.]+) ([\d.]+)"', s)
    if vb:
        return (round(float(vb[1]), 1), round(float(vb[2]), 1))
    return None


def _pretty_label(src_svg: str) -> str:
    """Turn a source path into a readable name, e.g. 'Figure 6.7: loss surface'.

    ``.../6.7_loss_surface/6.7_loss_surface.svg``        -> 'Figure 6.7: loss surface'
    ``.../1.3_binning/1.3_binning_bins30.svg``           -> 'Figure 1.3: binning (bins30)'
    """
    folder = os.path.basename(os.path.dirname(src_svg))          # 6.7_loss_surface
    stem = os.path.splitext(os.path.basename(src_svg))[0]        # 6.7_loss_surface[_var]
    m = re.match(r"(\d+\.\d+)_(.*)", folder)
    if not m:
        return os.path.relpath(src_svg, _CODE_ROOT)
    number, name = m.group(1), m.group(2).replace("_", " ")
    variant = stem[len(folder) + 1:].replace("_", " ") if stem.startswith(folder + "_") else ""
    return f"Figure {number}: {name}" + (f" ({variant})" if variant else "")


def build_figure_index(code_root: str = _CODE_ROOT) -> dict[str, str]:
    """Map md5(svg bytes) -> absolute path of the source ``.svg`` for every figure."""
    idx: dict[str, str] = {}
    for f in glob.glob(os.path.join(code_root, "0*_figures", "**", "*.svg"),
                        recursive=True):
        try:
            idx[hashlib.md5(open(f, "rb").read()).hexdigest()] = os.path.abspath(f)
        except OSError:
            pass
    return idx


class _Identifier:
    """Name a re-encoded figure by rasterising it and the same-size sources."""

    def __init__(self, source_svgs: list[str]):
        self.sources = []
        for svg in source_svgs:
            pdf = os.path.splitext(svg)[0] + ".pdf"
            if os.path.exists(pdf):
                try:
                    dims = _svg_dims_pt(open(svg, "rb").read(3000))
                except OSError:
                    dims = None
                self.sources.append((svg, pdf, dims))
        self._thumbs: dict[str, object] = {}

    def identify(self, svg_bytes: bytes) -> Optional[str]:
        try:
            import numpy as np
        except Exception:
            return None
        emb_pdf = tempfile.mktemp(suffix=".pdf")
        try:
            if not _svg_to_pdf(svg_bytes, emb_pdf):
                return None
            te = _pdf_to_thumb(emb_pdf)
        finally:
            try:
                os.remove(emb_pdf)
            except OSError:
                pass
        if te is None:
            return None
        dims = _svg_dims_pt(svg_bytes)
        cands = [(s, p) for s, p, dd in self.sources
                 if dims and dd and abs(dd[0] - dims[0]) <= 1.0
                 and abs(dd[1] - dims[1]) <= 1.0] \
            or [(s, p) for s, p, _ in self.sources]
        scored = []
        for svg, pdf in cands:
            tc = self._thumbs.get(pdf)
            if tc is None:
                tc = _pdf_to_thumb(pdf)
                self._thumbs[pdf] = tc
            if tc is None:
                continue
            scored.append((float(np.mean((te - tc) ** 2)), svg))
        if not scored:
            return None
        scored.sort()
        best_mse = scored[0][0]
        # An exact figure renders at ~10-15; the nearest *different* figure (or a
        # different animation frame) is >=~200, and an unrelated graphic is many
        # hundreds. So a low absolute error means a confident match. No relative
        # rule -- it wrongly rejects when two source files are the same frame
        # (e.g. ``6.7_loss_surface`` and its ``rotation_00`` are byte-identical).
        if best_mse >= 120:
            return None
        # Among byte-identical near-ties, prefer the canonical (no-variant) file
        # so the report reads 'loss surface', not 'loss surface (rotation 00)'.
        near = [s for mse, s in scored if mse <= best_mse + 1.0]

        def _rank(p: str):
            folder = os.path.basename(os.path.dirname(p))
            stem = os.path.splitext(os.path.basename(p))[0]
            return (0 if stem == folder else 1, len(stem))

        return min(near, key=_rank)


def _slide_order(z: zipfile.ZipFile) -> list[str]:
    """Return slide part names in presentation order, skipping hidden slides."""
    pres = z.read("ppt/presentation.xml").decode()
    rels = z.read("ppt/_rels/presentation.xml.rels").decode()
    id2t = dict(re.findall(r'Id="([^"]+)"[^>]*Target="([^"]+)"', rels))
    order = []
    for sm in re.finditer(r"<p:sldId\b([^>]*)/>", pres):
        attrs = sm.group(1)
        if re.search(r'show="0"', attrs):        # hidden slide: not exported
            continue
        rid = re.search(r'r:id="([^"]+)"', attrs)
        tgt = id2t.get(rid.group(1), "") if rid else ""
        if tgt:
            order.append("ppt/" + tgt.lstrip("/").replace("../", ""))
    return order


def _figures_on_slide(z: zipfile.ZipFile, slide_part: str, min_in: float = 1.5
                      ) -> Iterator[tuple[bytes, int, int, int, int]]:
    """Yield (svg_bytes, off_x, off_y, ext_cx, ext_cy) for each top-level SVG figure."""
    rels_part = slide_part.replace("slides/", "slides/_rels/") + ".rels"
    rid2tgt = dict(re.findall(r'Id="([^"]+)"[^>]*Target="([^"]+)"',
                              z.read(rels_part).decode()))
    doc = minidom.parseString(z.read(slide_part))
    trees = doc.getElementsByTagName("p:spTree")
    if not trees:
        return
    for pic in trees[0].childNodes:                # direct children only
        if getattr(pic, "tagName", None) != "p:pic":
            continue
        svg = pic.getElementsByTagName("asvg:svgBlip")
        xfrm = pic.getElementsByTagName("a:xfrm")
        if not (svg and xfrm):
            continue
        off = xfrm[0].getElementsByTagName("a:off")
        ext = xfrm[0].getElementsByTagName("a:ext")
        if not (off and ext):
            continue
        tgt = rid2tgt.get(svg[0].getAttribute("r:embed"), "")
        if not tgt:
            continue
        cx, cy = int(ext[0].getAttribute("cx")), int(ext[0].getAttribute("cy"))
        if cx / EMU < min_in and cy / EMU < min_in:
            continue                                   # decorative icon
        ox, oy = int(off[0].getAttribute("x")), int(off[0].getAttribute("y"))
        media = "ppt/" + tgt.lstrip("/").replace("../", "")
        yield (z.read(media), ox, oy, cx, cy)


def overlay(pptx_path: str, pdf_path: str, out_path: str,
            figindex: Optional[dict[str, str]] = None,
            verbose: bool = True) -> list[tuple[int, str]]:
    """Stamp vector figures onto the exported PDF.

    Returns a list of ``(slide_number, figure_label)`` for each replacement.
    """
    PdfReader, PdfWriter, Transformation = _lazy_pypdf()
    if figindex is None:
        figindex = build_figure_index()
    identifier = _Identifier(sorted(set(figindex.values())))
    lecture = os.path.splitext(os.path.basename(pptx_path))[0]

    z = zipfile.ZipFile(pptx_path)
    pres = z.read("ppt/presentation.xml").decode()
    m = re.search(r'<p:sldSz cx="(\d+)" cy="(\d+)"', pres)
    slide_w_in, slide_h_in = int(m[1]) / EMU, int(m[2]) / EMU

    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    writer.append(reader)
    slides = _slide_order(z)
    if len(slides) != len(writer.pages) and verbose:
        print(f"  ! note: {len(slides)} visible slides but "
              f"{len(writer.pages)} PDF pages -- check for hidden slides")

    report: list[tuple[int, str]] = []
    skipped = 0
    for page_idx, slide_part in enumerate(slides):
        if page_idx >= len(writer.pages):
            break
        page = writer.pages[page_idx]
        pw, ph = float(page.mediabox.width), float(page.mediabox.height)
        sx, sy = pw / (slide_w_in * 72), ph / (slide_h_in * 72)
        for i, (svg, ox, oy, cx, cy) in enumerate(_figures_on_slide(z, slide_part)):
            # 1) exact byte match, then 2) match by rendered appearance
            src_svg = figindex.get(hashlib.md5(svg).hexdigest()) \
                or identifier.identify(svg)
            src_pdf = os.path.splitext(src_svg)[0] + ".pdf" if src_svg else None
            if src_pdf and os.path.exists(src_pdf):
                fig_pdf, label = src_pdf, _pretty_label(src_svg)
            else:
                fig_pdf = f"/tmp/_ovl_embed_{page_idx}_{i}.pdf"
                if _svg_to_pdf(svg, fig_pdf):
                    label = "unnamed (embedded SVG; not found in figure folders)"
                else:
                    skipped += 1
                    if verbose:
                        print(f"  {lecture} / slide {page_idx + 1:>2} / "
                              f"SKIPPED (install svglib pymupdf pillow numpy)")
                    continue
            fig = PdfReader(fig_pdf).pages[0]
            fw, fh = float(fig.mediabox.width), float(fig.mediabox.height)
            x = ox / EMU * 72 * sx
            w = cx / EMU * 72 * sx
            h = cy / EMU * 72 * sy
            y = ph - (oy / EMU * 72 * sy) - h
            page.merge_transformed_page(
                fig, Transformation().scale(w / fw, h / fh).translate(x, y))
            report.append((page_idx + 1, label))
            if verbose:
                print(f"  {lecture} / slide {page_idx + 1:>2} / {label}")

    with open(out_path, "wb") as f:
        writer.write(f)
    if verbose:
        extra = f" ({skipped} skipped)" if skipped else ""
        print(f"  -> {len(report)} figure(s) replaced{extra}, "
              f"wrote {os.path.basename(out_path)}")
    return report


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("usage: python overlay_vector_figures.py deck.pptx exported.pdf out.pdf")
    overlay(sys.argv[1], sys.argv[2], sys.argv[3])
