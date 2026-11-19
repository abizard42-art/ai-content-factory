# Peta Sunyi — Long Horror Production Standard

Status: v1.2 — scene-aware narration delivery added  
Target: YouTube long-form horror stories; runtime is determined by the approved script, not padded to a target.  
Frame: 16:9 landscape, 1920×1080, 25 fps.

## Editorial rules

- Preserve the chronology and details of the source. Never invent a witness, incident, exact campsite, quote, or supernatural claim.
- Label the source accurately: verified interview, published first-person account, anonymous submission, urban legend, or fictional adaptation.
- An anonymous/unverified account must be identified as such in the video and description. Do not market it as proven true.
- Dialogue written for pacing is a dramatized reconstruction, not a verbatim quote.
- Add atmosphere and reflective narration, but do not use invented events to inflate runtime.
- Protect private identities. Use licensed, public-domain, or original music and SFX.

## Pipeline

1. Episode config: `episodes/peta-sunyi/<episode_id>.json`.
2. Visual prompts: `assets/peta-sunyi/<episode_id>/asset-manifest.json`.
3. Generate 16:9 stills: GitHub Actions workflow **Generate Peta Sunyi long-form horror assets**.
4. Render review video: GitHub Actions workflow **Render Peta Sunyi long horror review**.
5. Inspect the MP4 artifact and approve edits manually. The workflow does not publish to YouTube.

Renderer: `scripts/peta-sunyi/render_long_horror.py`. This is separate from the existing portrait Shorts renderer; the two formats do not share canvas settings.

## Voice cast

- The renderer supports a separate Edge TTS voice for each `speaker` ID.
- Current Indonesian voices configured for the pilot: NARATOR = `id-ID-ArdiNeural`; TEMAN = `id-ID-GadisNeural`.
- Keep assignments consistent. A voice is an acting device, not evidence of a person's actual identity or gender.
- Avoid excessive acting, shouting, or fake distress. Never present invented dialogue as a verbatim quote.

## Subtitle standard

- Burned-in subtitles, maximum two lines per cue.
- A small speaker label appears above dialogue.
- Check timing manually around pauses and interruptions.
- Keep text inside title/action safe zones and readable on a phone.

## Visual direction: rough pencil / charcoal

Preferred style: monochrome rough graphite storyboard, visible pencil grain, scratchy cross-hatching, imperfect hand-drawn contours, deep charcoal shadows, paper texture, restrained highlights. Avoid glossy photorealistic AI art, clean vector art, anime, and explicit monster close-ups.

Prompts should describe a wide 16:9 composition and include:
"rough graphite pencil storyboard illustration, charcoal shading, scratchy cross-hatching, imperfect hand-drawn linework, visible paper grain, high-contrast monochrome, unsettling negative space, cinematic wide composition, no text, no watermark"

The renderer applies a restrained monochrome graphite edge treatment after generation. This treatment cannot turn an unsuitable source image into a convincing drawing; prompt quality and visual review remain essential. AI illustrations are reconstructions, not documentary photographs or evidence.

## Sound design

Each scene may optionally specify:
- `ambience_asset`: continuous atmosphere, looped quietly under the voice.
- `music_asset`: continuous music bed, looped at a lower level.
- `sfx_asset`: one-shot effect, delayed by `sfx_delay_ms` (default 900 ms).

Files are stored in the private Supabase `visual-assets` bucket at:
`peta-sunyi/<episode_id>/audio/<filename>`.

The render workflow downloads configured layers. The renderer mixes voice, ambience, music, and SFX; voice remains the primary track. Do not imply designed SFX are recordings from the actual location. Use licensed, public-domain, or original audio only. Review on phone speakers and headphones; listen for clipping, masking, and abrupt transitions.

## Episode JSON contract

Required:
- `episode_id`
- `title`
- `scenes[]`, each with `shot`, `text`; optional `title`, `speaker`
- `speaker_voices` maps speaker IDs to Edge TTS voice names.

Optional:
- `visual_style`: `rough_pencil` (default for the pilot).
- Per-scene `delivery`: `natural`, `paced`, `suspense`, `reflective`, or `urgent`.
- Per-scene `dramatic_pause_after`: exact phrase strings that receive an additional 850 ms hold; use sparingly.
- Per-scene `tts_rate`, `tts_pitch`, and `tts_volume` can override delivery defaults.
- Per-scene `ambience_asset`, `music_asset`, `sfx_asset`, and `sfx_delay_ms`.

Example:

~~~json
{
  "episode_id": "example-long-horror",
  "title": "Judul Cerita",
  "visual_style": "rough_pencil",
  "speaker_voices": {
    "NARATOR": "id-ID-ArdiNeural",
    "TEMAN": "id-ID-GadisNeural"
  },
  "scenes": [
    {
      "shot": "01A",
      "title": "PEMBUKA",
      "speaker": "NARATOR",
      "text": "Narasi yang sudah diverifikasi atau diberi label sebagai rekonstruksi."
    },
    {
      "shot": "02A",
      "title": "DIALOG",
      "speaker": "TEMAN",
      "text": "Dialog rekonstruksi, bukan kutipan asli."
    }
  ]
}
~~~

## Preflight checklist

- [ ] Source link and source status recorded.
- [ ] Timeline and details checked; uncertainty flagged.
- [ ] Reconstructed dialogue clearly disclosed.
- [ ] Voice IDs and assignments tested.
- [ ] Character, clothing, tent, and campsite continuity reviewed.
- [ ] Every scene has a distinct visual purpose.
- [ ] Subtitle labels, timing, line breaks, and safe areas checked.
- [ ] Music/SFX rights recorded.
- [ ] Mix checked on phone speaker and headphones.
- [ ] Final video watched from beginning to end.
- [ ] Title, thumbnail, and description do not overstate evidence.
- [ ] Upload remains manual until explicitly approved.


## Scene-aware narration direction

The script planner (including Gemini when used to draft a scene plan) must assign one `delivery` value to every scene based on its narrative function. Do not apply suspense delivery to the entire episode.

| Delivery | Use when | Renderer behavior |
|---|---|---|
| `natural` | Opening, factual context, ordinary action | Existing continuous provider-default TTS |
| `paced` | A first anomaly or a moment that needs clearer phrasing | Sentence segmentation, -3% rate, 320 ms sentence pauses |
| `suspense` | Uncertainty, approaching threat, reveal setup | Phrase segmentation at sentence and comma boundaries, -5% rate, 170 ms comma / 460 ms sentence pauses |
| `reflective` | Aftermath, realization, unresolved ending | Phrase segmentation at sentence and comma boundaries, -4% rate, 220 ms comma / 520 ms sentence pauses |
| `urgent` | Immediate danger or frantic action | Sentence segmentation, default rate, 170 ms sentence pauses |

Gemini/script planning should:
1. Choose the delivery from the scene's function, not merely from scary vocabulary.
2. Keep most exposition `natural`; use special delivery only where it improves the listener's experience.
3. Add `dramatic_pause_after` only for a specific reveal, impact, or important sound cue. Each entry must exactly match one phrase produced by punctuation splitting; avoid vague directions.
4. Never alter or omit the approved narration text to create a pause. Pauses are timing instructions, not script edits.
5. Keep the same narrator voice ID throughout. Delivery changes pace and silence; it does not claim to create human-like emotional acting.

If `delivery` is omitted, the renderer defaults to `natural` so older episode JSON files remain compatible.
