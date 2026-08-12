"""Shared figure utilities for the Statistical Learning lecture notebooks.

Figures use paper-style numbering ``Fig. <lecture>.<number>``. Each figure is
saved as a loss-free PDF into a per-figure folder::

    <code_root>/<LL>_figures/<L.N>_<name>/<L.N>_<name>[_<variant>].pdf

``<code_root>`` is the ``02_lectures_code`` directory, i.e. the parent of the
``src`` folder that holds this module. Numbering is independent of slide order,
so figures keep their identity when slides move.

A single figure number may hold several PDFs, for example the frames of an
animation or a parameter sweep. Pass a distinct ``variant`` for each frame; all
frames land in the same ``<L.N>_<name>`` folder.

Example
-------
>>> import matplotlib.pyplot as plt
>>> plt.plot([0, 1], [0, 1])           # doctest: +SKIP
>>> save_figure(1, 1, "damage_scatter")  # doctest: +SKIP
Saved Fig. 1.1 -> 01_figures/1.1_damage_scatter/1.1_damage_scatter.pdf
>>> for k in range(3):                    # animation frames  # doctest: +SKIP
...     plt.plot([0, k], [0, 1])
...     save_figure(6, 15, "momentum_2d", variant=f"step_{k:02d}")
"""

from __future__ import annotations

import os
import re
from typing import Optional

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

# Root of the lecture-code tree (parent of this src/ folder).
CODE_ROOT: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Folder holding the shared matplotlib style.
_STYLE_PATH: str = os.path.join(CODE_ROOT, "configs", "visualisations.mplstyle")
__all__ = ["save_figure", "figure_path", "figure_dir", "use_style", "CODE_ROOT"]

# palette (tableau-colorblind, shared across lectures)
BLUE="#006BA4"; ORANGE="#FF800E"; GRAY="#ABABAB"; DARK="#595959"; GREEN="#2C8A3B"; RED="#C0392B"
DIS_COL={"Earthquake":"#C0392B","Flood":"#2C6FA6","Storm":"#27AE60","Volcanic activity":"#E67E22"}


def use_style() -> None:
    """Apply the shared matplotlib style used across all lectures."""
    if os.path.exists(_STYLE_PATH):
        plt.style.use(_STYLE_PATH)


def _slugify(text: str) -> str:
    """Return a filesystem-safe slug.

    Spaces collapse to underscores and any character outside ``[A-Za-z0-9._-]``
    is dropped. This keeps variant strings (which may contain column names such
    as ``"Total Damages (US$)"``) readable and portable.
    """
    text = str(text).strip().replace(" ", "_")
    text = re.sub(r"[^A-Za-z0-9._-]", "", text)
    return re.sub(r"_+", "_", text).strip("_")


def figure_dir(lecture: int, number: int, name: str) -> str:
    """Return (creating if needed) the folder for figure ``Fig. lecture.number``.

    Args:
        lecture: Lecture index, e.g. ``1`` for lecture 01.
        number: Figure index within the lecture, e.g. ``3`` for ``Fig. 1.3``.
        name: Short descriptive slug for the figure, e.g. ``"binning"``.

    Returns:
        Absolute path to ``<LL>_figures/<L.N>_<name>/``.
    """
    slug = f"{lecture}.{number}_{_slugify(name)}"
    folder = os.path.join(CODE_ROOT, f"{lecture:02d}_figures", slug)
    os.makedirs(folder, exist_ok=True)
    return folder


def figure_path(
    lecture: int,
    number: int,
    name: str,
    variant: Optional[str] = None,
    ext: str = "pdf",
) -> str:
    """Return the full output path for a figure, creating its folder.

    Use this when a caller writes the file itself rather than through
    ``Figure.savefig`` (e.g. saving a Matplotlib animation as a GIF)::

        anim.save(figure_path(3, 2, "ols_fit", variant="regression", ext="gif"),
                  writer=PillowWriter(fps=8))

    Args:
        lecture: Lecture index, e.g. ``3``.
        number: Figure index within the lecture, e.g. ``2``.
        name: Short descriptive slug, e.g. ``"ols_fit"``.
        variant: Optional suffix for one figure with several files.
        ext: File extension without the dot. Defaults to ``"pdf"``.

    Returns:
        Absolute path ``<LL>_figures/<L.N>_<name>/<L.N>_<name>[_<variant>].<ext>``.
    """
    folder = figure_dir(lecture, number, name)
    stem = os.path.basename(folder)
    fname = stem if variant is None else f"{stem}_{_slugify(variant)}"
    return os.path.join(folder, f"{fname}.{ext}")


def save_figure(
    lecture: int,
    number: int,
    name: str,
    variant: Optional[str] = None,
    *,
    fig: Optional[Figure] = None,
    ext: str = "pdf",
    close: bool = False,
    verbose: bool = True,
    **savefig_kwargs,
) -> str:
    """Save a lecture figure using paper-style numbering.

    The figure is written to
    ``<LL>_figures/<L.N>_<name>/<L.N>_<name>[_<variant>].<ext>``. ``bbox_inches``
    defaults to ``"tight"`` and can be overridden through ``savefig_kwargs``.

    Args:
        lecture: Lecture index, e.g. ``1`` for lecture 01.
        number: Figure index within the lecture, e.g. ``3`` for ``Fig. 1.3``.
        name: Short descriptive slug for the figure, e.g. ``"binning"``.
        variant: Optional suffix for a single figure with several PDFs, such as
            animation frames (``"step_03"``) or a parameter sweep (``"bins5"``).
        fig: Figure to save. Defaults to the current figure (``plt.gcf()``).
        ext: File extension without the dot. Defaults to ``"pdf"``.
        close: Close the figure after saving. Useful when a cell generates many
            frames in a loop.
        verbose: Print the saved path.
        **savefig_kwargs: Extra keyword arguments forwarded to
            ``Figure.savefig`` (e.g. ``dpi=140``).

    Returns:
        Absolute path of the written file.
    """
    fig = fig if fig is not None else plt.gcf()
    path = figure_path(lecture, number, name, variant, ext)

    savefig_kwargs.setdefault("bbox_inches", "tight")
    fig.savefig(path, **savefig_kwargs)
    if close:
        plt.close(fig)
    if verbose:
        rel = os.path.relpath(path, CODE_ROOT)
        print(f"Saved Fig. {lecture}.{number} -> {rel}")
    return path
