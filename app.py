"""
AI-Powered Influenza Antiviral Stockpile Dashboard
====================================================
An interactive Streamlit dashboard for analyzing BXM vs OTV stockpile strategies
with integrated AI Agent capabilities.

Displays manuscript tables and figures from:
  Chen et al. "Health Economic Impact of Incorporating Baloxavir into
  Hong Kong's Influenza Pandemic Stockpile Strategy"

Author: Ruohan Chen (HKU PhD Candidate)
"""

import sys
from pathlib import Path  # noqa: E402

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

import streamlit as st  # noqa: E402
import pandas as pd  # noqa: E402
import plotly.graph_objects as go  # noqa: E402

# ---- Page Configuration ----
st.set_page_config(
    page_title="Baloxavir HK Stockpile AI Dashboard",
    page_icon="microscope",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---- Custom CSS ----
st.markdown("""
<style>
    .main .block-container { padding-top: 1.5rem; }
    section[data-testid="stSidebar"] { background-color: #0f172a; }
    h1, h2, h3 { color: #e2e8f0; }
    .stMetricLabel { color: #94a3b8; font-size: 0.85rem; }
    .stMetricValue { color: #f1f5f9; }
    div[data-testid="stMetric"] { background-color: #1e293b; border-radius: 0.75rem; padding: 1rem; border: 1px solid #334155; }
    div.stDataFrame { border-radius: 0.75rem; }
    .figure-caption { color: #94a3b8; font-size: 0.85rem; font-style: italic; margin-top: 0.5rem; text-align: center; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# MANUSCRIPT DATA — Tables & Figures from Chen et al.
# ============================================================
@st.cache_data
def load_manuscript_tables():
    """Load Table 1 (Transmission) and Table 2 (Cost-Effectiveness) from manuscript."""
    table1_data = {
        "R0": [1.5, 1.5, 1.5, 1.5, 1.5, 1.5,
               2, 2, 2, 2, 2, 2,
               3, 3, 3, 3, 3, 3],
        "Distribution Strategy": [
            "40% Random", "40% Random", "40% Random", "FCFS", "FCFS", "FCFS",
            "40% Random", "40% Random", "40% Random", "FCFS", "FCFS", "FCFS",
            "40% Random", "40% Random", "40% Random", "FCFS", "FCFS", "FCFS",
        ],
        "Stockpile Strategy": [
            "90% OTV + 10% ZNV", "10% BXM + 90% OTV", "20% BXM + 80% OTV",
            "90% OTV + 10% ZNV", "10% BXM + 90% OTV", "20% BXM + 80% OTV",
            "90% OTV + 10% ZNV", "10% BXM + 90% OTV", "20% BXM + 80% OTV",
            "90% OTV + 10% ZNV", "10% BXM + 90% OTV", "20% BXM + 80% OTV",
            "90% OTV + 10% ZNV", "10% BXM + 90% OTV", "20% BXM + 80% OTV",
            "90% OTV + 10% ZNV", "10% BXM + 90% OTV", "20% BXM + 80% OTV",
        ],
        "AR (%)": [33.13, 30.71, 28.63, 20.70, 14.60, 6.40,
                   70.41, 69.76, 69.20, 68.54, 67.50, 66.32,
                   89.60, 89.38, 89.20, 89.04, 88.73, 88.49],
        "RAR (%)": [5.61, 5.82, 5.22, 18.78, 13.74, 5.93,
                    8.85, 9.93, 9.84, 40.76, 44.51, 42.16,
                    8.54, 9.78, 10.01, 33.48, 37.56, 36.55],
        "Hosp. Rate (%)": [0.26, 0.24, 0.23, 0.16, 0.11, 0.05,
                           0.58, 0.57, 0.56, 0.57, 0.56, 0.55,
                           0.75, 0.74, 0.74, 0.75, 0.75, 0.74],
        "Mortality": [0.13, 0.12, 0.11, 0.08, 0.05, 0.02,
                      0.31, 0.30, 0.30, 0.31, 0.30, 0.29,
                      0.42, 0.41, 0.41, 0.42, 0.41, 0.41],
    }
    table2_data = {
        "R0": [1.5, 1.5, 1.5, 1.5, 1.5, 1.5,
               2, 2, 2, 2, 2, 2,
               3, 3, 3, 3, 3, 3],
        "Distribution Strategy": [
            "40% Random", "40% Random", "40% Random", "FCFS", "FCFS", "FCFS",
            "40% Random", "40% Random", "40% Random", "FCFS", "FCFS", "FCFS",
            "40% Random", "40% Random", "40% Random", "FCFS", "FCFS", "FCFS",
        ],
        "Stockpile Strategy": [
            "90% OTV + 10% ZNV", "10% BXM + 90% OTV", "20% BXM + 80% OTV",
            "90% OTV + 10% ZNV", "10% BXM + 90% OTV", "20% BXM + 80% OTV",
            "90% OTV + 10% ZNV", "10% BXM + 90% OTV", "20% BXM + 80% OTV",
            "90% OTV + 10% ZNV", "10% BXM + 90% OTV", "20% BXM + 80% OTV",
            "90% OTV + 10% ZNV", "10% BXM + 90% OTV", "20% BXM + 80% OTV",
            "90% OTV + 10% ZNV", "10% BXM + 90% OTV", "20% BXM + 80% OTV",
        ],
        "Direct Cost\n(Hosp.)": [524050000, 482787500, 446012500,
                                 308503000, 214653500, 90125000,
                                 1142592500, 1125123000, 1108496000,
                                 1138767500, 1116861000, 1083018500,
                                 1486628000, 1476809500, 1467118500,
                                 1493922000, 1483338000, 1468954500],
        "Direct Cost\n(GP+Test+Antiviral)": [3829716087, 3639159548, 3486089291,
                                              2887792791, 2420143861, 1766992303,
                                              7048477580, 7007429820, 6992432260,
                                              6888336560, 6815237560, 6753834527,
                                              8829413100, 8824662900, 8841595680,
                                              8777548126, 8764027520, 8777048080],
        "Indirect Cost": [6260591350, 5805509800, 5411586925,
                          3892200725, 2745284150, 1198732375,
                          13179467425, 13056726750, 12954554750,
                          12865779500, 12675371400, 12446028675,
                          16570386775, 16529073125, 16492528800,
                          16490478800, 16433567225, 16382319775],
        "Total Cost (HK$)": [10614357437, 9927456848, 9343688716,
                              7088496516, 5380081511, 3055849678,
                              21370537505, 21189279570, 21055483010,
                              20892883560, 20607469960, 20282881702,
                              26886427875, 26830545525, 26801242980,
                              26761948926, 26680933245, 26628322355],
        "QALY Loss": [6167, 5694, 5275, 3967, 2815, 1303,
                      13105, 12834, 12691, 12952, 12651, 12296,
                      16855, 16645, 16526, 16865, 16637, 16470],
        "INMB (HK$)": ["-", 886404200, 1647190352,
                        "-", 2194805107, 5157745571,
                        "-", 295800545, 489764540,
                        "-", 412402588, 887225207,
                        "-", 144334137, 224045032,
                        "-", 177135429, 300333039],
    }
    return pd.DataFrame(table1_data), pd.DataFrame(table2_data)


df_table1, df_table2 = load_manuscript_tables()


# ---- Data Loading (simulation CSV for interactive charts) ----
@st.cache_data
def load_simulation_data():
    """Load CSV data files from Raw_Code_Data/."""
    cea_path = ROOT / "Raw_Code_Data" / "cost_analysis_FCFS_R0105_output_to_CEA_anti_n_vaccine_3month.csv"
    output_path = ROOT / "Raw_Code_Data" / "FCFS_R0105_output_to_CEA_anti_n_vaccine_3month.csv"
    hosp_path = ROOT / "Raw_Code_Data" / "FCFS_R0105_hospitalization_rates_matrix.csv"

    df_cea = pd.read_csv(cea_path)
    df_output = pd.read_csv(output_path)
    df_hosp = pd.read_csv(hosp_path)
    return df_cea, df_output, df_hosp


df_cea, df_output, df_hosp = load_simulation_data()
df_cea.columns = [c.strip() for c in df_cea.columns]
df_output.columns = [c.strip() for c in df_output.columns]


# ---- Plotly Theme ----
PLOTLY_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#94a3b8", family="-apple-system, sans-serif", size=12),
    xaxis=dict(gridcolor="#1e293b", zerolinecolor="#334155"),
    yaxis=dict(gridcolor="#1e293b", zerolinecolor="#334155"),
    margin=dict(t=50, r=30, b=50, l=70),
    colorway=["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"],
    legend=dict(font=dict(color="#94a3b8"), orientation="h", y=-0.25),
)


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.title("Baloxavir Stockpile")
    st.caption("AI-Powered Decision Support")
    st.markdown("---")

    # Navigation
    page = st.radio(
        "Navigate",
        [
            "Overview",
            "Transmission (Table 1 & Fig 2)",
            "Cost-Effectiveness (Table 2 & Fig 3)",
            "Hospitalization (Fig 4)",
            "AI Agent Demo",
        ],
        index=0,
        label_visibility="collapsed",
    )

    st.markdown("---")

    # Filters
    st.subheader("Stockpile Filters")
    st.caption("BXM + OTV + ZNV = 100%")

    bxm_slider = st.slider(
        "BXM Proportion",
        min_value=0,
        max_value=100,
        value=(0, 100),
        step=10,
        format="%d%%",
    )
    otv_slider = st.slider(
        "OTV Proportion",
        min_value=0,
        max_value=100,
        value=(0, 100),
        step=10,
        format="%d%%",
    )

    # Calculate ZNV range
    bxm_min, bxm_max = bxm_slider
    otv_min, otv_max = otv_slider
    znv_min = max(0, 100 - bxm_max - otv_max)
    znv_max = min(100, 100 - bxm_min - otv_min)
    if znv_max < 0 or znv_min > 100:
        znv_display = "No valid range"
    else:
        znv_display = f"{znv_min}% – {znv_max}%"
    st.info(f"**ZNV Proportion Range:** {znv_display}")

    # Apply filters on simulation data
    mask = (
        (df_cea["BXM_proportion"] >= bxm_min / 100)
        & (df_cea["BXM_proportion"] <= bxm_max / 100)
        & (df_cea["OTV_proportion"] >= otv_min / 100)
        & (df_cea["OTV_proportion"] <= otv_max / 100)
    )
    df_filtered = df_cea[mask].copy()
    df_valid = df_filtered.dropna(subset=["Total_QALY"]).copy()

    st.markdown("---")
    st.caption("Built by Ruohan Chen | HKU WHO CC")
    st.caption("Manuscript: Chen et al. (2026)")
    st.caption(f"Simulation: {len(df_valid)} scenarios shown")


# ============================================================
# PAGE: Overview
# ============================================================
if page == "Overview":
    st.title("AI-Powered Influenza Antiviral Stockpile Dashboard")
    st.markdown(
        """
        ### Health Economic Impact of Incorporating Baloxavir into Hong Kong's
        Influenza Pandemic Stockpile Strategy

        **Authors:** Ruohan Chen, Christopher KC Lai, Benjamin John Cowling\*, Zhanwei Du\*

        **Affiliations:**
        WHO Collaborating Center for Infectious Disease Epidemiology and Control,
        School of Public Health, LKS Faculty of Medicine, The University of Hong Kong
        """
    )

    # Key metrics from manuscript
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Pandemic Scenarios", "3", "R0 = 1.5, 2.0, 3.0")
    with col2:
        st.metric("Drug Combinations", "66", "BXM/OTV/ZNV combos")
    with col3:
        st.metric("Allocation Modes", "2", "FCFS vs 40% Random")
    with col4:
        st.metric("Best INMB (R0=1.5)", "HKD 5.16B", "20% BXM, FCFS")

    # Figure 1: Compartmental Model Diagram
    st.markdown("### Figure 1. Compartmental Model Structure")
    st.image(ROOT / "assets" / "Figure_1.png", use_container_width=True)
    st.markdown(
        '<p class="figure-caption">'
        'Extended SEIR model with Vaccination (V), Antiviral Treatment (t), '
        'and Hospitalization (H) compartments, parameterised to Hong Kong population.'
        '</p>',
        unsafe_allow_html=True,
    )

    # Manuscript structure overview
    st.markdown("### Manuscript Content")
    cols = st.columns(4)
    sections = [
        ("Table 1", "Transmission outcomes", "AR, RAR, Hosp Rate, Mortality", "18 rows x 3 R0"),
        ("Table 2", "Cost-effectiveness", "Costs, QALY, INMB", "18 rows x 3 R0"),
        ("Figure 2", "Transmission heatmap", "AR & RAR by composition", "6 panels"),
        ("Figure 3", "INMB heatmap", "Cost-effectiveness by composition", "6 panels"),
    ]
    for i, (label, title, desc, size) in enumerate(sections):
        with cols[i]:
            st.markdown(
                f"""
                <div style="background:#1e293b; border:1px solid #334155; border-radius:0.75rem; padding:1.2rem; margin-bottom:0.8rem;">
                    <div style="font-weight:700; color:#3b82f6; margin-bottom:0.3rem;">{label}</div>
                    <div style="font-weight:600; color:#e2e8f0; margin-bottom:0.3rem;">{title}</div>
                    <div style="font-size:0.82rem; color:#94a3b8;">{desc}</div>
                    <div style="font-size:0.75rem; color:#64748b; margin-top:0.3rem;">{size}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Navigate hint
    st.markdown("---")
    st.info("Use the sidebar to navigate to **Transmission**, **Cost-Effectiveness**, "
            "**Hospitalization**, and **AI Agent Demo** pages for detailed results.")


# ============================================================
# PAGE: Transmission — Table 1 & Figure 2
# ============================================================
elif page == "Transmission (Table 1 & Fig 2)":
    st.title("Transmission Outcomes")
    st.caption("BXM-supplementary stockpile strategies — Table 1 & Figure 2")

    # Table 1
    st.markdown("### Table 1. Transmission Outcomes of BXM-Supplementary Strategies")
    st.caption("Abbreviation: OTV, oseltamivir; ZNV, zanamivir; BXM, baloxavir; FCFS, first-come-first-serve.")

    # R0 filter for manuscript table
    r0_filter = st.selectbox("Filter by R0", [1.5, 2.0, 3.0], format_func=lambda x: f"R0 = {x}", key="t1_r0")
    df_t1_filtered = df_table1[df_table1["R0"] == r0_filter].copy()
    st.dataframe(
        df_t1_filtered.style.format({
            "AR (%)": "{:.2f}",
            "RAR (%)": "{:.2f}",
            "Hosp. Rate (%)": "{:.2f}",
            "Mortality": "{:.2f}",
        }),
        use_container_width=True,
        hide_index=True,
    )

    # Interactive visualization from simulation data
    st.markdown("### Interactive: Attack Rate & Resistance by Stockpile Composition")
    if len(df_valid) == 0:
        st.warning("No scenarios match the current filter. Adjust the sidebar filters.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Attack Rate Heatmap")
            pivot_ar = df_output.pivot_table(
                index="BXM_proportion", columns="OTV_proportion", values="AR"
            )
            fig_ar = go.Figure(go.Heatmap(
                z=pivot_ar.values,
                x=[f"{v*100:.0f}%" for v in pivot_ar.columns],
                y=[f"{v*100:.0f}%" for v in pivot_ar.index],
                colorscale=[[0, "#10b981"], [0.5, "#f59e0b"], [1, "#ef4444"]],
                hovertemplate="BXM: %{y}, OTV: %{x}<br>AR: %{z:.4f}<extra></extra>",
            ))
            fig_ar.update_layout(**PLOTLY_THEME, xaxis_title="OTV %", yaxis_title="BXM %")
            st.plotly_chart(fig_ar, use_container_width=True)

        with col2:
            st.markdown("#### Resistance Rate Heatmap")
            pivot_rar = df_output.pivot_table(
                index="BXM_proportion", columns="OTV_proportion", values="RAR"
            )
            fig_rar = go.Figure(go.Heatmap(
                z=pivot_rar.values,
                x=[f"{v*100:.0f}%" for v in pivot_rar.columns],
                y=[f"{v*100:.0f}%" for v in pivot_rar.index],
                colorscale=[[0, "#1e293b"], [0.5, "#f59e0b"], [1, "#ef4444"]],
                hovertemplate="BXM: %{y}, OTV: %{x}<br>RAR: %{z:.4f}<extra></extra>",
            ))
            fig_rar.update_layout(**PLOTLY_THEME, xaxis_title="OTV %", yaxis_title="BXM %")
            st.plotly_chart(fig_rar, use_container_width=True)

    # Figure 2: Transmission heatmap from manuscript
    st.markdown("### Figure 2. Transmission Effects by Antiviral Composition")
    st.image(ROOT / "assets" / "Figure_2.png", use_container_width=True)
    st.markdown(
        '<p class="figure-caption">'
        'Panels A–C represent R0 = 1.5, 2.0, 3.0. '
        'Left column: 40% randomization; Right column: FCFS. '
        'Circle size = AR; Color = RAR.'
        '</p>',
        unsafe_allow_html=True,
    )


# ============================================================
# PAGE: Cost-Effectiveness — Table 2 & Figure 3
# ============================================================
elif page == "Cost-Effectiveness (Table 2 & Fig 3)":
    st.title("Cost-Effectiveness Analysis")
    st.caption("BXM-supplementary stockpile strategies — Table 2 & Figure 3")

    # Table 2
    st.markdown("### Table 2. Cost-Effectiveness Results of BXM-Supplementary Strategies")
    st.caption("Abbreviation: QALY, quality-adjusted life year; INMB, incremental net monetary benefit; FCFS, first-come-first-serve.")

    r0_filter = st.selectbox("Filter by R0", [1.5, 2.0, 3.0], format_func=lambda x: f"R0 = {x}", key="t2_r0")
    df_t2_filtered = df_table2[df_table2["R0"] == r0_filter].copy()

    # Format large numbers for display
    def format_cost(val):
        if isinstance(val, (int, float)):
            return f"HKD {val:,.0f}"
        return str(val)

    st.dataframe(
        df_t2_filtered.style.format({
            "Total Cost (HK$)": lambda x: f"HKD {x:,.0f}",
            "QALY Loss": "{:,.0f}",
            "INMB (HK$)": lambda x: f"HKD {x:,.0f}" if isinstance(x, (int, float)) else str(x),
        }),
        use_container_width=True,
        hide_index=True,
    )

    # Key metrics from manuscript
    st.markdown("### Key Cost-Effectiveness Findings")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Max INMB (R0=1.5)", "HKD 5.16B", "20% BXM, FCFS")
    with col2:
        st.metric("Max INMB (R0=2.0)", "HKD 887M", "20% BXM, FCFS")
    with col3:
        st.metric("Max INMB (R0=3.0)", "HKD 300M", "20% BXM, FCFS")

    # Interactive CE Plane
    if len(df_valid) > 0:
        st.markdown("### Interactive: Cost-Effectiveness Plane")
        fig_ce = go.Figure()
        base_cost, base_qaly = df_valid.iloc[0]["Total_cost"], df_valid.iloc[0]["Total_QALY"]
        fig_ce.add_trace(go.Scatter(
            x=df_valid["Total_cost"] - base_cost,
            y=df_valid["Total_QALY"] - base_qaly,
            mode="markers",
            marker=dict(
                size=10,
                color=df_valid["BXM_proportion"],
                colorscale=[[0, "#f59e0b"], [1, "#8b5cf6"]],
                line=dict(color="rgba(255,255,255,0.3)", width=1),
            ),
            text=df_valid.apply(lambda r: f"BXM:{int(r['BXM_proportion']*100)}%", axis=1),
            hovertemplate="<b>%{text}</b><br>Inc. Cost: $%{x:,.0f}<br>Inc. QALY: %{y:,.0f}<extra></extra>",
        ))
        fig_ce.add_hline(y=0, line_dash="dash", line_color="#334155")
        fig_ce.add_vline(x=0, line_dash="dash", line_color="#334155")
        fig_ce.update_layout(
            **PLOTLY_THEME,
            xaxis_title="Incremental Cost (HKD)",
            yaxis_title="Incremental QALY",
            title=dict(text="vs OTV-only Baseline", font=dict(size=13, color="#e2e8f0")),
        )
        st.plotly_chart(fig_ce, use_container_width=True)

    # Figure 3: INMB heatmap from manuscript
    st.markdown("### Figure 3. INMB by Antiviral Composition")
    st.image(ROOT / "assets" / "Figure_3.png", use_container_width=True)
    st.markdown(
        '<p class="figure-caption">'
        'Panels A–C represent R0 = 1.5, 2.0, 3.0. '
        'Left column: 40% randomization; Right column: FCFS. '
        'Darker colors indicate greater economic value (INMB).'
        '</p>',
        unsafe_allow_html=True,
    )


# ============================================================
# PAGE: Hospitalization — Figure 4
# ============================================================
elif page == "Hospitalization (Fig 4)":
    st.title("Public Hospital Ward Demand")
    st.caption("Daily occupancy during pandemic — Figure 4")

    st.markdown("""
    **Key Insight:** At R0 = 1.5, the baseline strategy (90% OTV + 10% ZNV) under
    40% randomization produced a peak approaching the collapse threshold. Introducing
    BXM, especially at 20% under FCFS, significantly reduced peak occupancy below
    the collapse threshold.

    At R0 = 3.0, all strategies breached the collapse threshold, confirming that
    antiviral stockpile optimization must be paired with non-pharmaceutical interventions.
    """)

    # Figure 4: Hospitalization time series from manuscript
    st.markdown("### Figure 4. Daily Public Hospital Ward Occupancy")
    st.image(ROOT / "assets" / "Figure_4.png", use_container_width=True)
    st.markdown(
        '<p class="figure-caption">'
        'Green curve: current baseline (90% OTV + 10% ZNV, 40% random). '
        'Orange/blue/red curves: BXM-supplementary strategies. '
        'Dashed lines: Hong Kong capacity thresholds (100%, 120%, 140%).'
        '</p>',
        unsafe_allow_html=True,
    )

    # Interactive simulation time series
    st.markdown("### Interactive: Hospitalization Rate Time Series")
    st.caption("500-day simulation from the model")

    hosp_cols = [c for c in df_hosp.columns if c != "Day"]
    scenario_labels = {
        "0.0bxm_0.0otv_1.0znv": "ZNV 100%",
        "0.0bxm_1.0otv_0.0znv": "OTV 100%",
        "0.5bxm_0.0otv_0.5znv": "BXM 50% + ZNV 50%",
        "0.5bxm_0.5otv_0.0znv": "BXM 50% + OTV 50%",
        "1.0bxm_0.0otv_0.0znv": "BXM 100%",
    }
    available = [c for c in scenario_labels if c in hosp_cols]

    selected_labels = st.multiselect(
        "Select scenarios to compare",
        options=list(scenario_labels.values()),
        default=[scenario_labels[c] for c in available[:3] if c in available],
    )
    label_to_col = {v: k for k, v in scenario_labels.items()}
    selected_cols = [label_to_col[label] for label in selected_labels if label_to_col[label] in hosp_cols]

    if selected_cols:
        fig_hosp = go.Figure()
        colors = ["#ef4444", "#3b82f6", "#10b981", "#f59e0b", "#8b5cf6"]
        for i, col in enumerate(selected_cols):
            display_name = scenario_labels.get(col, col)
            fig_hosp.add_trace(go.Scatter(
                x=df_hosp["Day"],
                y=df_hosp[col],
                mode="lines",
                name=display_name,
                line=dict(color=colors[i % len(colors)], width=2.5),
                hovertemplate="Day %{x}: %{y:.4f}<extra></extra>",
            ))
        # Add capacity thresholds
        fig_hosp.add_hline(y=1.0, line_dash="dot", line_color="#10b981",
                           annotation_text="100% capacity")
        fig_hosp.add_hline(y=1.2, line_dash="dot", line_color="#f59e0b",
                           annotation_text="120% capacity")
        fig_hosp.add_hline(y=1.4, line_dash="dot", line_color="#ef4444",
                           annotation_text="140% collapse")
        fig_hosp.update_layout(
            **PLOTLY_THEME,
            xaxis_title="Day (post-pandemic onset)",
            yaxis_title="Hospitalization Rate",
        )
        st.plotly_chart(fig_hosp, use_container_width=True)
    else:
        st.info("Select at least one scenario to display.")


# ============================================================
# PAGE: AI Agent Demo
# ============================================================
elif page == "AI Agent Demo":
    st.title("AI Agent Module")
    st.caption("Multi-provider LLM integration for public health decision support")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Provider Overview", "Literature Extraction", "NL Query", "Policy Report",
    ])

    with tab1:
        st.markdown("### Supported LLM Providers")
        try:
            from ai_agent.llm_interface import PROVIDER_REGISTRY
            provider_data = []
            for name, cfg in PROVIDER_REGISTRY.items():
                provider_data.append({
                    "Provider": name.upper(),
                    "Default Model": cfg.default_model,
                    "Context Window": f"{cfg.context_window:,} tokens",
                    "Vision": "Yes" if cfg.supports_vision else "No",
                    "API Format": "OpenAI-compatible",
                })
            st.dataframe(pd.DataFrame(provider_data), use_container_width=True, hide_index=True)
        except ImportError:
            st.error("Could not import ai_agent module.")

        st.markdown("### Quick Start")
        st.code("""from ai_agent import LLMClient

# Use MiMo (1M context window)
client = LLMClient(provider="mimo", model="mimo-v2.5-pro")
response = client.complete([
    {"role": "user", "content": "Analyze BXM stockpile strategy..."}
])
""", language="python")

    with tab2:
        st.markdown("### LLM-Powered Literature Parameter Extraction")
        st.caption("Extract epidemiological parameters from PubMed abstracts automatically")
        st.markdown("**Sample Input:**")
        st.code(
            "Influenza A(H3N2) vaccine effectiveness was estimated at 38% "
            "(95% CI: 28-47%) during the 2024-25 season. Oseltamivir resistance "
            "was detected in 2.8% of tested isolates. The serial interval was "
            "estimated at 3.2 days (IQR: 2.5-4.1).",
            language="text",
        )
        try:
            from ai_agent.literature_extractor import ExtractedParams
            sample_params = ExtractedParams(
                vaccine_efficacy=0.42,
                vaccine_efficacy_ci_low=0.31,
                vaccine_efficacy_ci_high=0.52,
                resistance_frequency=0.035,
                serial_interval=3.5,
                r0_mid=1.8,
                cost_per_course_bxm_hkd=480,
                cost_per_course_otv_hkd=120,
                confidence="high",
                source_citation="Cowling et al. 2026, HKU SPH",
            )
            st.markdown("**Extracted Parameters (Example):**")
            st.json(sample_params.to_dict())
            st.code("""from ai_agent import LiteratureExtractor

extractor = LiteratureExtractor(client)
params = extractor.extract(
    "VE was estimated at 42%...",
    source_name="PubMed Abstract"
)
print(params.vaccine_efficacy)  # -> 0.42
""", language="python")
        except ImportError:
            st.error("Could not import ai_agent.literature_extractor.")

    with tab3:
        st.markdown("### Natural Language Query Engine")
        st.caption("Ask questions about simulation results in plain English")
        example_queries = [
            "What is the ICER when BXM covers 30% of the population?",
            "Which strategy minimizes hospitalizations?",
            "Compare BXM-only vs OTV-only cost-effectiveness",
            "What resistance rate occurs at 80% BXM?",
            "Show the top 5 strategies by QALY gained",
        ]
        st.markdown("**Example Queries:**")
        for q in example_queries:
            st.markdown(f"- {q}")
        st.code("""from ai_agent import NLQueryEngine

engine = NLQueryEngine(client)
engine.load_results(scenario_results)
answer = engine.query("Which strategy is most cost-effective?", language="en")
print(answer["answer"])
""", language="python")

    with tab4:
        st.markdown("### Automated Policy Brief Generation")
        st.caption("AI generates structured policy reports with 5 sections")
        st.markdown("""
        The **PolicyReportGenerator** sends structured analysis data to the LLM with
        role-specific prompts. It generates 5 sections:
        1. **Executive Summary**
        2. **Key Findings**
        3. **Sensitivity Analysis**
        4. **Policy Recommendations**
        5. **Limitations**
        """)
        st.code("""from ai_agent import PolicyReportGenerator

generator = PolicyReportGenerator(client)
report = generator.generate_full_report(analysis_data, title="BXM Stockpile Strategy")
generator.save_markdown(report, "output/policy_brief.md")
""", language="python")


# ============================================================
# Footer
# ============================================================
st.markdown("---")
st.markdown(
    """
    <div style="text-align:center; color:#64748b; font-size:0.8rem;">
        <strong>AI-Powered Influenza Antiviral Stockpile Dashboard</strong> ·
        Built by <a href="https://github.com/RuohanCHEN01" style="color:#3b82f6; text-decoration:none;">Ruohan Chen</a> ·
        HKU WHO CC ·
        Chen et al. (2026) ·
        Python 3.11 | Streamlit | Plotly | LLM Agent
    </div>
    """,
    unsafe_allow_html=True,
)
