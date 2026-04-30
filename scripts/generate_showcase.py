"""
Generate a static demo page showcasing the dashboard capabilities.
This creates a self-contained HTML file for GitHub README screenshots and project showcase.
"""

import json
import os
import sys

import pandas as pd
import numpy as np

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

import pandas as pd
import numpy as np
# =============================================================================
# Load Data
# =============================================================================
DATA_DIR = os.path.join(PROJECT_ROOT, "Raw_Code_Data")
CSV_FILE = os.path.join(
    DATA_DIR, "cost_analysis_FCFS_R0105_output_to_CEA_anti_n_vaccine_3month.csv"
)

df = pd.read_csv(CSV_FILE)
print(f"Loaded {len(df)} rows, {len(df.columns)} columns")
print(f"Columns: {list(df.columns[:10])}...")

# =============================================================================
# Generate Visualizations using Plotly
# =============================================================================
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_scenario_scatter(df):
    """Scenario comparison scatter plot."""
    fig = go.Figure()

    # Group by drug type if available
    drug_col = None
    for col in ["Drug", "drug", "Antiviral", "antiviral"]:
        if col in df.columns:
            drug_col = col
            break

    if drug_col:
        for drug in df[drug_col].unique():
            subset = df[df[drug_col] == drug]
            color = "#E63946" if "BXM" in str(drug).upper() or "Baloxavir" in str(drug) else "#457B9D"
            fig.add_trace(go.Scatter(
                x=subset.iloc[:, 3] if len(subset.columns) > 3 else range(len(subset)),
                y=subset.iloc[:, 4] if len(subset.columns) > 4 else range(len(subset)),
                mode="markers",
                name=str(drug),
                marker=dict(size=10, color=color, opacity=0.7),
                text=[f"Row {i}" for i in subset.index],
                hovertemplate="%{text}<extra></extra>",
            ))
    else:
        fig.add_trace(go.Scatter(
            x=df.iloc[:, 3],
            y=df.iloc[:, 4],
            mode="markers",
            marker=dict(size=8, color="#1E3A5F", opacity=0.7),
        ))

    fig.update_layout(
        title="Scenario Analysis: Multi-dimensional Comparison",
        template="plotly_white",
        height=450,
        font=dict(size=12),
    )
    return fig


def create_cost_bar(df):
    """Cost comparison bar chart."""
    fig = go.Figure()
    labels = df.iloc[:8, 1].astype(str) if len(df.columns) > 1 else [f"S{i}" for i in range(8)]

    # Use numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns[:4]
    colors = ["#E63946", "#457B9D", "#2A9D8F", "#E9C46A"]

    for i, col in enumerate(numeric_cols):
        fig.add_trace(go.Bar(
            name=col,
            x=labels[:min(8, len(df))],
            y=df[col].iloc[:min(8, len(df))],
            marker_color=colors[i % len(colors)],
        ))

    fig.update_layout(
        barmode="group",
        title="Cost-Effectiveness Metrics by Scenario",
        template="plotly_white",
        height=450,
        font=dict(size=12),
    )
    return fig


