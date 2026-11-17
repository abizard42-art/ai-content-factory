# AI Clipping Factory — Product Plan

## Goal
Build a quality-first clipping workflow for the Rockaroma clipping competition. The first engine is for podcast episodes. A separate gaming-streamer engine can be added later without changing the core pipeline.

## First test source
- YouTube URL supplied by the user: https://youtu.be/D_mKXncfU8o?si=CI2og_CBthceZjIt
- Source must be publicly accessible and authorized for clipping under the competition rules or by the rights holder.
- Do not bypass DRM, login walls, age restrictions, private access, or other access controls. Prefer an official source download/export or a source file supplied by the rights holder/organizer.

## Podcast Clip Engine
1. Ingest an authorized source video or audio file.
2. Extract audio and inspect the full available duration.
3. Produce a timestamped transcript.
4. Detect complete, self-contained moments: funny, surprising, emotional, controversial, insightful, or highly relatable.
5. Score candidate moments for hook, context, build-up, payoff, clarity, emotion/reaction, audio/visual quality, subtitle readability, and retention potential.
6. Return ranked candidates with exact in/out timestamps and a short explanation. Do not invent moments or timestamps.
7. Render selected clips in vertical 9:16 (target 1080x1920), with synchronized Indonesian subtitles, careful reframing, clean audio, and restrained dynamic cuts/zooms.
8. Human review before publishing.

## Editorial rules
- Quality over quota: never pad the output with weak clips.
- Typical target length: 90–150 seconds, but let the story determine the final duration.
- Prefer a clear arc: 0–3 second hook, enough context, build-up, payoff, concise ending.
- Make a loop-friendly ending only when it feels natural; never force a loop.
- Preserve speaker meaning and context. Do not misleadingly splice statements or remove important qualifications.
- Keep subtitles accurate and synchronized; avoid covering faces or important visuals.
- AI scores are heuristics, not guarantees of views or virality.

## Initial output
- Ranked candidate list with timestamps and scores.
- Preview-ready vertical clips after the source-access path and analysis pipeline are validated.
- No automatic publishing in the first phase.

## Architecture
- Shared pipeline: ingest → transcribe → detect moments → rank → edit → quality check → human approval → export.
- Engine-specific analyzers: Podcast Clip Engine first; Gaming Streamer Clip Engine later.
- Output profiles are separate from analysis so horizontal and other formats can be added later.
- Keep clipping workflows separate from the existing Sejarah Dunia history-video workflows.

## Cost and reliability
- Prefer existing GitHub Actions and already-configured services where feasible.
- Check file size, duration, runtime, and API limits before processing.
- Fail clearly when credentials, source access, or media decoding are unavailable.
- Do not silently substitute partial analysis for full-video analysis.
