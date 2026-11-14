# Reliable Apps

**Public data tools that keep working.**

Reliable Apps is a small set of focused public-data tools on the Apify Store. Each one does one job, returns one clear schema and charges per result delivered. The tools are built and maintained by an AI team; Vasilis Linakis owns them and is accountable for them.

This repository holds copy-and-run examples for calling the tools from Python, JavaScript and n8n.

## The tools

| Tool | What it returns | Price (Store, 2026-10-31) |
|---|---|---|
| [Company Job Board Feeds](https://apify.com/reliable-apps/company-job-board-feeds) | Every open role from the Greenhouse, Lever and Ashby job boards you list, in one schema | $2 per 1,000 jobs |
| [Google Trends API & Scraper](https://apify.com/reliable-apps/google-trends-reliable) | Interest over time, by region, related queries and topics, for single terms or comparisons of up to 5 | $5 per 1,000 results |

Both tools also charge Apify's standard start fee of $0.00005 per run. You pay per result delivered: a company or term that fails comes back as an `error` record, and error and summary records are never charged. Platform usage is included in the price.

## Examples

| Folder | Use case | Python | JavaScript | n8n |
|---|---|---|---|---|
| [job-board-feeds](job-board-feeds/) | Monitor competitor hiring signals | [monitor_hiring.py](job-board-feeds/python/monitor_hiring.py) (CSV + new roles since last run) | [monitor-hiring.mjs](job-board-feeds/javascript/monitor-hiring.mjs) | [weekly-hiring-digest.json](job-board-feeds/n8n/weekly-hiring-digest.json) |
| [google-trends](google-trends/) | Weekly keyword trend report | [trends_to_csv.py](google-trends/python/trends_to_csv.py) (CSV + rising queries) | [trends.mjs](google-trends/javascript/trends.mjs) | [weekly-trends-to-sheet.json](google-trends/n8n/weekly-trends-to-sheet.json) |

**Tutorial:** [How to get Greenhouse, Lever and Ashby job postings as JSON (and track new roles weekly)](https://dev.to/reliableapps/how-to-get-greenhouse-lever-and-ashby-job-postings-as-json-and-track-new-roles-weekly-59cl) walks through the job-board example step by step.

**Tutorial:** [Google Trends API alternatives in 2026: getting Trends data as JSON (and what to do about 429s)](https://dev.to/reliableapps/google-trends-api-alternatives-in-2026-getting-trends-data-as-json-and-what-to-do-about-429s-2af0) walks through the Trends example step by step.

## Your Apify API token

Every example uses **your own** Apify account and token, read from the `APIFY_TOKEN` environment variable.

1. Sign up or log in at [console.apify.com](https://console.apify.com).
2. Open **Settings > API & Integrations** and copy your personal API token.
3. Set it in your shell for the session only:

   ```bash
   export APIFY_TOKEN=your_token_here        # macOS / Linux
   ```

   ```powershell
   $env:APIFY_TOKEN = "your_token_here"      # Windows PowerShell
   ```

4. In n8n, create a **Header Auth** credential with name `Authorization` and value `Bearer your_token_here`, then select it in the HTTP Request node.

Never commit a token. `.env` files are ignored by this repository's `.gitignore`. If a token leaks, regenerate it in the Apify Console.

Each example sets a maximum cost per run (`max_total_charge_usd` / `maxTotalChargeUsd`). The run stops cleanly when it reaches that amount.

## Quick start

```bash
# Python
pip install -r requirements.txt
python job-board-feeds/python/monitor_hiring.py greenhouse:airbnb lever:palantir --out jobs.csv
python google-trends/python/trends_to_csv.py "web scraping" "web crawler" --geo US

# JavaScript (Node.js 18+)
npm install
node job-board-feeds/javascript/monitor-hiring.mjs greenhouse:airbnb
node google-trends/javascript/trends.mjs "web scraping" "web crawler"
```

For n8n: **Workflows > Import from File**, pick a JSON file, then replace the placeholder credentials and IDs marked `REPLACE_WITH_...`.

## Responsible use

Public data only. No logins, no personal data, no captcha or block bypass.

- Company Job Board Feeds reads only the official public job-board feeds that employers publish, honours `robots.txt` and outputs no personal data. Link to the original posting (`job_url`) rather than republishing postings, and do not use the output to train AI models.
- Google Trends API & Scraper uses only the Trends data API that Google's `robots.txt` allows and returns aggregated, anonymised data. Values are a relative 0-100 index, not search volumes.
- You decide what to collect and how you use it, and you are responsible for complying with applicable law and the terms of the sites involved.

Not affiliated with Apify, Google, Greenhouse, Lever, Ashby or n8n. Their names are used only to describe compatibility.

## Issues and contributions

See [CONTRIBUTING.md](CONTRIBUTING.md). Problems with a tool itself go to the Issues tab of its Store page.

## AI-assisted disclosure

These tools are built and maintained by an AI team. Vasilis Linakis owns them and is accountable for them. The examples in this repository were also written with AI assistance and checked against the tools' real input and output schemas.

## License

MIT. See [LICENSE](LICENSE).

---

Reliable Apps by Vasilis Linakis
