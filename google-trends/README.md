# Weekly keyword trend report, without handling 429 errors yourself

Examples for [Google Trends API & Scraper](https://apify.com/reliable-apps/google-trends-reliable): interest over time, by region, related queries and topics, for single terms or comparisons of up to 5. $5 per 1,000 results (Store, 2026-10-31), plus a $0.00005 start fee per run. A comparison of up to 5 terms is one result.

**The use case.** Every Monday, compare the keywords you care about and log the numbers, without exporting CSVs from trends.google.com by hand or handling HTTP 429 responses in your own scripts.

**What happens on a rate limit.** Google limits how often Trends can be queried. The tool retries a 429 up to 3 times, honouring `Retry-After`, and then returns that term as an `error` record with `error_code: "rate_limited"`. Error records are never charged. The tool does not rotate proxies or IP addresses, so rate limits can still happen; smaller batches and spaced-out runs work best.

## Input

```json
{
  "searchTerms": ["web scraping", "web crawler"],
  "compareMode": true,
  "timeRange": "today 3-m",
  "geo": "US",
  "interestOverTime": true,
  "interestByRegion": false,
  "relatedQueries": true
}
```

`timeRange` is one of `now 1-H`, `now 4-H`, `now 1-d`, `now 7-d`, `today 1-m`, `today 3-m`, `today 12-m`, `today 5-y`, `all`. `geo` is a country or region code (`US`, `GB`, `US-CA`); empty means worldwide.

## Output

Each dataset item has a `type`: `result`, `error` (not charged) or `summary` (not charged, one per run). A comparison `result` holds:

- `interestOverTime.points[]`: `time`, `formattedTime`, `isPartial`, and `values` keyed by term (0-100, relative).
- `interestOverTime.averages`: the average per term.
- `relatedQueries[term].top[]` and `.rising[]`: `query`, `value`, `formattedValue`, `link`.
- `timeRangeResolved` (the dates Google used), `exploreUrl`, `warnings`.

## Examples

### Python: CSV and rising queries

```bash
pip install -r ../requirements.txt
export APIFY_TOKEN=your_token_here
python python/trends_to_csv.py "web scraping" "web crawler" --geo US --time-range "today 3-m" --out trends.csv
```

Writes one row per time point and one column per term, then prints average interest and up to 10 rising queries per term. Failed terms are printed with their error code.

### JavaScript

```bash
npm install
node javascript/trends.mjs "web scraping" "web crawler"
```

### n8n: weekly trends to Google Sheets

`n8n/weekly-trends-to-sheet.json`: Schedule (Monday 07:00) > HTTP Request to `run-sync-get-dataset-items` (past 7 days, 3 terms compared) > Code node (one row per term: week, average interest, top rising query, status) > Google Sheets append.

After import:
1. Create a Header Auth credential (`Authorization` / `Bearer <your token>`) and select it in the HTTP Request node.
2. Connect your Google Sheets credential, replace `REPLACE_WITH_YOUR_SPREADSHEET_ID`, and add a sheet named `Trends` with the header row `week, term, geo, dates, avg_interest, top_rising_query, top_rising_change, status, explore_url`.
3. Edit `searchTerms` in the JSON body.

Failed terms are written as rows with `status: error: <code>`, so a gap in the sheet always has a reason.

## Limits

- Values are Google's relative 0-100 index, sampled, not search volumes. Two runs can differ slightly.
- A comparison holds at most 5 terms; values are comparable only within one comparison.
- Related topics are not available in comparison mode.

Not affiliated with Google. Problems with the tool: open an issue at https://apify.com/reliable-apps/google-trends-reliable/issues.
