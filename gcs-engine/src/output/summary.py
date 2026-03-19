"""Console and markdown summary generators for scored partner data."""

import os
from datetime import datetime

import pandas as pd


def _tier_emoji(tier: str) -> str:
    """Return a text indicator for tier (no Unicode emoji for terminal compat)."""
    if tier == "green":
        return "[GREEN]"
    elif tier == "amber":
        return "[AMBER]"
    return "[RED]"


def print_summary(scored_df: pd.DataFrame) -> None:
    """Print top 10, bottom 10, and tier distribution to console.

    Args:
        scored_df: DataFrame from score_all_partners, sorted by composite_score desc.
    """
    if scored_df.empty:
        print("No partners to summarize.")
        return

    total = len(scored_df)
    avg_score = scored_df["composite_score"].mean()

    print("\n" + "=" * 60)
    print("GCS ENGINE — PARTNER SCORING SUMMARY")
    print("=" * 60)
    print(f"Total partners scored: {total}")
    print(f"Average composite score: {avg_score:.1f}")
    print()

    # Tier distribution
    tier_counts = scored_df["tier"].value_counts()
    print("TIER DISTRIBUTION:")
    for tier_name in ["green", "amber", "red"]:
        count = tier_counts.get(tier_name, 0)
        pct = (count / total * 100) if total > 0 else 0
        print(f"  {tier_name.upper():>6}: {count:>3} partners ({pct:.1f}%)")
    print()

    # Top 10
    top_n = min(10, total)
    print(f"TOP {top_n} PARTNERS:")
    print(f"  {'Rank':<5} {'Partner':<30} {'Score':>7} {'Tier':>8} {'Play'}")
    print(f"  {'----':<5} {'-------':<30} {'-----':>7} {'----':>8} {'----'}")
    for idx, (_, row) in enumerate(scored_df.head(top_n).iterrows(), start=1):
        name = row.get("partner_name", row.get("partner_id", ""))
        print(
            f"  {idx:<5} {str(name):<30} {row['composite_score']:>7.1f} "
            f"{row['tier']:>8} {row.get('recommended_play', '')}"
        )
    print()

    # Bottom 10
    if total > 10:
        bottom_n = min(10, total)
        print(f"BOTTOM {bottom_n} PARTNERS:")
        print(f"  {'Rank':<5} {'Partner':<30} {'Score':>7} {'Tier':>8}")
        print(f"  {'----':<5} {'-------':<30} {'-----':>7} {'----':>8}")
        bottom = scored_df.tail(bottom_n).iloc[::-1]  # Show worst first
        for idx, (_, row) in enumerate(bottom.iterrows(), start=total - bottom_n + 1):
            name = row.get("partner_name", row.get("partner_id", ""))
            print(
                f"  {idx:<5} {str(name):<30} {row['composite_score']:>7.1f} "
                f"{row['tier']:>8}"
            )
    print()


def generate_markdown_summary(
    scored_df: pd.DataFrame,
    output_dir: str = "output",
) -> str:
    """Generate markdown summary file.

    Args:
        scored_df: DataFrame from score_all_partners, sorted by composite_score desc.
        output_dir: Directory to write the markdown file.

    Returns:
        Path to the generated markdown file.
    """
    os.makedirs(output_dir, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m")
    md_path = os.path.join(output_dir, f"gcs_summary_{date_str}.md")

    total = len(scored_df)
    avg_score = scored_df["composite_score"].mean() if total > 0 else 0.0

    tier_counts = scored_df["tier"].value_counts() if total > 0 else pd.Series(dtype=int)

    lines = []
    lines.append("# GCS Engine — Partner Scoring Summary")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Total partners scored:** {total}")
    lines.append(f"**Average composite score:** {avg_score:.1f}")
    lines.append("")

    # Tier distribution
    lines.append("## Tier Distribution")
    lines.append("")
    lines.append("| Tier | Count | Percentage |")
    lines.append("|------|------:|----------:|")
    for tier_name in ["green", "amber", "red"]:
        count = int(tier_counts.get(tier_name, 0))
        pct = (count / total * 100) if total > 0 else 0
        lines.append(f"| {tier_name.capitalize()} | {count} | {pct:.1f}% |")
    lines.append("")

    # Top 10
    top_n = min(10, total)
    lines.append(f"## Top {top_n} Partners")
    lines.append("")
    lines.append("| Rank | Partner | Score | Tier | Recommended Play |")
    lines.append("|-----:|---------|------:|------|-----------------|")
    for idx, (_, row) in enumerate(scored_df.head(top_n).iterrows(), start=1):
        name = row.get("partner_name", row.get("partner_id", ""))
        lines.append(
            f"| {idx} | {name} | {row['composite_score']:.1f} | "
            f"{row['tier']} | {row.get('recommended_play', '')} |"
        )
    lines.append("")

    # Bottom 10
    if total > 10:
        bottom_n = min(10, total)
        lines.append(f"## Bottom {bottom_n} Partners")
        lines.append("")
        lines.append("| Rank | Partner | Score | Tier |")
        lines.append("|-----:|---------|------:|------|")
        for idx, (_, row) in enumerate(
            scored_df.tail(bottom_n).iterrows(),
            start=total - bottom_n + 1,
        ):
            name = row.get("partner_name", row.get("partner_id", ""))
            lines.append(f"| {idx} | {name} | {row['composite_score']:.1f} | {row['tier']} |")
        lines.append("")

    with open(md_path, "w") as f:
        f.write("\n".join(lines) + "\n")

    return md_path
