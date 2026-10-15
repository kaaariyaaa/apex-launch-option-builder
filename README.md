# Apex Option Lab

Astro + Svelte static builder for Apex Legends launch options. The option registry is intentionally empty while its contents are being rebuilt from verified sources. Presets are not part of this version.

## Local development

```sh
npm ci
npm run dev
```

Set `PUBLIC_GA_MEASUREMENT_ID` to enable anonymous GA4 events. Copying a command sends one `option_copy` event per included option. GitHub Actions periodically exports the GA4 `activeUsers` count per option as the popularity ranking.

## GitHub Pages and rankings

Set the repository's `PUBLIC_GA_MEASUREMENT_ID` variable and `GA4_PROPERTY_ID` and `GOOGLE_SERVICE_ACCOUNT_JSON` secrets. Enable GitHub Pages with GitHub Actions as the source. The workflow prepares the option registry, refreshes rankings, then builds and deploys the static site.

The ranking query spans from 2020-01-01 through yesterday and counts unique GA4 active users per option over that range. This is the closest static-site approximation to lifetime unique users; GA4 identity, retention settings, and the configured start date mean it cannot guarantee permanent exact deduplication.

The source CSV is a static registration dump, not a verified list of launch arguments. Recommendation metadata and CFG support must be curated when evidence is available.
