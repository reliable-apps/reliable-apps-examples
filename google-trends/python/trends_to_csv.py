"""Weekly keyword trend report with Google Trends API & Scraper.

Compares up to 5 search terms on one chart with the Apify Actor
reliable-apps/google-trends-reliable, writes interest over time to a CSV file
(one row per time point, one column per term) and prints the rising related
queries for each term.

Usage:
    export APIFY_TOKEN=...            # your own token, never commit it
    python trends_to_csv.py "web scraping" "web crawler" --geo US --time-range "today 3-m"

Pricing (as on the Store, 2026-10-31): $5 per 1,000 results, plus a $0.00005
start fee per run. A comparison of up to 5 terms is one result. Terms that fail
(for example when Google answers HTTP 429) come back as error records, which are
never charged.
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from decimal import Decimal
from pathlib import Path

from apify_client import ApifyClient

ACTOR_ID = "reliable-apps/google-trends-reliable"
TIME_RANGES = ["now 1-H", "now 4-H", "now 1-d", "now 7-d", "today 1-m", "today 3-m", "today 12-m", "today 5-y", "all"]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Compare up to 5 Google Trends terms and save them as CSV.")
    p.add_argument("terms", nargs="+", help="1 to 5 search terms.")
    p.add_argument("--geo", default="", help='Country or region code, e.g. US, GB, US-CA. Empty = worldwide.')
    p.add_argument("--time-range", default="today 12-m", choices=TIME_RANGES)
    p.add_argument("--out", type=Path, default=Path("trends.csv"), help="CSV to write (default: trends.csv).")
    p.add_argument(
        "--max-cost-usd",
        type=Decimal,
        default=Decimal("0.10"),
        help="Stop the run cleanly at this cost (default: 0.10).",
    )
    args = p.parse_args()
    if len(args.terms) > 5:
        p.error("Google Trends compares at most 5 terms on one chart.")
    return args


def run_actor(token: str, args: argparse.Namespace) -> list[dict]:
    client = ApifyClient(token)
    run_input = {
        "searchTerms": args.terms,
        "compareMode": True,
        "timeRange": args.time_range,
        "geo": args.geo,
        "interestOverTime": True,
        "interestByRegion": False,
        "relatedQueries": True,
    }
    run = client.actor(ACTOR_ID).call(run_input=run_input, max_total_charge_usd=args.max_cost_usd)
    if run is None:
        sys.exit("The run did not start. Check your token and the Actor ID.")
    status = getattr(run.status, "value", run.status)
    print(f"Run {run.id} finished with status {status}.")
    return list(client.dataset(run.default_dataset_id).iterate_items())


def write_csv(path: Path, result: dict) -> int:
    terms = result["searchTerms"]
    points = (result.get("interestOverTime") or {}).get("points") or []
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["time", "label", "is_partial", *terms])
        for pt in points:
            values = pt.get("values") or {}
            writer.writerow([pt.get("time"), pt.get("formattedTime"), pt.get("isPartial"), *(values.get(t) for t in terms)])
    return len(points)


def main() -> None:
    args = parse_args()
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        sys.exit("Set APIFY_TOKEN to your own Apify API token (Apify Console > Settings > API & Integrations).")

    items = run_actor(token, args)
    results = [i for i in items if i.get("type") == "result"]
    errors = [i for i in items if i.get("type") == "error"]

    for err in errors:
        # Error records are not charged. Re-run later or with fewer terms.
        print(f"  no data for {err.get('searchTerm')!r}: {err.get('error_code')} ({err.get('message')})")
    if not results:
        sys.exit("No result records in this run; nothing written.")

    result = results[0]
    rows = write_csv(args.out, result)
    print(f"Wrote {rows} time points for {', '.join(result['searchTerms'])} to {args.out}")
    print(f"Dates used: {result.get('timeRangeResolved')}  Open in Google Trends: {result.get('exploreUrl')}")

    averages = (result.get("interestOverTime") or {}).get("averages") or {}
    if averages:
        print("Average interest (0-100, relative): " + ", ".join(f"{t}={v}" for t, v in averages.items()))

    related = result.get("relatedQueries") or {}
    for term in result["searchTerms"]:
        rising = (related.get(term) or {}).get("rising") or []
        print(f"\nRising queries for {term!r}:")
        if not rising:
            print("  none returned")
        for q in rising[:10]:
            print(f"  {q.get('formattedValue'):>8}  {q.get('query')}")

    for warning in result.get("warnings") or []:
        print(f"Warning: {warning}")


if __name__ == "__main__":
    main()
