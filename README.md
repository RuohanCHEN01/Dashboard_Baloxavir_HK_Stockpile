# Baloxavir Stockpile Dashboard

A Streamlit dashboard project for scenario analysis of influenza antiviral stockpile strategies, based on the existing Hong Kong pandemic model outputs.

## Project structure

```text
baloxavir_dashboard/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   ├── raw/
│   └── processed/
└── src/
    └── prepare_dashboard_data.py
```

## What this project does

This project standardizes existing model outputs into dashboard-ready tables, then displays them in a Streamlit interface for scenario filtering and strategy comparison.

### Main dashboard filters

- Pandemic severity
- Vaccine availability
- Treatment uptake
- Antiviral resistance

### Main KPI cards

- Total infections
- Hospitalizations
- Deaths
- Total cost
- QALYs
- INMB

## Input files required

Place the following raw files into `data/raw/` before running the data preparation script:

- `FCFS_R0105_output_to_CEA_anti_n_vaccine_3month-3.csv`
- `cost_analysis_FCFS_R0105_output_to_CEA_anti_n_vaccine_3month.csv`
- `FCFS_R0105_hospitalization_rates_matrix-2.csv`

## Setup

### 1. Create and activate a virtual environment

#### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

## Run steps

### Step 1. Prepare dashboard data

```bash
python src/prepare_dashboard_data.py
```

This will generate:

- `data/processed/scenario_summary.csv`
- `data/processed/hospitalization_timeseries.csv`

### Step 2. Launch Streamlit

```bash
streamlit run app.py
```

## Current implementation notes

This first development version is designed to get the dashboard running quickly, so several scenario labels are currently inferred instead of being read from an explicit scenario design table.

### Current inferred logic

- `pandemic_severity`: assigned using repeating labels `low`, `moderate`, `high`
- `vaccine_availability`: inferred from whether `Vaccineused` is greater than zero
- `treatment_uptake`: inferred from terciles of `Antiviralused`
- `antiviral_resistance`: inferred from terciles of `RAR`
- `is_baseline`: defined as `BXM=0.0`, `OTV=0.9`, `ZNV=0.1`

## Recommended next refinement

For the formal research version, replace inferred labels with exact mappings from original model run settings, so every scenario shown in the dashboard matches the true experimental design.

## Deliverables in this package

- `app.py`: Streamlit dashboard prototype
- `src/prepare_dashboard_data.py`: result standardization script
- `README.md`: project run instructions
- `requirements.txt`: dependency list

## Troubleshooting

### If processed files are missing

Make sure the three raw CSV files are placed under `data/raw/` and that filenames match exactly.

### If Streamlit cannot open the app

Check that dependencies are installed and that you are running the command from the project root directory.

### If charts look empty

That usually means the filtered result set is empty or the standardization script did not successfully generate processed files.
