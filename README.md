# Apex Option Lab

Astro + Svelte static builder for Apex Legends launch options. The catalog is generated from the supplied static-analysis CSVs. It displays 330 candidates by default; enabling the excluded-items toggle searches all 4,042 unique option names (4,114 registrations). Presets are not part of this version.

## Local development

```sh
npm ci
npm run dev
```

Set `PUBLIC_GA_MEASUREMENT_ID` to enable anonymous GA4 events. Copying a command sends one `option_copy` event per included option.

Search analytics records only the result count; the entered search text is not sent. Generated launch options are intended for the game's launch-options field, not for execution by a shell. To reduce accidental interpretation, values containing quotes, $, `, & | < > parentheses, semicolons, Windows %/!/^ expansion characters, or line breaks are rejected. Spaces remain supported and are quoted for known argument formats. Shell escaping differs between Windows and Linux, so shell command execution is not supported.

## GitHub Pages

This repository deploys the builder to [kariya.dev/apex-launch-option-builder](https://kariya.dev/apex-launch-option-builder/) and the original sensitivity converter to [kariya.dev/Apex-Legends-Sensitivity-Converter](https://kariya.dev/Apex-Legends-Sensitivity-Converter/). The converter is copied from audited commit 982f5d90d50dd1dc1a04a600c5a1915619425019; update this pin only after reviewing the source diff.

The optional ranking updater requires `GA4_PROPERTY_ID` and `GOOGLE_SERVICE_ACCOUNT_JSON`. Its query counts unique GA4 active users from 2020-01-01 through yesterday; GA4 identity and retention settings prevent a guarantee of permanent exact deduplication.

The source CSV is a static registration dump, not a verified list of launch arguments. Recommendation metadata and CFG support must be curated when evidence is available.

## Catalog sources and checks

`data/candidates.csv` defines candidate membership and primary descriptions, classifications, examples and cautions. `data/all.csv` supplies the full catalog and supporting evidence. Both are unchanged copies of the supplied CSVs. Rows are grouped by exact option name; conflicting defaults are retained and leave the initial input blank. Candidate status does not establish effectiveness or recommendation. Every item is untested on Windows hardware.

Builds run `scripts/prepare-data.py` to regenerate `public/data/registrations.json`. No CSV-derived option is marked CFG-compatible, and input ranges are not inferred. Unknown argument formats allow manual argument entry, including an empty argument; their resulting syntax remains unverified.

Run catalog and command-generation checks with `npm test`, and the type/build checks with `npm run build`.
