#!/usr/bin/env bash
# Step 3/3 -- replace the softened figures in each exported PDF with their
# lossless vector originals, in place. Overwrites 01_Lectures/<name>.pdf.
#
# Run export_pdfs.sh first (or export from PowerPoint by hand). Re-export a deck
# before re-running this on it, otherwise the figures get stamped twice.
#
# Usage:  bash 02_lectures_code/scripts/upscale_images_pdf.sh
# Deps:   pip install pypdf svglib pymupdf pillow numpy

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
LEC="$REPO/01_Lectures"
TOOL="$HERE/overlay_vector_figures.py"

shopt -s nullglob
for pptx in "$LEC"/*.pptx; do
  base="$(basename "$pptx" .pptx)"
  [[ "$base" == ~\$* || "$base" == .* ]] && continue   # PowerPoint lock/temp
  pdf="$LEC/$base.pdf"
  tmp="$LEC/.$base.overlay.tmp.pdf"
  echo "================ $base ================"
  if [[ ! -f "$pdf" ]]; then
    echo "  skip: no $base.pdf (export it first)"
    continue
  fi
  if python3 "$TOOL" "$pptx" "$pdf" "$tmp" 2> >(grep -v "Ignoring wrong pointing" >&2); then
    cp -f "$tmp" "$pdf" && rm -f "$tmp"
  else
    rm -f "$tmp"
    echo "  FAILED on $base (see message above)"
  fi
done
echo "Done. 01_Lectures/*.pdf are now lossless."
