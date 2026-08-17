#!/usr/bin/env bash
# Step 1/3 -- regenerate every lecture figure (PDF + SVG) from the notebooks.
#
# Executes 02_lectures_code/NN.ipynb; each save_figure() call writes into the
# matching NN_figures/ folder (which is not tracked in git). The tracked .ipynb
# files are left unchanged.
#
# Usage:  bash 02_lectures_code/scripts/generate_figures.sh
# Requires Jupyter + the notebook stack (pandas, matplotlib, scikit-learn, ...).

HERE="$(cd "$(dirname "$0")" && pwd)"
CODE="$(cd "$HERE/.." && pwd)"          # 02_lectures_code

if ! command -v jupyter >/dev/null 2>&1; then
  echo "Jupyter not found. Install it (pip install jupyter nbconvert) and retry."
  exit 1
fi

shopt -s nullglob
for nb in "$CODE"/0*.ipynb; do
  echo "================ $(basename "$nb") ================"
  # --execute runs the notebook (figures are written as a side effect); --stdout
  # discards the executed copy so the tracked notebook is not modified.
  if ! jupyter nbconvert --to notebook --execute --stdout "$nb" >/dev/null; then
    echo "  FAILED: $(basename "$nb") (see traceback above)"
  fi
done
echo "Done regenerating figures."
