#!/usr/bin/env bash
# Master build -- run the three steps in order to regenerate everything:
#
#   1. generate_figures.sh    notebooks -> figures (PDF + SVG) in NN_figures/
#   2. export_pdfs.sh         PowerPoint -> 01_Lectures/<name>.pdf
#   3. upscale_images_pdf.sh  figures made lossless, in place
#
# Each step is also runnable on its own (see the files next to this one).
#
# Usage:  bash 02_lectures_code/scripts/build_all.sh
#
# Requirements:
#   step 1: Jupyter + the notebook stack (pandas, matplotlib, scikit-learn, ...)
#   step 3: pip install pypdf svglib pymupdf pillow numpy

HERE="$(cd "$(dirname "$0")" && pwd)"

bash "$HERE/generate_figures.sh"
bash "$HERE/export_pdfs.sh"
bash "$HERE/upscale_images_pdf.sh"

echo "======================================="
echo "build_all done. Publish 01_Lectures/*.pdf."
