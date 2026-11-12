// Compare up to 5 Google Trends terms with Google Trends API & Scraper (Node.js 18+).
//
//   export APIFY_TOKEN=...   # your own token, never commit it
//   node trends.mjs "web scraping" "web crawler"
//
// Prints average interest and rising queries, and writes trends.csv.
// Pricing (Store, 2026-10-31): $5 per 1,000 results plus a $0.00005 start fee
// per run. A comparison of up to 5 terms is one result. Error records are free.

import { writeFile } from 'node:fs/promises';
import { ApifyClient } from 'apify-client';

const token = process.env.APIFY_TOKEN;
if (!token) {
    console.error('Set APIFY_TOKEN to your own Apify API token.');
    process.exit(1);
}

const searchTerms = process.argv.slice(2);
if (searchTerms.length < 1 || searchTerms.length > 5) {
    console.error('Give 1 to 5 search terms.');
    process.exit(1);
}

const client = new ApifyClient({ token });
const run = await client.actor('reliable-apps/google-trends-reliable').call(
    {
        searchTerms,
        compareMode: true,
        timeRange: 'today 3-m',
        geo: 'US',
        interestOverTime: true,
        interestByRegion: false,
        relatedQueries: true,
    },
    { maxTotalChargeUsd: 0.1 }, // the run stops cleanly at this cost
);

const { items } = await client.dataset(run.defaultDatasetId).listItems();

for (const err of items.filter((i) => i.type === 'error')) {
    console.log(`no data for "${err.searchTerm}": ${err.error_code} (${err.message})`);
}

const result = items.find((i) => i.type === 'result');
if (!result) {
    console.error('No result record in this run.');
    process.exit(1);
}

const { points = [], averages = {} } = result.interestOverTime ?? {};
const header = ['time', 'label', 'is_partial', ...result.searchTerms];
const rows = points.map((p) => [p.time, p.formattedTime, p.isPartial, ...result.searchTerms.map((t) => p.values[t] ?? '')]);
const csv = [header, ...rows].map((r) => r.map((v) => JSON.stringify(v ?? '')).join(',')).join('\n');
await writeFile('trends.csv', `${csv}\n`);

console.log(`Average interest (0-100, relative): ${JSON.stringify(averages)}`);
for (const term of result.searchTerms) {
    const rising = result.relatedQueries?.[term]?.rising ?? [];
    console.log(`Rising for "${term}": ${rising.slice(0, 5).map((q) => `${q.query} (${q.formattedValue})`).join('; ') || 'none returned'}`);
}
console.log(`${points.length} points written to trends.csv. Open in Google Trends: ${result.exploreUrl}`);
