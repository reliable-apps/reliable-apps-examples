# Monitor competitor hiring signals

Examples for [Company Job Board Feeds](https://apify.com/reliable-apps/company-job-board-feeds): every open role from the Greenhouse, Lever and Ashby job boards you list, in one schema. $2 per 1,000 jobs (Store, 2026-10-31), plus a $0.00005 start fee per run. A board that fails returns a free `error` record.

**The use case.** Pick the companies you compete with, sell to or invest in. Run the tool every week. New roles tell you where each company is putting money: a first sales hire in Berlin, three data engineers, a hiring pause.

## Input

The tool takes a `companies` list. Each entry is a board URL, a `provider:token` string or an object:

```json
{
  "companies": [
    "https://boards.greenhouse.io/airbnb",
    "lever:palantir",
    {"provider": "ashby", "token": "openai", "name": "OpenAI"}
  ],
  "titleKeywords": ["engineer", "data"],
  "postedWithinDays": 7,
  "maxJobsPerCompany": 50
}
```

To find a token, open the company's careers page and follow a job link. In `jobs.lever.co/<token>`, `jobs.ashbyhq.com/<token>` or `boards.greenhouse.io/<token>`, the part after the slash is the token.

## Output

Each dataset item has a `type`: `job`, `error` (not charged) or `summary` (not charged, one per run). Job fields used here: `provider`, `company`, `job_id`, `title`, `department`, `team`, `locations`, `workplace_type`, `employment_type`, `salary_min`, `salary_max`, `salary_currency`, `salary_interval`, `posted_at`, `job_url`, `scraped_at`. `provider` + `job_id` identifies a posting, which is how the Python example spots new roles.

## Examples

### Python: CSV and "new roles since last run"

```bash
pip install -r ../requirements.txt
export APIFY_TOKEN=your_token_here
python python/monitor_hiring.py greenhouse:airbnb lever:palantir --out jobs-2026-11-02.csv
# a week later
python python/monitor_hiring.py greenhouse:airbnb lever:palantir --out jobs-2026-11-09.csv --previous jobs-2026-11-02.csv
```

Options: `--companies-file companies.txt` (one entry per line), `--title-keywords engineer data`, `--location London Remote`, `--max-jobs-per-company 100`, `--max-cost-usd 0.50`.

### JavaScript

```bash
npm install
node javascript/monitor-hiring.mjs greenhouse:airbnb ashby:openai
```

Prints each role and writes `jobs.json`.

### n8n: weekly hiring digest

`n8n/weekly-hiring-digest.json`: Schedule (Monday 08:00) > HTTP Request to `run-sync-get-dataset-items` with `postedWithinDays: 7` > Filter (`type` = `job`) > Code node that builds a digest grouped by company. Add a Slack, email or Notion node at the end to deliver it.

After import: create a Header Auth credential (`Authorization` / `Bearer <your token>`), select it in the HTTP Request node, and edit the `companies` list in the JSON body. The synchronous endpoint waits up to 300 seconds; for long company lists, start a run and read its dataset instead.

## Limits

- Greenhouse, Lever (including the EU instance) and Ashby only.
- Branded careers domains need `provider` and `token` passed explicitly.
- Greenhouse's list endpoint does not include pay ranges.

Not affiliated with Greenhouse, Lever or Ashby. Problems with the tool: open an issue at https://apify.com/reliable-apps/company-job-board-feeds/issues.
