# Apex Option Lab

Astro + Svelte static builder for Apex Legends launch options. The option registry is intentionally empty while its contents are being rebuilt from verified sources. Presets are not part of this version.

## Local development

```sh
npm ci
npm run dev
```

Set `PUBLIC_GA_MEASUREMENT_ID` to enable anonymous GA4 events. Copying a command sends one `option_copy` event per included option.

## GitHub Pages

This repository deploys to [kariya.dev/apex-launch-option-builder](https://kariya.dev/apex-launch-option-builder/). The workflow builds the app into the matching subdirectory and configures `kariya.dev` as its custom domain.

The optional ranking updater requires `GA4_PROPERTY_ID` and `GOOGLE_SERVICE_ACCOUNT_JSON`. Its query counts unique GA4 active users from 2020-01-01 through yesterday; GA4 identity and retention settings prevent a guarantee of permanent exact deduplication.

The source CSV is a static registration dump, not a verified list of launch arguments. Recommendation metadata and CFG support must be curated when evidence is available.
