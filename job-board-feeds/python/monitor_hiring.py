"""Monitor competitor hiring with Company Job Board Feeds.

Runs the Apify Actor reliable-apps/company-job-board-feeds for the companies you
list, writes every open role to a CSV file and, if you pass the CSV from the
previous run, prints the roles that are new since then.

Usage:
    export APIFY_TOKEN=...            # your own token, never commit it
    python monitor_hiring.py greenhouse:airbnb lever:palantir ashby:openai
    python monitor_hiring.py --companies-file companies.txt --out jobs.csv --previous jobs-last-week.csv

Pricing (as on the Store, 2026-10-31): $2 per 1,000 jobs, plus a $0.00005 start
fee per run. Error and summary records are never charged.
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from decimal import Decimal
from pathlib import Path

from apify_client import ApifyClient

ACTOR_ID = "reliable-apps/company-job-board-feeds"

CSV_FIELDS = [
    "provider",
    "company",
    "job_id",
    "title",
    "department",
    "team",
    "locations",
    "workplace_type",
    "employment_type",
    "salary_min",
    "salary_max",
    "salary_currency",
    "salary_interval",
    "posted_at",
    "job_url",
    "scraped_at",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Monitor hiring at the companies you choose.")
    p.add_argument(
        "companies",
        nargs="*",
        help='Board URLs or "provider:token" entries, e.g. greenhouse:airbnb lever:palantir',
    )
    p.add_argument("--companies-file", type=Path, help="Text file, one company entry per line.")
    p.add_argument("--out", type=Path, default=Path("jobs.csv"), help="CSV to write (default: jobs.csv).")
    p.add_argument("--previous", type=Path, help="CSV from an earlier run; prints roles that are new since then.")
    p.add_argument("--title-keywords", nargs="*", default=[], help="Keep titles containing any of these words.")
    p.add_argument("--location", nargs="*", default=[], help="Keep jobs whose location contains any of these.")
    p.add_argument("--max-jobs-per-company", type=int, default=100)
    p.add_argument(
        "--max-cost-usd",
        type=Decimal,
        default=Decimal("0.50"),
        help="Stop the run cleanly at this cost (default: 0.50).",
    )
    return p.parse_args()


def load_companies(args: argparse.Namespace) -> list[str]:
    companies = list(args.companies)
    if args.companies_file:
        for line in args.companies_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                companies.append(line)
    return companies


def run_actor(token: str, args: argparse.Namespace, companies: list[str]) -> list[dict]:
    client = ApifyClient(token)
    run_input = {
        "companies": companies,
        "maxJobsPerCompany": args.max_jobs_per_company,
        "includeDescription": False,
    }
    if args.title_keywords:
        run_input["titleKeywords"] = args.title_keywords
    if args.location:
        run_input["locationContains"] = args.location

    run = client.actor(ACTOR_ID).call(run_input=run_input, max_total_charge_usd=args.max_cost_usd)
    if run is None:
        sys.exit("The run did not start. Check your token and the Actor ID.")
    status = getattr(run.status, "value", run.status)
    print(f"Run {run.id} finished with status {status}.")
    return list(client.dataset(run.default_dataset_id).iterate_items())


def job_key(row: dict) -> tuple[str, str]:
    return (str(row.get("provider") or ""), str(row.get("job_id") or ""))


def write_csv(path: Path, jobs: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for job in jobs:
            row = dict(job)
            row["locations"] = "; ".join(job.get("locations") or [])
            writer.writerow(row)


def read_keys(path: Path) -> set[tuple[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return {job_key(row) for row in csv.DictReader(f)}


def new_since(previous: Path, jobs: list[dict]) -> list[dict]:
    """Jobs whose provider + job_id did not appear in the previous CSV."""
    seen = read_keys(previous)
    return [job for job in jobs if job_key(job) not in seen]


def main() -> None:
    args = parse_args()
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        sys.exit("Set APIFY_TOKEN to your own Apify API token (Apify Console > Settings > API & Integrations).")
    companies = load_companies(args)
    if not companies:
        sys.exit("Give at least one company, e.g. greenhouse:airbnb")

    items = run_actor(token, args, companies)
    jobs = [i for i in items if i.get("type") == "job"]
    errors = [i for i in items if i.get("type") == "error"]
    summary = next((i for i in items if i.get("type") == "summary"), None)

    write_csv(args.out, jobs)
    print(f"Wrote {len(jobs)} jobs to {args.out}")

    for err in errors:
        # Error records are not charged. They say which company failed and why.
        print(f"  not fetched: {err.get('input')} -> {err.get('error_code')}: {err.get('message')}")
    if summary:
        print(
            f"Summary: {summary.get('companies_ok')}/{summary.get('companies_total')} companies ok, "
            f"{summary.get('jobs_output')} jobs, {summary.get('duration_seconds')} s"
        )

    if args.previous:
        if not args.previous.exists():
            print(f"No previous file at {args.previous}; skipping the comparison.")
            return
        fresh = new_since(args.previous, jobs)
        print(f"\nNew roles since {args.previous.name}: {len(fresh)}")
        for job in fresh:
            where = ", ".join(job.get("locations") or []) or "location not stated"
            print(f"  [{job.get('company')}] {job.get('title')} ({where}) {job.get('job_url')}")


if __name__ == "__main__":
    main()
