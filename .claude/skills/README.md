# Claude Skills — AI Content Factory

These are project-level Claude Code skills stored in `.claude/skills/`. Claude Code can discover each skill through its `SKILL.md` file when this repository is opened as a project.

## Recommended order

1. `story-research` — build a source-backed research brief.
2. `story-writer-id` — write the Indonesian script from the approved brief.
3. `storyboard-maker` — map the approved script to vertical scenes.
4. `character-consistency` — apply whenever Raka appears in Sejarah Dunia visuals.
5. `video-quality-check` — audit the package/render before human approval.

## Important boundaries

- Skills are reusable instructions for Claude Code; they are not GitHub Actions workflows and do not run by themselves.
- Existing GitHub Actions, Supabase schema, dashboard, and publishing settings are intentionally unchanged in this branch.
- These skills do not call Gemini, consume API quota, generate images/video, or publish content on their own.
- Research claims and third-party visual reuse still require source verification and human review.
- Auto-upload remains disabled. Human approval remains required.

## Use

Open this repository in Claude Code and ask it to perform the relevant task, for example:
- "Use story-research to research this Peta Sunyi topic."
- "Use story-writer-id to draft a script from this approved research brief."
- "Use storyboard-maker to turn this script into a 9:16 storyboard."
- "Use video-quality-check to audit this rendered video."

Review every proposed change before merging this branch into `main`.
