---
name: storyboard-maker
description: Convert an approved Indonesian documentary script into a production-ready vertical 9:16 storyboard with varied visuals, timing, narration mapping, and asset notes. Use after the script is approved.
---

# Storyboard Maker

## Shared requirements
- Build a scene-by-scene plan for a 9:16 vertical video.
- Each scene must map to a specific narration segment.
- Specify scene number, narration, estimated duration, visual type, visual description/prompt, on-screen text, transition, and asset/source requirements.
- Keep total scene duration aligned with the narration duration.
- Vary composition and visual scale; avoid repeating the same static framing.
- Never describe AI reconstruction as documentary footage.
- Include a visual disclaimer for generated historical or folklore reconstructions where needed.
- Keep important text inside mobile-safe margins and readable at phone size.

## Sejarah Dunia visual direction
Use a hybrid 2D explainer approach. Raka is a consistent guide, not a permanent talking head.
- Use Raka for the opening, selected transitions/explanations, and closing where useful.
- Let the story itself occupy most scenes: historical environments, people, maps, diagrams, timelines, artefacts, comparisons, and simple infographics.
- Keep Raka's established appearance consistent: youthful anime-style male host, warm medium-tan skin, large brown eyes, thick tousled black hair, tan-brown explorer jacket over a black shirt, compass pendant.
- Do not redesign his face, clothing, hair, or signature pendant between scenes.
- Match architecture, clothing, tools, and environment to the correct historical period and region.

## Peta Sunyi visual direction
Use a hybrid documentary mystery treatment with a plain minimalist stickman as the recurring character identity. The stickman is a quiet visual guide, not the star of every shot.
- Stickman design: simple round head, thin clean line-art body and limbs, monochrome, no hair, clothes, shoes, jewellery, or accessories. Keep head/body proportions and line thickness consistent.
- Prefer a blank face; use only tiny simple marks if a facial emotion is essential. Communicate most emotion through posture, silhouette, framing, and movement.
- Never use Raka's anime style, facial details, explorer jacket, compass pendant, or other Sejarah Dunia character traits in Peta Sunyi.
- Use the stickman sparingly for scale, point-of-view, transitions, or symbolic reenactment. Do not force it into every scene.
- The story's locations, architecture, objects, maps, documents, and atmosphere should dominate the frame.
- Avoid a childish/chibi mascot look. Keep the stickman restrained, cinematic, and visually unobtrusive.
- Do not use the stickman to imply a real witness or to present an unverified event as fact.
- Real location/archive images only when a traceable source and reuse status are recorded.
- Maps, historical documents, street/building details, atmospheric establishing shots, and clearly labelled AI reconstructions may be mixed.
- Mark generated reconstructions with "REKA ADEGAN / ILUSTRASI AI".
- Do not fabricate a documentary photograph, archival document, map pin, or evidence.
- If image reuse permission is unclear, mark "reference_only_permission_required"; do not imply it is cleared for publication.
- Do not show private addresses or encourage unsafe access.

## Output schema
Return a storyboard array. Each scene should include:
- scene;
- duration_seconds;
- narration;
- visual_type;
- visual_prompt;
- camera_or_motion;
- on_screen_text;
- transition;
- asset_requirements;
- source_urls (empty array if none);
- visual_disclaimer (or null);
- continuity_notes.

Finish with a scene-duration total and a continuity checklist.