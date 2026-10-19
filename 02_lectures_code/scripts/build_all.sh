#!/usr/bin/env bash
# Master build -- run the four steps in order to regenerate everything:
#
#   1. generate_figures.sh    notebooks -> figures (PDF + SVG) in NN_figures/
#   2. export_pdfs.sh         PowerPoint -> 01_Lectures/<name>.pdf
#   3. upscale_images_pdf.sh  figures made lossless, in place
#   4. build_site.py          docs/ refreshed: slide SVGs, subchapters, figure gallery
#
# Each step is also runnable on its own (see the files next to this one).
#
# Usage:  bash 02_lectures_code/scripts/build_all.sh
#
# Requirements:
#   step 1: Jupyter + the notebook stack (pandas, matplotlib, scikit-learn, ...)
#   step 3: pip install pypdf svglib pymupdf pillow numpy
#   step 4: pip install pymupdf

HERE="$(cd "$(dirname "$0")" && pwd)"

bash "$HERE/generate_figures.sh"
bash "$HERE/export_pdfs.sh"
bash "$HERE/upscale_images_pdf.sh"
python3 "$HERE/build_site.py"

echo "======================================="
echo "build_all done. Commit 01_Lectures/*.pdf and docs/."
