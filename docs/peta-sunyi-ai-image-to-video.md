# Peta Sunyi — AI image-to-video scene assets

The long-form renderer can now use a generated motion clip as the visual source for an individual scene. This preserves actual subject movement; it does not apply the still-image zoompan to that scene. Animated atmosphere/infographic overlays, subtitles, title cards, narration and review-only export remain active.

## Scene configuration

Add `motion_video_asset` only after an image-to-video clip has been generated and reviewed:

```json
{
  "shot": "lorong-utama",
  "motion_video_asset": "scene-03.mp4",
  "motion_profile": "fog",
  "text": "Narasi untuk adegan ini."
}
```

The corresponding clip must be uploaded to the Supabase Storage bucket `visual-assets` at:

`peta-sunyi/<episode_id>/video/scene-03.mp4`

The review workflow downloads that file automatically. If the property is absent, the renderer keeps the existing still-image path. Clips are looped/trimmed to the scene narration duration, normalized to 1920x1080 at 25 fps, and their source audio is discarded in favor of the approved narration/mix.

## Generation provider

This repository intentionally does not hard-code a paid image-to-video vendor or silently spend credits. Generate clips with the provider/account selected by the channel owner, review them, then upload the approved MP4 to the path above. Provider API automation can be added once a vendor, model, pricing limit, and credentials are explicitly selected.

## Editorial safeguards

- Use image-to-video for scenes where subject motion adds meaning (walking, turning, opening, moving vehicles/objects).
- Keep factual diagrams and evidence graphics in the animated overlay renderer.
- Avoid asking the model to invent documentary evidence. Clearly label AI reconstructions as `REKA ADEGAN • ILUSTRASI AI`.
- Prefer short 4–6 second clips; the renderer loops/holds to fit the narration duration.
- The workflow remains review-only and does not publish automatically.
