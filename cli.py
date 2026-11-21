"""Command-line interface: cloudcost report <billing.csv> [--ai]"""

import argparse

from dotenv import load_dotenv

from .ai_advisor import advise
from .analyzer import cost_by, find_savings, load_costs, total_cost


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(prog="cloudcost", description="CloudCost AI")
    sub = parser.add_subparsers(dest="command", required=True)
    report = sub.add_parser("report", help="Analyze a billing CSV")
    report.add_argument("csv_path", help="Path to billing CSV")
    report.add_argument("--ai", action="store_true", help="Add AI-written advice")
    args = parser.parse_args()

    records = load_costs(args.csv_path)
    findings = find_savings(records)

    print(f"Total spend: ${total_cost(records)}\n")
    print("By provider:")
    for name, amt in cost_by(records, "provider").items():
        print(f"  {name}: ${amt}")
    print("\nBy service:")
    for name, amt in cost_by(records, "service").items():
        print(f"  {name}: ${amt}")

    print("\nSavings opportunities:")
    if not findings:
        print("  None found.")
    for f in findings:
        print(f"  [{f.provider}] {f.resource_id}: {f.issue}")
        print(f"      -> {f.recommendation} (save ~${f.monthly_savings_usd})")

    if args.ai:
        print("\nAI advice:\n")
        print(advise(records, findings))


if __name__ == "__main__":
    main()
