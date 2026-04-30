"""
AI-Powered Influenza Antiviral Stockpile Dashboard
====================================================
An interactive Streamlit dashboard for analyzing BXM vs OTV stockpile strategies
with integrated AI Agent capabilities.

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
    /* Override Streamlit defaults for a cleaner look */
    .main .block-container { padding-top: 1.5rem; }
    section[data-testid="stSidebar"] { background-color: #0f172a; }
    h1, h2, h3 { color: #e2e8f0; }
    .stMetricLabel { color: #94a3b8; font-size: 0.85rem; }
    .stMetricValue { color: #f1f5f9; }
    div[data-testid="stMetric"] { background-color: #1e293b; border-radius: 0.75rem; padding: 1rem; border: 1px solid #334155; }
    div.stDataFrame { border-radius: 0.75rem; }
</style>
""", unsafe_allow_html=True)


# ---- Data Loading ----
@st.cache_data
def load_data():
    """Load all CSV data files from Raw_Code_Data/."""
    cea_path = ROOT / "Raw_Code_Data" / "cost_analysis_FCFS_R0105_output_to_CEA_anti_n_vaccine_3month.csv"
    output_path = ROOT / "Raw_Code_Data" / "FCFS_R0105_output_to_CEA_anti_n_vaccine_3month.csv"
    hosp_path = ROOT / "Raw_Code_Data" / "FCFS_R0105_hospitalization_rates_matrix.csv"

    df_cea = pd.read_csv(cea_path)
    df_output = pd.read_csv(output_path)
    df_hosp = pd.read_csv(hosp_path)
    return df_cea, df_output, df_hosp


# ---- Load data ----
df_cea, df_output, df_hosp = load_data()

# Clean column names (strip whitespace)
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
            "Scenario Analysis",
            "Cost-Effectiveness",
            "Hospitalization",
            "AI Agent Demo",
        ],
        index=0,
        label_visibility="collapsed",
    )

    st.markdown("---")

    # Filters
    st.subheader("Filters")
    bxm_range = st.slider(
        "BXM Proportion Range",
        min_value=0.0,
        max_value=1.0,
        value=(0.0, 1.0),
        step=0.1,
        format="%0.0f%%",
    )
    otv_range = st.slider(
        "OTV Proportion Range",
        min_value=0.0,
        max_value=1.0,
        value=(0.0, 1.0),
        step=0.1,
        format="%0.0f%%",
    )

    # Apply filters
    mask = (
        (df_cea["BXM_proportion"] >= bxm_range[0])
        & (df_cea["BXM_proportion"] <= bxm_range[1])
        & (df_cea["OTV_proportion"] >= otv_range[0])
        & (df_cea["OTV_proportion"] <= otv_range[1])
    )
    df_filtered = df_cea[mask].copy()
    df_valid = df_filtered.dropna(subset=["Total_QALY"]).copy()

    st.markdown("---")
    st.caption("Built by Ruohan Chen | HKU WHO CC")
    st.caption(f"66 scenarios | {len(df_valid)} shown")


