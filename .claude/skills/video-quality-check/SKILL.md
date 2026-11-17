---
name: video-quality-check
description: Audit a generated script, storyboard, visual asset set, or rendered vertical video before human approval. Use before a video is marked ready for publishing.
---

# Video Quality Check

## Principle
This skill is a gate, not a rubber stamp. Identify defects clearly and do not mark a package approved merely because the render completed.

## Review categories
### 1. Factual and editorial
- Check factual claims against the supplied research sources.
- Flag unsupported dates, names, locations, quotes, statistics, and causal claims.
- Confirm legends, disputed claims, and AI reconstructions are labelled accurately.
- Check that title and hook do not promise more than the story proves.

### 2. Script and narration
- Check natural Indonesian, spelling, pronunciation risks, repeated phrases, and awkward sentences.
- Confirm narration matches the approved script.
- Check estimated duration against actual audio/video duration where available.

### 3. Visuals and continuity
- Confirm every scene matches its narration.
- Check vertical 9:16 framing, readable text, safe margins, and visual variety.
- Check Raka consistency whenever he appears.
- Flag anachronisms, malformed anatomy, duplicated elements, watermarks, and misleading documentary-style AI images.
- Confirm source and reuse notes exist for third-party assets.

### 4. Technical render
When a rendered file is available, inspect:
- file opens and plays from beginning to end;
- resolution and aspect ratio;
- audio presence, clipping, distortion, and sync;
- black/frozen frames, abrupt cuts, missing scenes, and unexpected silence;
- subtitle spelling and safe-area placement;
- duration and encoding compatibility.

Do not claim to have watched or inspected a video unless the file or representative frames/audio were actually provided and examined.

## Severity
- BLOCKER: factual fabrication, unsafe/private-location guidance, missing or corrupted video/audio, serious mismatch, unlicensed asset presented as cleared, or missing required approval.
- MAJOR: inconsistent character, unreadable text, broken timing, repeated/irrelevant visuals, or unsupported key claim.
- MINOR: small typo, minor transition issue, or cosmetic inconsistency.

## Output
Return:
- status: PASS, PASS_WITH_FIXES, or BLOCKED;
- blockers;
- major issues;
- minor issues;
- evidence or scene numbers for each issue;
- exact recommended corrections;
- human-review checklist.

Never change a publishing or approval status in a database, never upload, and never publish. This skill only reports quality findings.