def create_ce_plane(df):
    """Cost-Effectiveness Plane."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) >= 2:
        costs = df[numeric_cols[0]].values
        effects = df[numeric_cols[1]].values
    else:
        costs = np.random.randn(len(df)) * 1000
        effects = np.random.randn(len(df)) * 0.05

    fig = go.Figure()

    # WTP threshold line
    wtp = 50000
    x_range = np.linspace(min(effects) - 0.1, max(effects) + 0.1, 100)
    fig.add_trace(go.Scatter(
        x=x_range,
        y=wtp * x_range,
        mode="lines",
        name=f"WTP = HKD {wtp:,}",
        line=dict(dash="dash", color="#999"),
    ))

    fig.add_trace(go.Scatter(
        x=effects,
        y=costs,
        mode="markers",
        name="Scenarios",
        marker=dict(size=10, color="#1E3A5F", opacity=0.7),
    ))

    # Quadrant lines
    fig.add_hline(y=0, line_dash="dot", line_color="#CCC")
    fig.add_vline(x=0, line_dash="dot", line_color="#CCC")

    fig.update_layout(
        title="Cost-Effectiveness Plane",
        xaxis_title="Incremental Effectiveness (QALYs)",
        yaxis_title="Incremental Cost (HKD)",
        template="plotly_white",
        height=450,
        font=dict(size=12),
    )
    return fig


# =============================================================================
# Generate all charts
# =============================================================================
print("Generating visualizations...")
fig1 = create_scenario_scatter(df)
fig2 = create_cost_bar(df)
fig3 = create_ce_plane(df)

# =============================================================================
# Build HTML
# =============================================================================
charts_html = ""
for i, fig in enumerate([fig1, fig2, fig3], 1):
    charts_html += f'<div class="chart-section"><div id="chart{i}"></div></div>\n'

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Baloxavir Stockpile Dashboard - AI-Powered Decision Support</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, sans-serif;
            background: #F8FAFC;
            color: #1E293B;
            line-height: 1.6;
        }}
        .header {{
            background: linear-gradient(135deg, #1E3A5F 0%, #2A5A8F 100%);
            color: white;
            padding: 48px 40px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 8px;
            letter-spacing: -0.5px;
        }}
        .header .subtitle {{
            font-size: 16px;
            opacity: 0.85;
            max-width: 700px;
            margin: 0 auto;
        }}
        .header .badges {{
            margin-top: 16px;
            display: flex;
            justify-content: center;
            gap: 8px;
            flex-wrap: wrap;
        }}
        .header .badge {{
            background: rgba(255,255,255,0.15);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
        }}
        .container {{
            max-width: 1100px;
            margin: 0 auto;
            padding: 32px 24px;
        }}
        .section {{
            margin-bottom: 40px;
        }}
        .section h2 {{
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 2px solid #E2E8F0;
            color: #1E3A5F;
        }}
        .feature-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 16px;
            margin-bottom: 32px;
        }}
        .feature-card {{
            background: white;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 20px;
        }}
        .feature-card h3 {{
            font-size: 14px;
            font-weight: 600;
            color: #1E3A5F;
            margin-bottom: 6px;
        }}
        .feature-card p {{
            font-size: 13px;
            color: #64748B;
        }}
        .stats-row {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 32px;
        }}
        .stat-card {{
            background: white;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }}
        .stat-card .number {{
            font-size: 28px;
            font-weight: 700;
            color: #1E3A5F;
        }}
        .stat-card .label {{
            font-size: 12px;
            color: #64748B;
            margin-top: 4px;
        }}
        .chart-section {{
            background: white;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 20px;
        }}
        .arch-diagram {{
            background: white;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 24px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            line-height: 1.5;
            overflow-x: auto;
            white-space: pre;
            color: #475569;
        }}
        .footer {{
            text-align: center;
            padding: 24px;
            color: #94A3B8;
            font-size: 13px;
        }}
        .footer a {{
            color: #1E3A5F;
            text-decoration: none;
        }}
        @media (max-width: 640px) {{
            .stats-row {{ grid-template-columns: repeat(2, 1fr); }}
            .header h1 {{ font-size: 22px; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>AI-Powered Influenza Antiviral Stockpile Dashboard</h1>
        <p class="subtitle">
            Cost-effectiveness analysis of Baloxavir vs Oseltamivir stockpile strategies
            for Hong Kong pandemic preparedness, enhanced by LLM-driven automation.
        </p>
        <div class="badges">
            <span class="badge">Python 3.11</span>
            <span class="badge">Streamlit</span>
            <span class="badge">LLM Agents</span>
            <span class="badge">Plotly</span>
            <span class="badge">MIT License</span>
        </div>
    </div>

    <div class="container">
        <div class="section">
            <h2>Project Statistics</h2>
            <div class="stats-row">
                <div class="stat-card">
                    <div class="number">{len(df)}</div>
                    <div class="label">Scenarios Analyzed</div>
                </div>
                <div class="stat-card">
                    <div class="number">{len(df.columns)}</div>
                    <div class="label">Parameters per Scenario</div>
                </div>
                <div class="stat-card">
                    <div class="number">4</div>
                    <div class="label">LLM Providers Supported</div>
                </div>
                <div class="stat-card">
                    <div class="number">1M</div>
                    <div class="label">Max Context Tokens</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>AI Agent Capabilities</h2>
            <div class="feature-grid">
                <div class="feature-card">
                    <h3>Literature Extraction Agent</h3>
                    <p>Automatically extract epidemiological parameters (VE, R0, serial interval, drug costs) from PubMed abstracts and WHO guidelines using structured prompting.</p>
                </div>
                <div class="feature-card">
                    <h3>Natural Language Query Engine</h3>
                    <p>Query simulation results using plain language. Ask "What is the ICER when BXM covers 30%?" and get data-backed answers with citations.</p>
                </div>
                <div class="feature-card">
                    <h3>Policy Report Generator</h3>
                    <p>Generate professional policy briefs with AI-summarized executive summaries, key findings, sensitivity analysis, and actionable recommendations.</p>
                </div>
                <div class="feature-card">
                    <h3>Multi-Provider LLM Interface</h3>
                    <p>Unified SDK across OpenAI, Claude, MiMo V2.5 (1M context), and DeepSeek. Switch providers with a single configuration change.</p>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>Visualization Samples</h2>
            {charts_html}
        </div>

        <div class="section">
            <h2>System Architecture</h2>
            <div class="arch-diagram">+------------------------------------------------------------------+
|                     AI / Agent Layer                             |
|  +------------------+  +---------------+  +-------------------+  |
|  | Literature       |  | NL Query      |  | Policy Report     |  |
|  | Extraction Agent |  | Engine        |  | Generator         |  |
|  +--------+---------+  +-------+-------+  +---------+---------+  |
|           |                   |                     |             |
|           +-------------------+---------------------+             |
+-------------------------------|-----------------------------------+
                                |
+-------------------------------|-----------------------------------+
|                     Core Analytics Engine                        |
|  +------------------+  +---------------+  +-------------------+  |
|  | SEIR / SMM       |  | Monte Carlo   |  | Cost-Effectiveness|  |
|  | Transmission Model|  | Simulator     |  | Analyzer          |  |
|  +------------------+  +---------------+  +-------------------+  |
+-------------------------------|-----------------------------------+
                                |
+-------------------------------|-----------------------------------+
|                     Presentation Layer                         |
|  +------------------+  +---------------+  +-------------------+  |
|  | Streamlit        |  | Plotly        |  | PDF / CSV / HTML  |  |
|  | Dashboard        |  | Charts        |  | Export            |  |
|  +------------------+  +---------------+  +-------------------+  |
+------------------------------------------------------------------+</div>
        </div>
    </div>

    <div class="footer">
        <p>Ruohan Chen | PhD Candidate, HKU School of Public Health | WHO CC for Infectious Disease Epidemiology</p>
        <p><a href="https://github.com/RuohanCHEN01/Dashboard_Baloxavir_HK_Stockpile">GitHub Repository</a></p>
    </div>

    <script>
        // Render Plotly charts
        __CHART_SCRIPT_PLACEHOLDER__
    </script>
</body>
</html>"""

# Serialize Plotly figures to JSON
fig1_json = json.dumps(fig1.to_dict(), default=str)
fig2_json = json.dumps(fig2.to_dict(), default=str)
fig3_json = json.dumps(fig3.to_dict(), default=str)

chart_script = """
        var chartConfigs = [
            {fig: """ + fig1_json + """, id: 'chart1'},
            {fig: """ + fig2_json + """, id: 'chart2'},
            {fig: """ + fig3_json + """, id: 'chart3'},
        ];
        chartConfigs.forEach(function(cfg) {
            Plotly.newPlot(cfg.id, cfg.fig.data, cfg.fig.layout, {responsive: true});
        });"""

html_content = html_content.replace("__CHART_SCRIPT_PLACEHOLDER__", chart_script)

# Write output
output_path = os.path.join(PROJECT_ROOT, "docs", "demo_showcase.html")
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"\nDemo showcase generated: {output_path}")
print(f"File size: {os.path.getsize(output_path) / 1024:.1f} KB")
