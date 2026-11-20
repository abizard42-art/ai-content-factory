# Last30Days — private research module

This is an isolated research workflow for AI Content Factory. It does not build, render, schedule, upload, or publish videos.

## Run from Android

1. Open the repository on GitHub.
2. Open **Actions**.
3. Select **Last30Days private research**.
4. Tap **Run workflow**.
5. Choose a scope:
   - `all` (default): creates one report each for Peta Sunyi, Sejarah Dunia, AI Content Factory, and Business Opportunity Radar.
   - One individual scope: creates only that report.
6. Optionally enter a focus topic, then tap **Run workflow**.

There is no push trigger and no schedule. Every research run must be started manually.

## Sources and credentials

The workflow pins upstream `mvanhorn/last30days-skill` to commit
`262391603f3c2807606bffa0170547273fc273e5` and uses its Python 3.12+ engine.

The initial source allowlist is restricted to free/keyless lanes:
Reddit, Hacker News, Polymarket, public GitHub, YouTube via `yt-dlp`, and the engine's
keyless web-grounding lane. Optional paid/provider credentials are explicitly blanked in the
research process. X, TikTok, Instagram, and other credentialed lanes are not enabled.

Required GitHub Actions secrets:
- `SUPABASE_URL`
- `SUPABASE_SECRET_KEY`

No Gemini, OpenAI, xAI, ScrapeCreators, or paid web-search API key is required for this
initial configuration. GitHub-hosted execution runs in the cloud; no PC or Android-side
Python installation is needed.

## Private report handling

Reports are uploaded to the Supabase Storage bucket `research-reports`.
The runner creates it as private when absent and stops if it finds the bucket is public.
Object layout:

```
research-reports/
  peta-sunyi/YYYY-MM-DD/run-GITHUB_RUN_ID.md
  sejarah-dunia/YYYY-MM-DD/run-GITHUB_RUN_ID.md
  ai-content-factory/YYYY-MM-DD/run-GITHUB_RUN_ID.md
  business-opportunity/YYYY-MM-DD/run-GITHUB_RUN_ID.md
```

The workflow does not create GitHub Actions artifacts, commit report files, generate public
URLs, or publish reports. Access reports through the authenticated Supabase dashboard or a
future private application with appropriate access controls. Do not change the bucket to public.

## Isolation guarantees

- The only workflow added for this integration is
  `.github/workflows/last30days-private-research.yml`.
- The runner is in `scripts/last30days/run_research.py`.
- No existing Peta Sunyi or Sejarah Dunia production workflow is edited.
- No automatic publishing or recurring schedule is configured.
- Reports stay outside the public repository.

## Upstream

- Project: https://github.com/mvanhorn/last30days-skill
- Pinned commit: https://github.com/mvanhorn/last30days-skill/commit/262391603f3c2807606bffa0170547273fc273e5
- License: MIT
