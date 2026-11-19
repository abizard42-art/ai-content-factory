# Peta Sunyi — Voice-over Standard & TTS Test Plan

Status: approved editorial standard; implementation pending test results.

## 1. Voice identity

**Primary narrator:** Cinematic Baritone — Balanced Intensity.

The narrator should sound like a mature Indonesian man telling a disturbing experience with control and credibility. The delivery must remain comfortable over 15–20 minutes. Avoid trailer-style exaggeration, constant whispering, artificial growling, excessive bass, or shouting.

| Attribute | Standard |
|---|---|
| Voice | Indonesian male adult |
| Timbre | Mid-low baritone, warm, slightly textured |
| Clarity | Clear consonants; natural Indonesian diction |
| Pace | Medium, flexible by scene |
| Pitch | Natural lower-mid register; no extreme pitch shifting |
| Loudness | Consistent and comfortable; intensity is not simply louder |
| Emotion | Restrained, credible, responsive to story beats |
| Continuity | Same narrator voice and baseline settings across episodes |

## 2. Performance direction by story beat

| Story beat | Delivery direction |
|---|---|
| Opening / hook | Calm, close, inviting; establish curiosity |
| Setting and background | Conversational, steady, clear |
| First anomaly | Slightly slower; alert but not frightened |
| Escalation | More deliberate phrasing; stronger contrast between clauses |
| Peak / immediate danger | Firmer energy and tighter pacing; preserve intelligibility |
| Aftermath | Ease pace; let silence and ambience carry tension |
| Closing | Cooler, restrained, leave the final thought to linger |

Do not make every sentence dramatic. Most narration should stay conversational; only selected words and clauses receive emphasis.

## 3. Timing, pauses, and emphasis

- Use punctuation-aware phrasing. Never insert a pause inside a name or natural phrase.
- Short pause at commas only when the syntax and delivery call for it.
- Medium pause between complete thoughts.
- Longer pause before or after a reveal, not after every sentence.
- Use SSML prosody and break controls only where the selected TTS voice actually supports them.
- Prefer local rate adjustments over global slowing.
- Do not lower pitch aggressively to simulate fear.
- Do not use all-caps as a substitute for performance direction.
- Keep speech intelligible over music and ambience; narration remains the foreground.

Suggested starting ranges for testing (not final locked values):
- Baseline rate: 0% (provider default).
- Alternate rate: approximately -4% to -7% for reflective or suspense passages.
- Pitch: provider default first; test only a subtle downward adjustment if it improves the voice without sounding artificial.
- Breaks: compare short and medium pauses at clause/reveal boundaries; do not blanket-insert them.

## 4. Narration text preparation

- Preserve every word in the approved script.
- Do not paraphrase, summarize, or omit text during TTS preparation.
- Split long narration into semantic phrases for timing and subtitle alignment.
- Keep names, locations, and Indonesian pronunciation consistent.
- Any invented dialogue must be identified editorially as dramatized reconstruction when the source is an account without recorded dialogue.

## 5. TTS audition plan

Use one identical Indonesian test script for every candidate voice and setting. Do not compare different text, different background music, or different loudness.

### Test passage (same text for all candidates)

> Awalnya, tidak ada yang terasa aneh malam itu. Angin bergerak pelan di antara pepohonan, sementara kami mulai membereskan barang-barang di sekitar tenda. Tapi beberapa menit kemudian, terdengar sesuatu dari arah hutan. Bukan suara ranting patah. Bukan pula langkah orang yang sedang berjalan. Suaranya pelan, teratur, dan semakin dekat. Saat itu, tidak seorang pun dari kami berani menoleh.

### Candidate matrix

1. Current baseline: id-ID-ArdiNeural, default rate and pitch.
2. Same voice: carefully paced version with semantic pauses and restrained rate variation.
3. One or more available Indonesian male neural voices discovered from the provider's current voice list; default settings.
4. Best alternative voice with the same restrained pacing treatment.

Do not assume a voice supports named emotional styles. Verify available voice capabilities before using style/emotion tags. If the provider exposes only general prosody controls, use rate, pitch, breaks, punctuation, and phrase segmentation; do not label that as true emotion synthesis.

### Listening criteria

Score each sample from 1–5:
- Comfort over a long listen.
- Natural Indonesian pronunciation.
- Warmth and credibility.
- Low-mid resonance without muddiness.
- Ability to make suspenseful lines feel tense without overacting.
- Phrase rhythm and pauses.
- Absence of robotic cadence, clipped endings, or strange emphasis.

Normalize perceived loudness before judging. Listen once on headphones and once on ordinary phone/desktop speakers. Keep music and SFX off during the first comparison.

### Decision rule

Choose the voice with the strongest combined comfort, naturalness, and credibility—not simply the deepest voice. If the baseline voice wins, retain it and improve phrase direction. Lock the chosen voice and settings only after listening tests.

## 6. Multi-character voice test

The Lembang pilot is primarily narration and is not sufficient to judge character separation. Create a separate 30–45 second audition scene with:
- Narrator: approved cinematic baritone.
- Male witness: lighter, more conversational male voice.
- Female witness: natural adult female voice, clear and restrained.

Use the same short exchange for every test. Check that speakers are distinguishable without caricature, that dialogue sounds conversational, and that volume/timbre remain consistent. A mysterious voice is optional and should only be added when a story actually needs it.

## 7. Release gates

Do not replace the production voice based only on a generated sample or provider marketing description. Approve only after:
1. All candidates use identical text.
2. Samples are loudness-matched.
3. Listening scores are recorded.
4. Long-listen comfort is checked.
5. A multi-character scene is tested separately.

This document defines the editorial target. It does not claim that the renderer already supports expressive performance or that a new voice has been selected.


## 8. Implemented scene-level delivery controls

The long-form renderer now reads an optional `delivery` field on each scene:
- `natural`: provider-default continuous delivery; best for calm exposition.
- `paced`: sentence-aware delivery at a restrained slower rate, with medium sentence pauses.
- `suspense`: phrase-aware delivery, including selected comma boundaries, with longer pauses at sentence endings.
- `reflective`: slower reflective phrasing with room for aftermath and closing thoughts.
- `urgent`: firmer baseline pace with short sentence gaps for immediate danger.

Optional `dramatic_pause_after` is an array of exact phrase strings. A matching phrase receives an additional 850 ms hold. Use sparingly, only before/after a reveal or a major sound cue. The renderer retains the same speaker voice; these controls change pacing and silence, not the speaker identity or true emotional acting.

For scenes without a `delivery` field, the renderer keeps the previous natural behavior. Scene text is split only at punctuation boundaries, and the generated VTT timings are offset and reassembled so subtitle coverage remains aligned. The subtitle renderer continues to preserve the complete approved script and limits each displayed card to six words.

The Lembang pilot uses natural delivery for the opening and setup, suspense/paced delivery for the anomalies, urgent delivery for the immediate danger, and reflective delivery for the aftermath and closing. These assignments are a first editorial pass and should be reviewed by listening to the rendered episode.
