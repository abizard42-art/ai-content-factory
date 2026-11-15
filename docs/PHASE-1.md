# Phase 1 — Cloud foundation

## Goal
Prepare the repository, database, and a small dashboard from an Android phone. This phase does not generate or upload videos yet.

## Step 1 — Create the Supabase project
1. Open https://supabase.com and create a project.
2. Save the database password somewhere private.
3. In Project Settings → API, copy the Project URL and publishable/anon key.
4. Open the SQL Editor and run `supabase/schema.sql`.

## Step 2 — Publish the dashboard
1. Open this repository on GitHub.
2. Go to Settings → Pages.
3. Under Build and deployment, choose Deploy from a branch.
4. Select `main` and `/dashboard` if GitHub Pages offers that folder, or move dashboard files to the repository root if needed.
5. Save and wait for the Pages URL.

## Step 3 — Connect the dashboard
Open the Pages URL, enter the Supabase Project URL and publishable key, then sign up with your email. Confirm the email if Supabase asks.

## Safety
- Never put a Supabase service-role key, YouTube client secret, or OAuth refresh token in browser code or GitHub commits.
- Keep auto-upload disabled until generation, review, and YouTube OAuth are tested.
- GitHub Actions schedules are not guaranteed to run at the exact minute.

## Current scope
The heartbeat workflow only verifies that scheduled automation can start. It does not create videos, spend AI credits, or publish content.
