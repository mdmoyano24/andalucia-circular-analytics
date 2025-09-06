# andalucia-circular-analytics

Evidence-driven analytics on circular economy for Andalusia: household sustainable habits (ESOC 2023), municipal waste generation, and packaging recycling. The repo provides reproducible pipelines, tidy datasets, and visuals comparing **Andalusia / Spain / EU**.

## Quick start
```bash
# create & activate your environment (example with conda)
conda create -n aca python=3.11 -y
conda activate aca
pip install -r requirements.txt
```

Open Jupyter and run the notebooks in `notebooks/`.

## Repository structure

├── data/
│ ├── raw/ # original inputs (ESOC CSV/XLS, Junta datasets…)
│ ├── external/ # downloaded from APIs (Eurostat…)
│ └── processed/ # cleaned / tidy outputs ready for analysis
│
├── notebooks/
│ ├── 01_indicadores_basicos.ipynb
│ └── 02_visualizaciones.ipynb
│
├── src/
│ └── update_data.py
│
├── figures/
│
├── docs/
│ └── policy_brief_circularidad.md
│
├── .github/
│ └── workflows/ # (optional) CI to refresh data
│
├── README.md
└── requirements.txt

## Data sources
- **Andalusia – ESOC 2023**: household sustainable habits (CSV microdata + XLS dictionary).  
- **Eurostat**:  
  - `env_wasmun` – municipal waste per capita (kg/hab).  
  - `env_waspac` – packaging recycling rate (%), total packaging (W1501), operation = RCV.  
- **Junta de Andalucía (Open Data / REDIAM)**: municipal waste and environmental indicators.  

## Reproducibility
- Run the data refresh script:
```bash
python -m src.update_data
```
This will:
1. Pull Eurostat datasets and save tidy CSVs in `data/external/`.  
2. (If present) parse ESOC 2023 microdata (`data/raw/md_ESOC2023.csv`) + dictionary and write processed tables in `data/processed/`.  

## Notebooks
- `01_indicadores_basicos.ipynb`: builds key indicators (waste per capita, packaging recycling, ESOC habits).  
- `02_visualizaciones.ipynb`: Spain vs EU trends; optionally Andalusia vs Spain when regional data is available.  

## License
- **Code**: MIT (or similar) — edit if needed.  
- **Data**: original sources’ licenses apply (Eurostat, IECA/Junta). Please cite appropriately.

# 2) `requirements.txt`
```txt
pandas
matplotlib
plotly
eurostat
openpyxl
odfpy
jupyter
```
