# Peta Sunyi — Long Horror Production Standard

Status: production specification v1.0  
Target: YouTube long-form horror stories, 10–15 minutes  
Frame: 16:9 landscape (1920×1080), 25 or 30 fps  
Editorial model: one central story, one main witness/source, multi-voice dramatization only where the source supports it.

## Editorial rules

- Research and preserve the source chronology. Never invent a witness, incident, location, quote, or supernatural claim.
- Label the story accurately: verified interview, published first-person account, anonymous submission, urban legend, or fictionalized adaptation.
- If a story is anonymous/unverified, say so in the opening or end card and video description. Do not market it as a proven true case.
- Dialogue written for pacing is a dramatized reconstruction, not a verbatim quote. Mark it in production notes.
- Do not add new plot events to stretch runtime. Add atmosphere, context, and reactions only when supported or clearly identified as reconstruction.
- Protect private identities. Use licensed, public-domain, or original music/SFX.

## Runtime and pacing

Aim for 1,350–1,750 spoken Indonesian words for 10–15 minutes, adjusted to actual TTS pace and pauses. Do not pad with repetition.

1. Cold open: 0:00–0:40 — strongest sourced moment.
2. Context/location: 0:40–1:45 — only history needed to understand the incident.
3. Witness and ordinary setup: 1:45–3:15.
4. First anomaly: 3:15–5:00.
5. Escalation: 5:00–8:30.
6. Main climax: 8:30–11:30.
7. Aftermath / what is and is not known: 11:30–13:30.
8. Quiet closing question and source note: final 30–60 seconds.

Timings are flexible; evidence and natural pacing take priority.

## Voice cast

Suggested cast:
- NARATOR: calm, intimate storyteller; default id-ID-ArdiNeural.
- TOKOH_1: natural conversational voice; test a distinct Indonesian voice such as id-ID-GadisNeural where appropriate to the character.
- TOKOH_2: choose a distinct supported voice; do not assign gender or identity unsupported by the source.

Episode JSON may map IDs to Edge TTS voices through the speaker_voices object. Each scene may specify speaker; omitted speaker defaults to NARATOR. Keep assignments consistent. Avoid excessive acting, shouting, or fake distress. Never present invented dialogue as a verbatim quote.

## Subtitle standard

- Burned-in subtitles, max two lines per cue.
- Show a small speaker label above dialogue.
- Preserve natural punctuation and Indonesian spelling.
- Keep subtitles inside title/action safe zones and away from bottom UI.
- Convey speaker identity through label as well as restrained accent color; never rely on color alone.
- Review timing manually around pauses and interruptions.

## Visual direction: rough pencil / charcoal

Preferred style: monochrome rough graphite storyboard, visible pencil grain, scratchy cross-hatching, imperfect hand-drawn contours, deep charcoal shadows, paper texture, restrained highlights. Avoid glossy photorealistic AI art, clean vector art, anime, and explicit monster close-ups.

Prompt suffix:
"rough graphite pencil storyboard illustration, charcoal shading, scratchy cross-hatching, imperfect hand-drawn linework, visible paper grain, high-contrast monochrome, unsettling negative space, cinematic composition, no text, no watermark"

Create a continuity sheet for campers, clothing, hair silhouettes, tent, campsite layout, tree line, path, lantern, recurring props, and any ambiguous figure. Use wide establishing shots, medium character blocking, POV shots, inserts, and negative-space frames. Do not repeat one image with only a different crop. Label reconstructions clearly.

## Sound design and mix

Track layout:
- A1: narration / dialogue.
- A2: ambience (forest, wind, distant insects).
- A3: designed SFX (footsteps, fabric, bell, branch snap) only when appropriate.
- A4: music bed (low, sparse, licensed/original).

Voice remains intelligible on phone speakers. Duck music and ambience under speech. Avoid clipping and sudden loudness spikes; use fades and silence deliberately. Do not imply designed SFX are recordings from the real location. Review loudness, true peak, mono compatibility, phone playback, and headphones.

## Episode JSON contract

Existing renderer fields remain required: episode_id, title, map, fact, end, and scenes. Optional long-horror fields:

~~~json
{
  "format": "long_horror",
  "visual_style": "rough_pencil",
  "speaker_voices": {
    "NARATOR": "id-ID-ArdiNeural",
    "TOKOH_1": "id-ID-GadisNeural",
    "TOKOH_2": "id-ID-ArdiNeural"
  },
  "scenes": [
    {
      "shot": "01A",
      "title": "COLD OPEN",
      "kind": "ai",
      "speaker": "NARATOR",
      "text": "Narasi untuk bagian ini."
    },
    {
      "shot": "02A",
      "title": "DI DALAM TENDA",
      "kind": "ai",
      "speaker": "TOKOH_1",
      "text": "Dialog rekonstruksi yang diberi label sebagai dramatisasi."
    }
  ]
}
~~~

Notes:
- speaker selects the voice and subtitle label.
- speaker_voices maps speaker IDs to Edge TTS voice names.
- visual_style rough_pencil applies a monochrome graphite treatment to AI stills. Prompts should already request pencil/charcoal art; post-processing cannot fully turn photorealism into convincing hand-drawn art.
- Keep one spoken beat per scene where practical.
- Existing MAP/FACT/END graphic templates need layout review before use in landscape episodes.

## Preflight checklist

- [ ] Source link and source status recorded.
- [ ] Timeline checked; uncertainty flagged.
- [ ] Invented dialogue marked as dramatized reconstruction.
- [ ] Voice IDs and assignments tested.
- [ ] Character/location continuity sheet approved.
- [ ] Every scene has a distinct visual prompt and shot purpose.
- [ ] Subtitle labels, timing, line breaks, and safe areas checked.
- [ ] Music/SFX rights recorded.
- [ ] Mix checked on phone speaker and headphones.
- [ ] Final video watched from beginning to end.
- [ ] Title, thumbnail, and description do not overstate evidence.
- [ ] Upload remains manual until explicitly approved.
