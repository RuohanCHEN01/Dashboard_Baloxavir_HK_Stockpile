"""
Example: Using Xiaomi MiMo V2.5 for Literature Parameter Extraction

This script demonstrates how to use the MiMo V2.5-Pro model through the
ai_agent module to extract epidemiological parameters from scientific text.

Requirements:
    pip install openai pyyaml

    Set environment variable:
    export MIMO_API_KEY="your_mimo_api_key"

    Or create a .env file with:
    MIMO_API_KEY=your_mimo_api_key
"""

from ai_agent import LLMClient, LiteratureExtractor, NLQueryEngine, PolicyReportGenerator


def demo_mimo_extraction():
    """Demo: Extract parameters from a PubMed-style abstract using MiMo V2.5."""

    # Initialize MiMo client
    # API keys are loaded from MIMO_API_KEY environment variable automatically
    client = LLMClient(
        provider="mimo",
        model="mimo-v2.5-pro",   # 1M context window
        temperature=0.1,          # Low temperature for factual extraction
    )

    print(f"Connected to: {client.info}")
    print(f"Context window: {client.info['context_window']:,} tokens")
    print()

    # Sample PubMed abstract for extraction
    abstract = """
    Title: Effectiveness of Baloxavir Marboxil in High-Risk Influenza Patients
    Authors: Uehara T, et al. (2026)

    Background: Baloxavir marboxil (BXM) is a cap-dependent endonuclease inhibitor
    with a single-dose regimen for influenza treatment. We assessed its effectiveness
    in a prospective cohort of high-risk patients during the 2025-26 influenza season.

    Methods: We enrolled 1,247 patients aged >= 65 years or with underlying conditions
    across 23 hospitals in Hong Kong. Patients received either BXM (single 40mg dose)
    or oseltamivir (OTV, 75mg twice daily for 5 days) within 48 hours of symptom onset.
    The primary endpoint was time to alleviation of symptoms. Viral resistance was
    assessed by serial RT-PCR and next-generation sequencing.

    Results: The median time to symptom alleviation was 53.7 hours (95% CI: 49.2-58.1)
    for BXM vs 73.2 hours (95% CI: 68.1-78.3) for OTV (p<0.001). BXM showed superior
    viral reduction at 48 hours (mean log10 decrease: 3.2 vs 1.8, p<0.001).
    The emergence of PA I38T resistance variant was observed in 2.3% (14/612) of BXM
    patients. The serial interval was estimated at 3.1 days (95% CI: 2.7-3.5).
    Hospitalization rate was 4.2% for BXM vs 6.8% for OTV (RR 0.62, 95% CI: 0.41-0.93).
    The incremental cost per QALY gained was HKD 45,200 (95% CI: 28,500-78,300).

    Conclusions: BXM demonstrated superior efficacy with a favorable cost-effectiveness
    profile in high-risk influenza patients. Resistance emergence remains low.
    """

    # Extract structured parameters
    extractor = LiteratureExtractor(client)

    print("=" * 60)
    print("Extracting parameters from abstract...")
    print("=" * 60)

    params = extractor.extract(abstract, source_name="Uehara et al. 2026")

    print(f"\nExtraction confidence: {params.confidence}")
    print(f"Source: {params.source_citation}")
    print()

    # Display extracted parameters
    if params.vaccine_efficacy is not None:
        print(f"  Vaccine/Drug effectiveness: {params.vaccine_efficacy}")
    if params.resistance_frequency is not None:
        print(f"  Resistance frequency: {params.resistance_frequency}")
    if params.serial_interval is not None:
        print(f"  Serial interval: {params.serial_interval} days")
    if params.hospitalization_rate is not None:
        print(f"  Hospitalization rate: {params.hospitalization_rate}")
    if params.case_fatality_rate is not None:
        print(f"  Case fatality rate: {params.case_fatality_rate}")

    print()

    # Export as JSON
    print("JSON output:")
    print(params.to_json())


def demo_mimo_nl_query():
    """Demo: Query scenario results using natural language with MiMo."""

    client = LLMClient(provider="mimo", model="mimo-v2.5-pro")
    engine = NLQueryEngine(client)

    # Load sample scenario results
    scenarios = [
        {
            "scenario_name": "BXM_30pct_coverage_R0_1.5",
            "drug": "BXM",
            "coverage": 0.30,
            "r0": 1.5,
            "icer": 45200,
            "total_cost": 52000000,
            "qaly": 1250,
            "nmb": 8200000,
        },
        {
            "scenario_name": "OTV_30pct_coverage_R0_1.5",
            "drug": "OTV",
            "coverage": 0.30,
            "r0": 1.5,
            "icer": 68500,
            "total_cost": 18000000,
            "qaly": 980,
            "nmb": 3100000,
        },
        {
            "scenario_name": "BXM_50pct_coverage_R0_2.0",
            "drug": "BXM",
            "coverage": 0.50,
            "r0": 2.0,
            "icer": 32100,
            "total_cost": 87000000,
            "qaly": 2800,
            "nmb": 15600000,
        },
    ]

    engine.load_results(scenarios)

    print("=" * 60)
    print("Natural Language Query")
    print("=" * 60)

    result = engine.query(
        "Which BXM strategy is most cost-effective?",
        language="en"
    )

    print(f"\nAnswer:\n{result['answer']}")
    print(f"\nData references: {result['data_references']}")
    print(f"Confidence: {result['confidence']}")


def demo_mimo_report():
    """Demo: Generate policy brief section using MiMo."""

    client = LLMClient(provider="mimo", model="mimo-v2.5-pro")
    generator = PolicyReportGenerator(client)

    analysis_data = {
        "optimal_strategy": "BXM at 50% coverage",
        "icer": 32100,
        "nmb": 15600000,
        "wtp_threshold": 50000,
        "qaly_gained": 2800,
        "resistance_risk": "Low (2.3%)",
        "sensitivity_drivers": ["R0", "drug cost", "resistance frequency"],
    }

    print("=" * 60)
    print("Policy Report Generation")
    print("=" * 60)

    summary = generator.generate_section(
        "executive_summary",
        analysis_data
    )
    print(f"\nExecutive Summary:\n{summary}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        demo_name = sys.argv[1]
        demos = {
            "extract": demo_mimo_extraction,
            "query": demo_mimo_nl_query,
            "report": demo_mimo_report,
        }
        if demo_name in demos:
            demos[demo_name]()
        else:
            print(f"Unknown demo: {demo_name}")
            print(f"Available: {list(demos.keys())}")
    else:
        print("MiMo V2.5 Integration Examples")
        print("=" * 60)
        print()
        print("Usage: python examples/mimo_demo.py [demo_name]")
        print()
        print("Available demos:")
        print("  extract  - Literature parameter extraction")
        print("  query    - Natural language query engine")
        print("  report   - Policy report generation")
        print()
        print("Set MIMO_API_KEY environment variable before running.")
        print("API platform: https://platform.xiaomimimo.com/")
