#!/usr/bin/env bash
# Step 2/3 -- export each deck to PDF via the real PowerPoint app (macOS), so
# animations, builds, and layout render exactly as in the presentation.
#
# Writes 01_Lectures/<name>.pdf with the figures still softened; run
# upscale_images_pdf.sh next to make them lossless.
#
# Usage:  bash 02_lectures_code/scripts/export_pdfs.sh
# The first run prompts once to let your terminal control PowerPoint.

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
LEC="$REPO/01_Lectures"
OSA="$HERE/export_pptx_to_pdf.applescript"

shopt -s nullglob
for pptx in "$LEC"/*.pptx; do
  base="$(basename "$pptx" .pptx)"
  [[ "$base" == ~\$* || "$base" == .* ]] && continue   # PowerPoint lock/temp
  echo "================ $base ================"
  err="$(osascript "$OSA" "$pptx" "$LEC/$base.pdf" 2>&1 >/dev/null)"
  if [[ -n "$err" || ! -f "$LEC/$base.pdf" ]]; then
    echo "  export FAILED: ${err:-no PDF produced}"
  else
    echo "  wrote $base.pdf"
  fi
done
echo "Done exporting PDFs."
