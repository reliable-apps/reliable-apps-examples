// Monitor competitor hiring with Company Job Board Feeds (Node.js 18+).
//
//   export APIFY_TOKEN=...   # your own token, never commit it
//   node monitor-hiring.mjs greenhouse:airbnb lever:palantir ashby:openai
//
// Prints every open role and writes jobs.json. Pricing (Store, 2026-10-31):
// $2 per 1,000 jobs plus a $0.00005 start fee per run. Error records are free.

import { writeFile } from 'node:fs/promises';
import { ApifyClient } from 'apify-client';

const token = process.env.APIFY_TOKEN;
if (!token) {
    console.error('Set APIFY_TOKEN to your own Apify API token.');
    process.exit(1);
}

const companies = process.argv.slice(2);
if (companies.length === 0) {
    console.error('Give at least one company, e.g. greenhouse:airbnb');
    process.exit(1);
}

const client = new ApifyClient({ token });
const run = await client.actor('reliable-apps/company-job-board-feeds').call(
    { companies, maxJobsPerCompany: 100, includeDescription: false },
    { maxTotalChargeUsd: 0.5 }, // the run stops cleanly at this cost
);

const { items } = await client.dataset(run.defaultDatasetId).listItems();
const jobs = items.filter((i) => i.type === 'job');

for (const job of jobs) {
    console.log(`[${job.company}] ${job.title} (${job.locations.join(', ') || 'location not stated'}) ${job.job_url}`);
}
for (const err of items.filter((i) => i.type === 'error')) {
    console.log(`not fetched: ${JSON.stringify(err.input)} -> ${err.error_code}: ${err.message}`);
}

await writeFile('jobs.json', JSON.stringify(jobs, null, 2));
console.log(`${jobs.length} jobs written to jobs.json (run ${run.id}, status ${run.status})`);
