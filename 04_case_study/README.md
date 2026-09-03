# ***A Data-Driven Study of Delay Patterns and Cancellation Risks in the German Rail System***
## **<span style="color:royalblue">Final case study</span>**
### Applied AI Course

**Lecturer**: Prof. Niklas Kühl  
**Supervisors**: Lars Böcking
**Submission Date**: 31st of January 23:59

#### Please submit your final work as a .zip file via email to [lars.boecking@tum.de](mailto:lars.boecking@tum.de).

**Summarize Findings**
- Create onepager reports in PDF format for each task. Please use the latex template *submission.tex* in the repository.
- Incorporate relevant visualizations, charts, and data tables to support your conclusions.

**Submission Requirements**
- A structured 3-page PDF report summarizing your findings and methodological choices across all tasks.
- All supporting analysis, visualisations and experiments must be provided in well-organised Jupyter notebooks.
- The setup must be fully specified:
  - All Python packages required to execute the notebooks must be listed in a requirements.txt file.
  - Any randomness in data splitting, model training or evaluation must be controlled by explicitly fixed random seeds.
  - The README.md must contain clear, step-by-step instructions on how to set up the environment and reproduce your results.

---
**Setup for Working with LaTeX in VS Code**
- Download and Install TeX Live:
    - Go to the [TeX Live website](https://www.tug.org/texlive/).
    - Download the installer for your operating system.
    - Follow the installation instructions provided on the website.
- Install LaTeX Workshop Extension in VS Code:
    - Open VS Code.
    - Go to the Extensions view by clicking on the Extensions icon in the Activity Bar on the side of the window or by pressing `Ctrl+Shift+X`.
    - Search for LaTeX Workshop.
    - Click `Install` to install the extension.
- Open `submission/submission.tex` to start working on your submission .tex file
- By clicking on `View Latex PDF file` you create the formatted .pdf file, which will appear here: `submission/submission.pdf`.


---
## Background:

This case study examines delays and cancellations in the German rail network using a real-world dataset collected and published by Piet Brömmel. The underlying data is openly available on Hugging Face [1] and is accompanied by a detailed exploratory analysis on his documentation website [2] as well as the full data collection and processing pipeline provided in the corresponding GitHub repository [3]. The dataset covers train movements across Germany over an extended time period and includes, among other elements, information on scheduled and actual arrival and departure times, train types, station identifiers, delay evolution, and cancellation events.

<img src="./figures/distribution.png" alt="drawing" style="height:200px;"/>
<img src="./figures/punctuality.png" alt="drawing" style="height:200px;"/>
<img src="./figures/ice_verspaetung.png" alt="drawing" style="height:200px;"/>


> **Data Volume Disclaimer:**
> The dataset is large. Individual months contain more than two million rows, and the complete dataset exceeds 1 GB in size. Depending on the hardware used, full-scale processing may lead to substantial computational overhead. If you encounter memory or runtime constraints, it is acceptable to work with a well-justified subset of the data. Any such reduction must be clearly documented, including the selection strategy, underlying assumptions, and potential implications for your analysis and modelling results.

---
## Tasks
**Task 1: Exploratory Data Analysis of Train Delays and Cancellations**

This task builds on the exploratory work by Piet Brömmel [2], who provides initial descriptive insights into delay and cancellation behaviour in the German rail network. His analysis illustrates, among other aspects, how cancellation rates evolve across the day and across train types, and how delays accumulate over the course of a train ride.

Using the provided dataset (no further API calls are required), extend this analysis by identifying additional, data-driven patterns that are not explicitly covered in [2]. Your work should deepen the understanding of structural properties of delays and cancellations and prepare the ground for subsequent modelling tasks.

Possible directions include, but are not limited to:
- Feature engineering of temporal structure (e.g., weekday vs. weekend distinctions, peak vs. off-peak hours, seasonal or monthly effects).
- Processing and enriching station-level information using geographic methods to reveal spatial or regional patterns.
- Incorporating external data such as weather or calendar information. If external data is used, it must be provided offline within the repository and not obtained via live API calls.

**Objectives**
- Identify at least two additional, clearly defined patterns in the dataset that go beyond those discussed in [2].
- Support each pattern with at least one well-designed, clearly labelled visualisation and a concise interpretation that explains the empirical finding and the steps that led to it.

---
**Task 2: Predictive Modelling of Train Delays**

The objective of this task is to develop a predictive model for train delays using the dataset provided in this case study. Unlike Task 1, where the focus lies on uncovering descriptive patterns, this task requires you to formalise a predictive problem, justify your modelling assumptions, and construct an appropriate machine learning pipeline.

You are asked to define your own problem formulation within the scope of delay prediction. Examples include, but are not limited to: predicting the delay at the next station, predicting the expected delay at final arrival, or estimating the delay at a specific forecast horizon. You should derive a clear problem statement based on the structure of the data, the temporal nature of train operations, and the available attributes.

Objectives
- Define a precise predictive problem related to train delays, including a justification of why the target variable and input features are appropriate.
- State all assumptions about feature availability, temporal ordering, and potential data leakage.
- Construct a modelling pipeline that includes feature engineering, model training, and model evaluation.
- Evaluate your model using suitable quantitative metrics and provide a short interpretation of the results, including limitations and potential improvements.

---
**Task 3: Predictive Modelling of Train Cancellations**

The objective of this task is to develop a predictive model for train cancellations using the dataset provided in this case study. While Task 2 focuses on predicting the magnitude of delays, this task requires you to formalise a classification problem, justify your modelling assumptions, and construct an appropriate machine learning pipeline for binary outcomes.

**Objectives**
- Define a precise classification problem related to train cancellations, including a justification of why the target variable and input features are appropriate and operationally meaningful.
- Construct a modelling pipeline that includes feature engineering, model training, and model evaluation.
- Evaluate your model using suitable classification metrics and provide a short interpretation of the results, including limitations, trade-offs between different error types, and potential improvements.

---

## References
- [1] Data: https://huggingface.co/datasets/piebro/deutsche-bahn-data
- [2] Website: https://piebro.github.io/deutsche-bahn-statistics/questions/allgemein/
- [3] Github: https://github.com/piebro/deutsche-bahn-statistics