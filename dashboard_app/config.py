# Baloxavir Stockpile Dashboard Configuration

# Data Paths
DATA_PATH = 'data/'
INPUT_FILE = 'data/input_data.xlsx'
OUTPUT_FILE = 'data/output_data.xlsx'

# Dashboard Config
DASHBOARD_CONFIG = {
    'title': 'Baloxavir Stockpile Dashboard',
    'version': '1.0',
}

# Scenario Labels
SCENARIO_LABELS = ['Baseline', 'Treatment Scenario 1', 'Treatment Scenario 2']

# KPI Metrics
KPI_METRICS = {
    'total_stockpile': 'Total stockpile of Baloxavir',
    'treated_patients': 'Total number of treated patients',
    'cost_efficacy': 'Cost-effectiveness ratio',
}

# Visualization Settings
VISUALIZATION_SETTINGS = {
    'theme': 'light',
    'show_legend': True,
    'title_font_size': 20,
}

# Baseline Scenario
BASELINE_SCENARIO = 'Baseline'

# Willingness to Pay Parameters
WTP_PARAMETERS = {
    'threshold': 50000,
    'discount_rate': 0.03,
}