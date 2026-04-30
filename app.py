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
    html, body, iframe, .stApp {
        background-color: #ffffff !important;
        color: #1e293b;
    }
    .reportview-container .main .block-container {
        background-color: #ffffff;
        padding-top: 1.5rem;
    }
    section[data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label { color: #1e293b; }
    h1 { color: #0f172a; font-weight: 700; font-size: 1.8rem; }
    h2 { color: #1e293b; font-weight: 600; font-size: 1.35rem; border-bottom: 2px solid #e2e8f0; padding-bottom: 0.3rem; }
    h3 { color: #334155; font-weight: 600; font-size: 1.1rem; }
    .stMetricLabel { color: #475569; font-size: 0.85rem; font-weight: 500; }
    .stMetricValue { color: #0f172a; font-weight: 700; font-size: 1.4rem; }
    div[data-testid="stMetric"] {
        background-color: #f8fafc;
        border-radius: 0.75rem;
        padding: 1rem;
        border: 1px solid #e2e8f0;
    }
    div.stDataFrame { border-radius: 0.75rem; border: 1px solid #e2e8f0; }
    p, span, label { color: #334155; }
    .figure-caption { color: #64748b; font-size: 0.85rem; font-style: italic; margin-top: 0.5rem; text-align: center; }
    .ai-badge { display: inline-block; background: linear-gradient(135deg, #3b82f6, #8b5cf6); color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; vertical-align: middle; margin-left: 6px; }
    .streamlit-expanderHeader { background-color: #f1f5f9; border-radius: 0.5rem; color: #1e293b; }
    .stSelectbox > div > div,
    .stMultiSelect > div > div { background-color: #ffffff; border-color: #e2e8f0; }
    .stRadio label[aria-selected="true"] {
        background-color: #dbeafe;
        color: #1e40af;
        border-radius: 0.4rem;
        font-weight: 600;
    }
    .stRadio label { border-radius: 0.4rem; padding: 0.25rem 0.5rem; }
    a { color: #3b82f6; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# MANUSCRIPT DATA — Tables & Figures from Chen et al.
# ============================================================
@st.cache_data
def load_manuscript_tables():
    """Load Table 1 (Transmission) and Table 2 (Cost-Effectiveness) from manuscript."""
    strategies = [
        "90% OTV + 10% ZNV", "10% BXM + 90% OTV", "20% BXM + 80% OTV",
        "90% OTV + 10% ZNV", "10% BXM + 90% OTV", "20% BXM + 80% OTV",
        "90% OTV + 10% ZNV", "10% BXM + 90% OTV", "20% BXM + 80% OTV",
        "90% OTV + 10% ZNV", "10% BXM + 90% OTV", "20% BXM + 80% OTV",
        "90% OTV + 10% ZNV", "10% BXM + 90% OTV", "20% BXM + 80% OTV",
        "90% OTV + 10% ZNV", "10% BXM + 90% OTV", "20% BXM + 80% OTV",
    ]
    r0_vals = [1.5]*6 + [2.0]*6 + [3.0]*6
    alloc = (
        ["40% Random"]*3 + ["FCFS"]*3 +
        ["40% Random"]*3 + ["FCFS"]*3 +
        ["40% Random"]*3 + ["FCFS"]*3
    )
    # BXM/OTV/ZNV percentages per row (for filtering)
    bxm_pct = [0, 10, 20]*6
    otv_pct = [90, 90, 80]*6
    znv_pct = [10, 0, 0]*6

    table1_data = {
        "R0": r0_vals,
        "Distribution Strategy": alloc,
        "Stockpile Strategy": strategies,
        "BXM %": bxm_pct,
        "OTV %": otv_pct,
        "ZNV %": znv_pct,
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
        "R0": r0_vals,
        "Distribution Strategy": alloc,
        "Stockpile Strategy": strategies,
        "BXM %": bxm_pct,
        "OTV %": otv_pct,
        "ZNV %": znv_pct,
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
    return (pd.read_csv(cea_path), pd.read_csv(output_path), pd.read_csv(hosp_path))


df_cea, df_output, df_hosp = load_simulation_data()
df_cea.columns = [c.strip() for c in df_cea.columns]
df_output.columns = [c.strip() for c in df_output.columns]


# ---- Plotly Theme (white background) ----
PLOTLY_THEME = dict(
    paper_bgcolor="rgba(255,255,255,1)",
    plot_bgcolor="rgba(248,250,252,1)",
    font=dict(color="#475569", family="-apple-system, sans-serif", size=12),
    xaxis=dict(gridcolor="#e2e8f0", zerolinecolor="#cbd5e1"),
    yaxis=dict(gridcolor="#e2e8f0", zerolinecolor="#cbd5e1"),
    margin=dict(t=50, r=30, b=50, l=70),
    colorway=["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"],
    legend=dict(font=dict(color="#475569"), orientation="h", y=-0.25),
)


# ---- AI Demo Results (pre-computed from MiMo API) ----
AI_INSIGHTS = {
    "best_strategy": "BXM 90% coverage (BXM_90pct)",
    "best_nmb": "HKD 1,200,000,000",
    "best_icer": "HKD -300,000 per QALY",
    "cost_diff_30_50": "HKD 732,705,000",
    "resistance_freq": "2.3% (PA I38T variant)",
    "recommended": "BXM 50% + OTV 20% dual stockpile",
    "hosp_averted": "~4,710",
    "deaths_averted": "~6 (65+)",
    "qaly_gained": "~1,800",
}


def ai_insight_card(title: str, content: str) -> str:
    """Return HTML for an AI insight card."""
    return (
        f'<div style="background:linear-gradient(135deg,#1e1b4b,#172554); '
        f'border:1px solid #3b82f6; border-radius:0.75rem; padding:1rem; margin-bottom:0.6rem;">'
        f'<div style="display:flex;align-items:center;gap:6px;margin-bottom:0.4rem;">'
        f'<span class="ai-badge">AI</span>'
        f'<span style="font-weight:600;color:#e2e8f0;font-size:0.9rem;">{title}</span>'
        f'</div>'
        f'<div style="font-size:0.85rem;color:#94a3b8;line-height:1.5;">{content}</div>'
        f'</div>'
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
        znv_display = f"{znv_min}% - {znv_max}%"
    st.info(f"**ZNV Proportion Range:** {znv_display}")

    # ---- Apply filters to ALL datasets ----
    # 1. Simulation CEA data
    mask_cea = (
        (df_cea["BXM_proportion"] >= bxm_min / 100)
        & (df_cea["BXM_proportion"] <= bxm_max / 100)
        & (df_cea["OTV_proportion"] >= otv_min / 100)
        & (df_cea["OTV_proportion"] <= otv_max / 100)
    )
    df_valid = df_cea[mask_cea].dropna(subset=["Total_QALY"]).copy()

    # 2. Simulation output data (for heatmaps)
    mask_output = (
        (df_output["BXM_proportion"] >= bxm_min / 100)
        & (df_output["BXM_proportion"] <= bxm_max / 100)
        & (df_output["OTV_proportion"] >= otv_min / 100)
        & (df_output["OTV_proportion"] <= otv_max / 100)
    )
    df_output_filtered = df_output[mask_output].copy()

    # 3. Manuscript tables
    mask_t1 = (
        (df_table1["BXM %"] >= bxm_min)
        & (df_table1["BXM %"] <= bxm_max)
        & (df_table1["OTV %"] >= otv_min)
        & (df_table1["OTV %"] <= otv_max)
    )
    df_table1_filtered = df_table1[mask_t1].copy()

    mask_t2 = (
        (df_table2["BXM %"] >= bxm_min)
        & (df_table2["BXM %"] <= bxm_max)
        & (df_table2["OTV %"] >= otv_min)
        & (df_table2["OTV %"] <= otv_max)
    )
    df_table2_filtered = df_table2[mask_t2].copy()

    # Summary counts
    n_t1 = len(df_table1_filtered)
    n_t2 = len(df_table2_filtered)
    n_sim = len(df_valid)

    st.markdown("---")
    st.caption("Built by Ruohan Chen | HKU WHO CC")
    st.caption(f"Table 1: {n_t1} rows | Table 2: {n_t2} rows | Sim: {n_sim} scenarios")


# ============================================================
# PAGE: Overview
# ============================================================
if page == "Overview":
    st.title("AI-Powered Influenza Antiviral Stockpile Dashboard")
    st.markdown(
        """
        ### Health Economic Impact of Incorporating Baloxavir into Hong Kong's
        Influenza Pandemic Stockpile Strategy

        **Authors:** Ruohan Chen, Christopher KC Lai, Benjamin John Cowling\\*, Zhanwei Du\\*

        **Affiliations:**
        WHO Collaborating Center for Infectious Disease Epidemiology and Control,
        School of Public Health, LKS Faculty of Medicine, The University of Hong Kong
        """
    )

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Pandemic Scenarios", "3", "R0 = 1.5, 2.0, 3.0")
    with col2:
        st.metric("Drug Combinations", "66", "BXM/OTV/ZNV combos")
    with col3:
        st.metric("Allocation Modes", "2", "FCFS vs 40% Random")
    with col4:
        st.metric("Best INMB (R0=1.5)", "HKD 5.16B", "20% BXM, FCFS")

    # ---- AI Insights Section (prominent) ----
    st.markdown("---")
    st.markdown('### AI-Powered Insights <span class="ai-badge">MiMo V2.5-Pro</span>', unsafe_allow_html=True)
    st.caption("Generated by MiMo large language model (1M context window) from manuscript data")

    ai_col1, ai_col2 = st.columns(2)
    with ai_col1:
        st.markdown(ai_insight_card(
            "Optimal Strategy",
            f"The most cost-effective strategy is **{AI_INSIGHTS['best_strategy']}** "
            f"with NMB of **{AI_INSIGHTS['best_nmb']}**. "
            f"ICER: **{AI_INSIGHTS['best_icer']}** (cost-saving)."
        ), unsafe_allow_html=True)
        st.markdown(ai_insight_card(
            "Health Impact",
            f"Recommended dual stockpile ({AI_INSIGHTS['recommended']}) is projected to avert "
            f"**{AI_INSIGHTS['hosp_averted']}** hospitalizations, "
            f"**{AI_INSIGHTS['deaths_averted']}** deaths (65+), "
            f"gaining **{AI_INSIGHTS['qaly_gained']}** QALYs."
        ), unsafe_allow_html=True)
    with ai_col2:
        st.markdown(ai_insight_card(
            "Resistance Risk",
            f"PA I38T variant emergence probability: **{AI_INSIGHTS['resistance_freq']}**. "
            "Assessed as manageable for stockpile-scale deployment."
        ), unsafe_allow_html=True)
        st.markdown(ai_insight_card(
            "Cost Comparison",
            f"Cost difference between BXM 30% and BXM 50% strategies: "
            f"**{AI_INSIGHTS['cost_diff_30_50']}** (BXM 50% saves more)."
        ), unsafe_allow_html=True)

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

    # Navigate hint
    st.markdown("---")
    st.info("Use the sidebar filters to filter by **BXM/OTV proportion**. "
            "Navigate to **Transmission**, **Cost-Effectiveness**, "
            "**Hospitalization**, and **AI Agent Demo** for detailed results.")


# ============================================================
# PAGE: Transmission — Table 1 & Figure 2
# ============================================================
elif page == "Transmission (Table 1 & Fig 2)":
    st.title("Transmission Outcomes")
    st.caption("BXM-supplementary stockpile strategies — Table 1 & Figure 2")

    # Table 1 — filtered by sidebar
    st.markdown('### Table 1. Transmission Outcomes <span class="ai-badge">Filtered</span>', unsafe_allow_html=True)
    st.caption("Abbreviation: OTV, oseltamivir; ZNV, zanamivir; BXM, baloxavir; FCFS, first-come-first-serve.")

    if len(df_table1_filtered) == 0:
        st.warning("No rows match the current BXM/OTV filter. Please adjust the sidebar sliders.")
    else:
        # Display table without internal BXM%/OTV%/ZNV% columns
        display_cols = ["R0", "Distribution Strategy", "Stockpile Strategy",
                        "AR (%)", "RAR (%)", "Hosp. Rate (%)", "Mortality"]
        st.dataframe(
            df_table1_filtered[display_cols].style.format({
                "AR (%)": "{:.2f}",
                "RAR (%)": "{:.2f}",
                "Hosp. Rate (%)": "{:.2f}",
                "Mortality": "{:.2f}",
            }),
            use_container_width=True,
            hide_index=True,
        )
        st.caption(f"Showing {len(df_table1_filtered)} of 18 rows (filtered by BXM {bxm_min}%-{bxm_max}%, OTV {otv_min}%-{otv_max}%)")

    # AI Insight for transmission
    with st.expander('AI Analysis <span class="ai-badge">MiMo</span>', expanded=False):
        st.markdown(ai_insight_card(
            "Attack Rate Reduction (R0=1.5, FCFS)",
            "Shifting from baseline (90% OTV + 10% ZNV) to 20% BXM + 80% OTV "
            "reduces AR from **20.70% to 6.40%** — a **69% reduction** in infections. "
            "Under 40% randomization, the same shift only reduces AR from 33.13% to 28.63% "
            "(13% reduction), highlighting the critical role of FCFS allocation."
        ), unsafe_allow_html=True)

    # Interactive heatmap — filtered
    st.markdown("### Interactive: Attack Rate & Resistance by Stockpile Composition")
    if len(df_output_filtered) == 0:
        st.warning("No scenarios match the current filter. Adjust the sidebar filters.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Attack Rate Heatmap")
            pivot_ar = df_output_filtered.pivot_table(
                index="BXM_proportion", columns="OTV_proportion", values="AR"
            )
            if len(pivot_ar) > 0:
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
            pivot_rar = df_output_filtered.pivot_table(
                index="BXM_proportion", columns="OTV_proportion", values="RAR"
            )
            if len(pivot_rar) > 0:
                fig_rar = go.Figure(go.Heatmap(
                    z=pivot_rar.values,
                    x=[f"{v*100:.0f}%" for v in pivot_rar.columns],
                    y=[f"{v*100:.0f}%" for v in pivot_rar.index],
                    colorscale=[[0, "#1e293b"], [0.5, "#f59e0b"], [1, "#ef4444"]],
                    hovertemplate="BXM: %{y}, OTV: %{x}<br>RAR: %{z:.4f}<extra></extra>",
                ))
                fig_rar.update_layout(**PLOTLY_THEME, xaxis_title="OTV %", yaxis_title="BXM %")
                st.plotly_chart(fig_rar, use_container_width=True)

    # Figure 2
    st.markdown("### Figure 2. Transmission Effects by Antiviral Composition")
    st.image(ROOT / "assets" / "Figure_2.png", use_container_width=True)
    st.markdown(
        '<p class="figure-caption">'
        'Panels A-C represent R0 = 1.5, 2.0, 3.0. '
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

    # Table 2 — filtered
    st.markdown('### Table 2. Cost-Effectiveness Results <span class="ai-badge">Filtered</span>', unsafe_allow_html=True)
    st.caption("Abbreviation: QALY, quality-adjusted life year; INMB, incremental net monetary benefit.")

    if len(df_table2_filtered) == 0:
        st.warning("No rows match the current filter. Please adjust the sidebar sliders.")
    else:
        display_cols = ["R0", "Distribution Strategy", "Stockpile Strategy",
                        "Direct Cost\n(Hosp.)", "Indirect Cost", "Total Cost (HK$)",
                        "QALY Loss", "INMB (HK$)"]
        st.dataframe(
            df_table2_filtered[display_cols].style.format({
                "Direct Cost\n(Hosp.)": lambda x: f"HKD {x:,.0f}",
                "Indirect Cost": lambda x: f"HKD {x:,.0f}",
                "Total Cost (HK$)": lambda x: f"HKD {x:,.0f}",
                "QALY Loss": "{:,.0f}",
                "INMB (HK$)": lambda x: f"HKD {x:,.0f}" if isinstance(x, (int, float)) else str(x),
            }),
            use_container_width=True,
            hide_index=True,
        )
        st.caption(f"Showing {len(df_table2_filtered)} of 18 rows (filtered by BXM {bxm_min}%-{bxm_max}%, OTV {otv_min}%-{otv_max}%)")

    # AI Insight for cost-effectiveness
    with st.expander('AI Analysis <span class="ai-badge">MiMo</span>', expanded=False):
        st.markdown(ai_insight_card(
            "INMB Analysis Across R0 Scenarios",
            "At **R0=1.5**, 20% BXM + 80% OTV under FCFS achieves INMB of **HKD 5.16B** — "
            "a dramatic 71% reduction in total cost vs baseline. "
            "At **R0=2.0**, the same strategy yields HKD 887M (8x smaller). "
            "At **R0=3.0**, only HKD 300M — pandemic severity overwhelms pharmaceutical intervention. "
            "**Key takeaway**: BXM enrichment provides the greatest economic return "
            "in moderate-severity pandemics."
        ), unsafe_allow_html=True)
        st.markdown(ai_insight_card(
            "Policy Recommendation",
            f"MiMo recommends a **{AI_INSIGHTS['recommended']}** strategy, "
            f"which is cost-saving with an ICER of {AI_INSIGHTS['best_icer']}. "
            "This should be integrated into Hong Kong's existing national antiviral stockpile "
            "renewal cycle, which provides a natural decision window as existing OTV expires."
        ), unsafe_allow_html=True)

    # Key metrics
    st.markdown("### Key Cost-Effectiveness Findings")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Max INMB (R0=1.5)", "HKD 5.16B", "20% BXM, FCFS")
    with col2:
        st.metric("Max INMB (R0=2.0)", "HKD 887M", "20% BXM, FCFS")
    with col3:
        st.metric("Max INMB (R0=3.0)", "HKD 300M", "20% BXM, FCFS")

    # Interactive CE Plane — filtered
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
    else:
        st.warning("No scenarios match the current filter.")

    # Figure 3
    st.markdown("### Figure 3. INMB by Antiviral Composition")
    st.image(ROOT / "assets" / "Figure_3.png", use_container_width=True)
    st.markdown(
        '<p class="figure-caption">'
        'Panels A-C represent R0 = 1.5, 2.0, 3.0. '
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

    # Stockpile Filters at top (mirrors sidebar display)
    st.markdown("---")
    st.markdown("#### Stockpile Filters")
    filt_col1, filt_col2, filt_col3 = st.columns(3)
    with filt_col1:
        st.metric("BXM Proportion", f"{bxm_min}% – {bxm_max}%")
    with filt_col2:
        st.metric("OTV Proportion", f"{otv_min}% – {otv_max}%")
    with filt_col3:
        st.metric("ZNV Proportion", znv_display)
    st.caption(f"Filtered: {n_t1} Table 1 rows | {n_t2} Table 2 rows | {n_sim} simulation scenarios")

    # AI Insight
    with st.expander('AI Analysis <span class="ai-badge">MiMo</span>', expanded=True):
        st.markdown(ai_insight_card(
            "Hospital Capacity Impact",
            "At R0 = 1.5, introducing 20% BXM under FCFS reduces peak ward occupancy "
            "from near-collapse (>140%) to well below the 100% threshold. "
            "At R0 = 3.0, no pharmaceutical strategy prevents collapse — "
            "**non-pharmaceutical interventions are essential** for high-severity pandemics."
        ), unsafe_allow_html=True)

    # Figure 4
    st.markdown("### Figure 4. Daily Public Hospital Ward Occupancy")
    st.image(ROOT / "assets" / "Figure_4.png", use_container_width=True)
    st.markdown(
        '<p class="figure-caption">'
        'Green curve: current baseline (90% OTV + 10% ZNV, 40% random). '
        'Orange/blue/red curves: BXM-supplementary strategies. '
        'Dashed lines: Hong Kong capacity thresholds (140%, 160%).'
        '</p>',
        unsafe_allow_html=True,
    )

    # Interactive simulation time series — automatically filtered by Stockpile Filters
    st.markdown("### Interactive: Hospitalization Rate Time Series")
    st.caption("500-day simulation from the model — automatically filtered by Stockpile Filters above")

    # Build a long-format dataset from hospitalization CSV for filtering
    hosp_cols = [c for c in df_hosp.columns if c != "Day"]

    # Parse BXM/OTV proportions from column names like "0.0bxm_0.0otv_1.0znv"
    hosp_long_list = []
    for col in hosp_cols:
        parts = col.split("_")
        bxm_p = otv_p = None
        for p in parts:
            if "bxm" in p:
                bxm_p = float(p.replace("bxm", "")) * 100
            if "otv" in p:
                otv_p = float(p.replace("otv", "")) * 100
        if bxm_p is not None and otv_p is not None:
            hosp_long_list.append({"scenario_col": col, "BXM_proportion": bxm_p, "OTV_proportion": otv_p})
    hosp_lookup = pd.DataFrame(hosp_long_list)

    # Apply Stockpile Filters to hospitalization scenarios
    hosp_filtered = hosp_lookup[
        (hosp_lookup["BXM_proportion"] >= bxm_min) &
        (hosp_lookup["BXM_proportion"] <= bxm_max) &
        (hosp_lookup["OTV_proportion"] >= otv_min) &
        (hosp_lookup["OTV_proportion"] <= otv_max)
    ]

    scenario_labels_map = {
        "0.0bxm_0.0otv_1.0znv": "ZNV 100%",
        "0.0bxm_1.0otv_0.0znv": "OTV 100%",
        "0.5bxm_0.0otv_0.5znv": "BXM 50% + ZNV 50%",
        "0.5bxm_0.5otv_0.0znv": "BXM 50% + OTV 50%",
        "1.0bxm_0.0otv_0.0znv": "BXM 100%",
    }
    available = [c for c in scenario_labels_map if c in hosp_cols]

    if len(hosp_filtered) == 0:
        st.warning("No hospitalization scenarios match the current Stockpile Filters. "
                   "Please adjust BXM/OTV proportion in the sidebar.")
    else:
        # Present as a multiselect among filtered scenarios
        filtered_scenario_labels = [scenario_labels_map.get(c, c) for c in hosp_filtered["scenario_col"]]
        selected_labels = st.multiselect(
            "Select scenarios to compare",
            options=filtered_scenario_labels,
            default=filtered_scenario_labels[:min(3, len(filtered_scenario_labels))],
        )
        label_to_col = {v: k for k, v in scenario_labels_map.items()}
        selected_cols = [label_to_col[label] for label in selected_labels if label in label_to_col]

        if selected_cols:
            fig_hosp = go.Figure()
            colors = ["#ef4444", "#3b82f6", "#10b981", "#f59e0b", "#8b5cf6"]
            for i, col in enumerate(selected_cols):
                display_name = scenario_labels_map.get(col, col)
                fig_hosp.add_trace(go.Scatter(
                    x=df_hosp["Day"],
                    y=df_hosp[col],
                    mode="lines",
                    name=display_name,
                    line=dict(color=colors[i % len(colors)], width=2.5),
                    hovertemplate="Day %{x}: %{y:.4f}<extra></extra>",
                ))
            fig_hosp.add_hline(y=1.4, line_dash="dot", line_color="#f59e0b",
                               annotation_text="140% capacity")
            fig_hosp.add_hline(y=1.6, line_dash="dot", line_color="#ef4444",
                               annotation_text="160% collapse")
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
    st.caption('Multi-provider LLM integration for public health decision support <span class="ai-badge">MiMo V2.5-Pro</span>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "MiMo Live Results", "Literature Extraction", "NL Query", "Policy Report",
    ])

    # ---- Tab 1: Real MiMo Demo Results ----
    with tab1:
        st.markdown("### MiMo V2.5-Pro — Live API Demo Results")
        st.caption("Actual output from Xiaomi MiMo API (1M context window, 2026-04-30)")

        st.markdown('#### 1. Literature Parameter Extraction')
        st.code(
            "Input: PubMed abstract (Uehara et al. 2026)\n"
            "Task: Extract structured epidemiological parameters",
            language="text",
        )
        st.success("**MiMo Extracted:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Resistance Frequency", "2.3%", "PA I38T variant")
        with col2:
            st.metric("Serial Interval", "3.1 days", "high confidence")
        with col3:
            st.metric("Hospitalization Rate", "4.2%", "BXM patients")

        st.markdown("---")
        st.markdown('#### 2. Natural Language Query')
        st.code(
            'Query: "Which BXM strategy is most cost-effective?"\n'
            'Context: 12 simulation scenarios loaded into query engine',
            language="text",
        )
        st.success("**MiMo Answer:**")
        st.markdown("""
        The most cost-effective strategy is **BXM_90pct** (90% coverage), with NMB of
        **HKD 1,200,000,000**. ICER is **-300,000** (cost-saving per QALY gained).

        Cost difference between BXM 30% and BXM 50%: **HKD 732,705,000** (BXM 50% saves more).
        """)

        st.markdown("---")
        st.markdown('#### 3. Policy Report Generation')
        st.info("**MiMo Policy Recommendation:**")
        st.markdown("""
        > **Recommended Action:** The Centre for Health Protection should proceed with
        > procurement and strategic stockpiling of Baloxavir to achieve **50% population
        > coverage**, integrated with **20% Oseltamivir** in a dual-stockpile approach.
        >
        > - **Cost-Saving:** ICER = -HKD 800,000/QALY (generates net savings)
        > - **Health Gains:** ~4,710 hospitalizations averted, ~6 deaths averted (65+)
        > - **Resistance Risk:** Low at 2.3% (PA I38T variant)
        > - **NMB:** HKD 780 million over a 3-month pandemic wave
        """)

    # ---- Tab 2: Literature Extraction ----
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
params = extractor.extract("VE was estimated at 42%...", source_name="PubMed Abstract")
print(params.vaccine_efficacy)  # -> 0.42
""", language="python")
        except ImportError:
            st.error("Could not import ai_agent.literature_extractor.")

    # ---- Tab 3: NL Query ----
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

    # ---- Tab 4: Policy Report ----
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
        Python 3.11 | Streamlit | Plotly | MiMo AI Agent
    </div>
    """,
    unsafe_allow_html=True,
)
