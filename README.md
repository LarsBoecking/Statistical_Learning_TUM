# Statistical Learning

Course material for **Statistical Learning**, a master's course at the TUM School of Management
(Chair for Information Systems and Human-centric Artificial Intelligence, Prof. Dr. Niklas Kühl).
The content follows *An Introduction to Statistical Learning* (Hastie, Tibshirani et al.) and works
throughout on a real natural-disaster dataset.

A landing page walking through every lecture is published with GitHub Pages from the `docs/` folder.

## Repository layout

```
.
├── 01_Lectures/          Lecture slides. Only the exported PDFs are tracked; the .pptx sources stay local.
├── 02_lectures_code/     One notebook per lecture that regenerates all of its figures.
│   └── NN_figures/        Generated figure PDFs (imported into the slides), grouped per lecture.
├── 03_exercises_code/    One folder per session with the student exercise notebook.
│                          Worked *_Solution.ipynb notebooks are kept private (see .gitignore).
├── configs/              Shared Matplotlib style (visualisations.mplstyle).
├── data/                 The disaster dataset used across all notebooks.
├── docs/                 The GitHub Pages site (landing page + one page per lecture).
└── requirements.txt      Python dependencies.
```

## Getting started

```bash
git clone https://github.com/LarsBoecking/Statistical_Learning_TUM.git
cd Statistical_Learning_TUM

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Notebooks load the shared style and dataset with paths relative to their own location, so launch
Jupyter from the notebook's directory. Lecture figure notebooks in `02_lectures_code/` reference
`../configs` and `../data`; exercise notebooks in `03_exercises_code/NN/` reference `../../configs`
and `../../data`.

## Publishing the landing page

The site is a static, dependency-free set of HTML pages in `docs/`.

1. Push this repository to <https://github.com/LarsBoecking/Statistical_Learning_TUM>.
2. `docs/assets/js/config.js` is already set to `user: LarsBoecking`, `repo: Statistical_Learning_TUM`,
   `branch: main`. Every "View slides", "Open exercise", and "Figure notebook" link is built from these
   three values, so this is the only place to edit if the repository ever moves.
3. In the repository, go to **Settings → Pages**, set the source to **Deploy from a branch**, choose
   the `main` branch and the **`/docs`** folder, and save.
4. The site appears at <https://larsboecking.github.io/Statistical_Learning_TUM/>.

Because Pages serves only the `docs/` folder, slide PDFs and notebooks are linked back to the files in
the repository rather than copied into the site.

## What is and is not tracked

The `.gitignore` keeps the repository focused on shareable material:

- PowerPoint sources (`*.pptx`) are excluded; only the exported lecture PDFs are tracked.
- Exercise solutions (`*_Solution.ipynb`) are excluded so students receive only the blank exercises.
- Editor, OS, and Python caches are excluded.

The neural-network figure set (`02_lectures_code/06_figures/`) contains roughly 37 MB of frame-by-frame
animation PDFs that are fully reproducible from `06.ipynb`. A commented block at the bottom of
`.gitignore` lets you exclude those frames if you prefer a leaner repository.

## Slides on the site

`00_Intro` is used only with students attending in person and is intentionally left off the site.
All six lectures (01–06) are published with their slides and figures.

## Credits

Content developed by Lars Böcking. Chair for Information Systems and Human-centric
Artificial Intelligence (Prof. Dr. Niklas Kühl), TUM School of Management. Content follows
*An Introduction to Statistical Learning* by James, Witten, Hastie, and Tibshirani
(https://www.statlearning.com). Course page on Moodle:
https://www.moodle.tum.de/course/view.php?id=114373
