# AI Content Factory

A cloud-first, multi-channel content production system. The factory currently supports two planned Indonesian-language channels: Sejarah Dunia (2D cartoon explainer) and Misteri Nusantara (hybrid documentary mystery).

## Initial operating settings

- First channel: Sejarah Dunia
- Language: Indonesian
- Format: vertical short-form video
- Visual style: 2D cartoon
- Main character: one consistent recurring character
- Target: 2 videos per day
- Publishing: disabled until generation, quality checks, and OAuth publishing are tested
- Approval: required before publishing during the initial phase

## Build principles

1. Start with a reliable repository, database, and dashboard.
2. Keep channel-specific settings in configuration files.
3. Separate research, scripting, storyboarding, rendering, quality checks, and publishing.
4. Never publish automatically until the workflow has been tested end to end.
5. Keep costs visible; free tiers have usage limits and AI generation may incur costs.

## Project status

Phase 1: repository foundation. See `docs/PHASE-1.md` for the setup sequence.
