# Peta Sunyi — Long Horror Production Standard

Status: v1.1 — dedicated long-form pipeline added  
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
