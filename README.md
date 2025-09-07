# andalucia-circular-analytics

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Data Sources](https://img.shields.io/badge/data-Eurostat%20%7C%20IECA%20%7C%20Junta%20de%20Andaluc%C3%ADa-orange.svg)]()

**Evidence-driven analytics on circular economy for Andalusia**: household sustainable habits (ESOC 2023), municipal waste generation, and packaging recycling.  
This repository provides reproducible pipelines, tidy datasets, and visualizations comparing **Andalusia / Spain / EU**.

---


## Repository structure
```text
├── data/
│   ├── raw/          # original inputs (ESOC CSV/XLS, Junta datasets…)
│   ├── external/     # downloaded from APIs (Eurostat…)
│   └── processed/    # cleaned / tidy outputs ready for analysis
│
├── notebooks/
│   ├── update_data.ipynb
│   └── visualization.ipynb
│
├── src/
│   └── update_data.py
│
├── figures/
│
├── docs/
│   └── policy_brief_circularidad.md
│
├── .github/
│   └── workflows/    # (optional) CI to refresh data
│
├── README.md
└── requirements.txt
```

---

## Data sources
- **Andalusia – ESOC 2023**: household sustainable habits (CSV microdata + XLS dictionary).  
- **Eurostat**:  
  - `env_wasmun` – municipal waste per capita (kg/hab).  
  - `env_waspac` – packaging recycling rate (%), total packaging (W1501), operation = RCV.  
- **Junta de Andalucía (Open Data / REDIAM)**: municipal waste and environmental indicators.  


---

## Quick start
```bash
# create & activate your environment (example with conda)
conda create -n aca python=3.11 -y
conda activate aca
pip install -r requirements.txt
```

Open Jupyter and run the notebooks in `notebooks/`.

---

## How to use

This project can be executed in two main ways: from the command line (for automation) or from a Jupyter Notebook (for interactive exploration).


### 1. Run from Terminal (CLI)

Make sure you are in the project root and that the virtual environment is activated.  
Then run:

```bash
python src/update_data.py
```
This will:

1. Pull Eurostat and Andalucía Open Data datasets.
2. Process and clean them into usable formats.
3. Save processed files in `data/processed/` and `data/external/`.


### 2. Run from Jupyter Notebook

Open Jupyter and navigate to the notebooks/ folder.
Start with:
```bash
jupyter notebook
```
Then open:

- `notebooks/update_data.ipynb` → run the data update pipeline interactively.  
- `notebooks/visualization.ipynb` → explore and visualize the processed datasets.  

This mode is useful if you want to inspect intermediate steps, create plots, or extend the analysis.

---

## Reproducibility
- Run the data refresh script:
```bash
python -m src.update_data
```
This will:
1. Pull Eurostat datasets and save tidy CSVs in `data/external/`.  
2. (If present) parse ESOC 2023 microdata (`data/raw/md_ESOC2023.csv`) + dictionary and write processed tables in `data/processed/`.

---

## Example output
Example: municipal waste per capita (kg/hab) vs packaging recycling rate (%)
Spain vs EU27_2020 (1995–2023).

---

## Notebooks
- `update_data.ipynb`: builds key indicators (waste per capita, packaging recycling, ESOC habits).  
- `visualization.ipynb`: Spain vs EU trends; optionally Andalusia vs Spain when regional data is available.
  
---

## License
- **Code**: MIT (or similar) — edit if needed.  
- **Data**: original sources’ licenses apply (Eurostat, IECA/Junta). Please cite appropriately.
  
---

## Requirements
Create a virtual environment and install dependencies with:

```bash
pip install -r requirements.txt
```
Contents of requirements.txt
```txt
pandas
matplotlib
plotly
eurostat
openpyxl
odfpy
jupyter
```
