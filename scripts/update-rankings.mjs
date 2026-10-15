import { BetaAnalyticsDataClient } from '@google-analytics/data';
import { readFile, writeFile } from 'node:fs/promises';

const propertyId = process.env.GA4_PROPERTY_ID;
const credentials = process.env.GOOGLE_SERVICE_ACCOUNT_JSON;
if (!propertyId || !credentials) throw new Error('Set GA4_PROPERTY_ID and GOOGLE_SERVICE_ACCOUNT_JSON.');

const client = new BetaAnalyticsDataClient({ credentials: JSON.parse(credentials) });
const [report] = await client.runReport({
  property: `properties/${propertyId}`,
  dateRanges: [{ startDate: '2020-01-01', endDate: 'yesterday' }],
  dimensions: [{ name: 'customEvent:option_id' }],
  metrics: [{ name: 'activeUsers' }],
  dimensionFilter: {
    filter: { fieldName: 'eventName', stringFilter: { matchType: 'EXACT', value: 'option_copy' } }
  },
  orderBys: [{ metric: { metricName: 'activeUsers' }, desc: true }],
  limit: 10000
});

const options = JSON.parse(await readFile(new URL('../public/data/registrations.json', import.meta.url), 'utf8'));
const known = new Set(options.map(({ id }) => id));
const rankings = (report.rows ?? [])
  .map((row) => ({ id: row.dimensionValues[0].value, users: Number(row.metricValues[0].value) }))
  .filter(({ id }) => known.has(id));
await writeFile(new URL('../public/data/option-rankings.json', import.meta.url), `${JSON.stringify({ updatedAt: new Date().toISOString(), rankings }, null, 2)}\n`);
console.log(`Updated ${rankings.length} option rankings.`);
