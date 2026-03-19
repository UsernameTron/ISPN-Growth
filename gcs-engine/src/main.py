"""GCS Engine — Growth Composite Score pipeline.

Usage: python -m src.main [--partners N] [--output-dir DIR] [--format xlsx|csv|both]
"""

import argparse
import time


def main():
    parser = argparse.ArgumentParser(description="ISPN Growth Composite Score Engine")
    parser.add_argument("--partners", type=int, default=None, help="Limit to top N partners")
    parser.add_argument("--output-dir", type=str, default="output", help="Output directory")
    parser.add_argument("--format", type=str, choices=["xlsx", "csv", "both"], default="xlsx", help="Output format")
    args = parser.parse_args()

    pipeline_start = time.time()
    print("GCS Engine v0.1.0")
    print("=" * 40)

    # Step 1: Load data from all connectors
    print("Step 1: Loading data from connectors...")
    t0 = time.time()

    from src.connectors import (
        GenesysConnector, HelpDeskConnector, UKGConnector,
        WCSConnector, ServiceMixConnector, BEADConnector,
    )

    genesys_df = GenesysConnector().get_data()
    helpdesk_df = HelpDeskConnector().get_data()
    ukg_df = UKGConnector().get_data()
    wcs_df = WCSConnector().get_data()
    service_mix_df = ServiceMixConnector().get_data()
    bead_df = BEADConnector().get_data()

    print(f"  Loaded {len(genesys_df)} partners from Genesys")
    print(f"  Loaded {len(helpdesk_df)} partners from HelpDesk")
    print(f"  Loaded {len(ukg_df)} partners from UKG")
    print(f"  Loaded {len(wcs_df)} partners from WCS")
    print(f"  Loaded {len(service_mix_df)} partners from Service Mix")
    print(f"  Loaded {len(bead_df)} states from BEAD Status")
    print(f"  Step 1 completed in {time.time() - t0:.2f}s")

    # Step 2: Score all partners
    print("Step 2: Scoring all partners...")
    t0 = time.time()

    from src.scoring.engine import score_all_partners

    scored_df = score_all_partners(
        genesys_df, helpdesk_df, ukg_df, wcs_df, service_mix_df, bead_df,
    )

    # Merge partner_name from service_mix for display
    if "partner_name" in service_mix_df.columns:
        name_map = service_mix_df.set_index("partner_id")["partner_name"]
        scored_df["partner_name"] = scored_df["partner_id"].map(name_map).fillna(scored_df["partner_id"])
    else:
        scored_df["partner_name"] = scored_df["partner_id"]

    print(f"  Scored {len(scored_df)} partners")
    print(f"  Step 2 completed in {time.time() - t0:.2f}s")

    # Optional: Limit partners if --partners flag
    if args.partners:
        scored_df = scored_df.head(args.partners)
        print(f"  Limited output to top {args.partners} partners")

    # Step 3: Generate output
    print("Step 3: Generating output...")
    t0 = time.time()

    from src.output.report import generate_report
    from src.output.summary import print_summary, generate_markdown_summary

    report_path = generate_report(scored_df, args.output_dir, output_format=args.format)
    print_summary(scored_df)
    md_path = generate_markdown_summary(scored_df, args.output_dir)

    print(f"  Step 3 completed in {time.time() - t0:.2f}s")

    elapsed = round(time.time() - pipeline_start, 2)
    print(f"\nPipeline complete in {elapsed}s")
    print(f"Report: {report_path}")
    print(f"Summary: {md_path}")


if __name__ == "__main__":
    main()