# ============================================================
# PAGE: Overview
# ============================================================
if page == "Overview":
    st.title("AI-Powered Influenza Antiviral Stockpile Dashboard")
    st.markdown(
        """
        An **AI-enhanced decision support system** for comparing Baloxavir (BXM) vs
        Oseltamivir (OTV) stockpile strategies in Hong Kong. Built with Streamlit +
        LLM Agent workflow.

        **Author:** Ruohan Chen (HKU PhD) | WHO Collaborating Centre for Infectious Disease Epidemiology and Control
        """
    )

    # Key metrics
    if len(df_valid) > 0:
        best = df_valid.loc[df_valid["Total_QALY"].idxmax()]
        baseline = df_cea.iloc[0]
        hosp_reduction = baseline["Hospitalization"] - best["Hospitalization"]
        total_savings = baseline["Total_cost"] - best["Total_cost"]

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Scenarios Analyzed", "66", "BXM/OTV/ZNV combos")
        with col2:
            st.metric("Optimal Strategy", f"BXM {int(best['BXM_proportion']*100)}%", f"OTV {int(best['OTV_proportion']*100)}%")
        with col3:
            st.metric("Total QALY", f"{best['Total_QALY']:,.0f}", "vs baseline")
        with col4:
            st.metric("Hosp. Averted", f"{hosp_reduction:,.0f}", "vs OTV-only")
        with col5:
            st.metric("Cost Savings", f"HKD {total_savings/1e9:.2f}B", "vs baseline")

    # Feature cards
    st.markdown("### AI-Powered Features")
    cols = st.columns(3)
    features = [
        ("LLM Literature Extraction", "Extract VE, R0, serial interval from PubMed abstracts"),
        ("Natural Language Query", "Ask questions about results in plain English"),
        ("Auto Policy Brief", "AI-generated reports with recommendations"),
        ("Multi-Provider LLM", "OpenAI, Claude, MiMo (1M ctx), DeepSeek"),
        ("Cost-Effectiveness Engine", "ICER, NMB, WTP analysis"),
        ("Interactive Visualizations", "Heatmaps, scatter plots, time series"),
    ]
    for i, (title, desc) in enumerate(features):
        with cols[i % 3]:
            st.markdown(
                f"""
                <div style="background:#1e293b; border:1px solid #334155; border-radius:0.75rem; padding:1.2rem; margin-bottom:0.8rem;">
                    <div style="font-weight:600; color:#e2e8f0; margin-bottom:0.4rem;">{title}</div>
                    <div style="font-size:0.85rem; color:#94a3b8;">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # AI Agent provider table
    st.markdown("### Supported LLM Providers")
    try:
        from ai_agent.llm_interface import PROVIDER_REGISTRY
        provider_data = []
        for name, cfg in PROVIDER_REGISTRY.items():
            provider_data.append({
                "Provider": name.upper(),
                "Default Model": cfg.default_model,
                "Context Window": f"{cfg.context_window:,}",
                "Vision": "Yes" if cfg.supports_vision else "No",
            })
        st.dataframe(
            pd.DataFrame(provider_data),
            use_container_width=True,
            hide_index=True,
        )
    except ImportError:
        st.warning("AI Agent module not loaded. Install dependencies to enable AI features.")


# ============================================================
# PAGE: Scenario Analysis
# ============================================================
elif page == "Scenario Analysis":
    st.title("Scenario Analysis")
    st.caption("Compare 66 BXM/OTV/ZNV stockpile combinations")

    if len(df_valid) == 0:
        st.warning("No scenarios match the current filter. Adjust the sidebar filters.")
        st.stop()

    # Scatter: Cost vs QALY
    st.markdown("### Cost vs QALY — All Scenarios")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_valid["Total_cost"] / 1e9,
        y=df_valid["Total_QALY"],
        mode="markers+text",
        marker=dict(
            size=10,
            color=df_valid["BXM_proportion"],
            colorscale=[[0, "#f59e0b"], [0.5, "#3b82f6"], [1, "#8b5cf6"]],
            showscale=True,
            colorbar=dict(title="BXM %", tickfont=dict(color="#94a3b8")),
            line=dict(color="rgba(255,255,255,0.3)", width=1),
        ),
        text=df_valid.apply(
            lambda r: f"BXM:{int(r['BXM_proportion']*100)}% OTV:{int(r['OTV_proportion']*100)}%",
            axis=1,
        ),
        textposition="top center",
        textfont=dict(size=7, color="#64748b"),
        hovertemplate="<b>%{text}</b><br>Cost: $%{x:.2f}B<br>QALY: %{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        **PLOTLY_THEME,
        xaxis_title="Total Cost (HKD Billion)",
        yaxis_title="Total QALY",
        title=dict(text="Colored by BXM Proportion", font=dict(size=13, color="#e2e8f0")),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Heatmaps: AR and RAR
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
        fig_ar.update_layout(**PLOTLY_THEME, xaxis_title="OTV", yaxis_title="BXM")
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
        fig_rar.update_layout(**PLOTLY_THEME, xaxis_title="OTV", yaxis_title="BXM")
        st.plotly_chart(fig_rar, use_container_width=True)

    # Top scenarios table
    st.markdown("### Top 10 Scenarios by QALY")
    top10 = df_valid.nlargest(10, "Total_QALY")[
        ["BXM_proportion", "OTV_proportion", "ZNV_proportion",
         "Total_QALY", "Hospitalization", "Death_65", "AR", "RAR"]
    ].copy()
    top10.columns = ["BXM %", "OTV %", "ZNV %", "Total QALY", "Hospitalizations", "Deaths (65+)", "Attack Rate", "Resistance AR"]
    top10["BXM %"] = (top10["BXM %"] * 100).astype(int).astype(str) + "%"
    top10["OTV %"] = (top10["OTV %"] * 100).astype(int).astype(str) + "%"
    top10["ZNV %"] = (top10["ZNV %"] * 100).astype(int).astype(str) + "%"
    st.dataframe(top10.reset_index(drop=True), use_container_width=True, hide_index=True)


# ============================================================
# PAGE: Cost-Effectiveness
# ============================================================
elif page == "Cost-Effectiveness":
    st.title("Cost-Effectiveness Analysis")
    st.caption("ICER, NMB, WTP threshold analysis")

    if len(df_valid) == 0:
        st.warning("No scenarios match the current filter.")
        st.stop()

    best = df_valid.loc[df_valid["Total_QALY"].idxmax()]
    baseline = df_cea.iloc[0]
    total_savings = baseline["Total_cost"] - best["Total_cost"]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Best Strategy Cost", f"HKD {best['Total_cost']/1e9:.2f}B")
    with col2:
        st.metric("Cost Savings vs Baseline", f"HKD {total_savings/1e9:.2f}B",
                  f"{total_savings/baseline['Total_cost']*100:.1f}%")
    with col3:
        st.metric("WTP Threshold", "1x GDP", "HKD 422,242 per QALY")

    # CE Plane
    st.markdown("### Cost-Effectiveness Plane")
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
        text=df_valid.apply(
            lambda r: f"BXM:{int(r['BXM_proportion']*100)}%",
            axis=1,
        ),
        hovertemplate="<b>%{text}</b><br>Inc. Cost: $%{x:,.0f}<br>Inc. QALY: %{y:,.0f}<extra></extra>",
    ))
    # Reference lines
    fig_ce.add_hline(y=0, line_dash="dash", line_color="#334155")
    fig_ce.add_vline(x=0, line_dash="dash", line_color="#334155")
    fig_ce.update_layout(
        **PLOTLY_THEME,
        xaxis_title="Incremental Cost (HKD)",
        yaxis_title="Incremental QALY",
        title=dict(text="vs OTV-only Baseline", font=dict(size=13, color="#e2e8f0")),
    )
    st.plotly_chart(fig_ce, use_container_width=True)

    # Cost breakdown bar
    st.markdown("### Cost & Hospitalization by Strategy")
    bar_df = df_valid.head(12).copy()
    bar_df["scenario"] = bar_df.apply(
        lambda r: f"BXM:{int(r['BXM_proportion']*100)}%", axis=1
    )
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=bar_df["scenario"], y=bar_df["Total_cost"] / 1e9,
        name="Total Cost (HKD B)", marker_color="#3b82f6",
    ))
    fig_bar.add_trace(go.Bar(
        x=bar_df["scenario"], y=bar_df["Hospitalization"] / 1000,
        name="Hospitalizations (K)", marker_color="#ef4444",
        yaxis="y2",
    ))
    fig_bar.update_layout(
        **PLOTLY_THEME,
        barmode="group",
        xaxis_title="Stockpile Strategy",
        yaxis_title="Total Cost (HKD Billion)",
        yaxis2=dict(title="Hospitalizations (K)", side="right", overlaying="y",
                     gridcolor="transparent", color="#94a3b8"),
    )
    st.plotly_chart(fig_bar, use_container_width=True)


# ============================================================
# PAGE: Hospitalization
# ============================================================
elif page == "Hospitalization":
    st.title("Hospitalization Rate Time Series")
    st.caption("500-day simulation — Strategy Comparison")

    st.markdown("""
    **Key Insight:** BXM 100% strategy achieves the lowest peak hospitalization rate
    (0.90 to 0.30), but OTV 100% baseline shows prolonged high rates.
    Mixed strategies (BXM 50%) provide balanced protection with manageable resistance risk.
    """)

    # Let user pick scenarios to compare
    hosp_cols = [c for c in df_hosp.columns if c != "Day"]
    scenario_labels = {
        "0.0bxm_0.0otv_1.0znv": "OTV 0% + ZNV 100% (Baseline)",
        "0.0bxm_1.0otv_0.0znv": "OTV 100% (Baseline)",
        "0.5bxm_0.0otv_0.5znv": "BXM 50% + ZNV 50%",
        "0.5bxm_0.5otv_0.0znv": "BXM 50% + OTV 50%",
        "1.0bxm_0.0otv_0.0znv": "BXM 100%",
    }
    available = [c for c in scenario_labels if c in hosp_cols]

    # Multi-select
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
            label = [k for k, v in scenario_labels.items() if v == col or k == col][0]
            display_name = scenario_labels.get(col, col)
            fig_hosp.add_trace(go.Scatter(
                x=df_hosp["Day"],
                y=df_hosp[col],
                mode="lines",
                name=display_name,
                line=dict(color=colors[i % len(colors)], width=2.5),
                hovertemplate="Day %{x}: %{y:.4f}<extra></extra>",
            ))
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

    # Tab layout
    tab1, tab2, tab3, tab4 = st.tabs([
        "Provider Overview", "Literature Extraction", "NL Query", "Policy Report",
    ])

    # ---- Tab 1: Provider Overview ----
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
client = LLMClient(provider="mimo", model="MiMo-V2.5-Pro")
response = client.complete([
    {"role": "user", "content": "Analyze BXM stockpile strategy..."}
])
""", language="python")

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
params = extractor.extract(
    "VE was estimated at 42%...",
    source_name="PubMed Abstract"
)
print(params.vaccine_efficacy)  # → 0.42
print(params.confidence)        # → "high"
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

answer = engine.query(
    "Which strategy is most cost-effective?",
    language="en"  # or "zh"
)
print(answer["answer"])
print(answer["confidence"])
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

        # Pipeline visualization
        st.markdown("**Report Generation Pipeline:**")
        cols = st.columns(5)
        pipeline_steps = [
            ("Analysis Data", "data"),
            ("LLM Agent", "agent"),
            ("Markdown", "markdown"),
            ("PDF Export", "pdf"),
            ("Distribution", "share"),
        ]
        for i, (label, icon) in enumerate(pipeline_steps):
            with cols[i]:
                st.markdown(
                    f"""
                    <div style="text-align:center; padding:1rem; background:#1e293b;
                    border-radius:0.75rem; border:1px solid #334155;">
                        <div style="font-size:1.2rem; font-weight:600; color:#e2e8f0;">{label}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


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
        Python 3.11 | Streamlit | Plotly | LLM Agent
    </div>
    """,
    unsafe_allow_html=True,
)
