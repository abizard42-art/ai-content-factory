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

The free-first adapter is configured for the public ZeroGPU Space `zerogpu-aoti/wan2-2-fp8da-aoti-faster`, endpoint `/generate_video`. Its current app code accepts `input_image`, `prompt`, `steps`, `negative_prompt`, `duration_seconds`, `guidance_scale`, `guidance_scale_2`, `seed` and `randomize_seed`, and returns an MP4 path plus seed. The workflow uses 4 steps and 2.0 seconds as a conservative initial setting. The Space calculates requested GPU duration dynamically; the app formula estimates about 21 GPU-seconds for this setting at common aspect ratios, while our budget reserves 60 seconds per clip. Public Space availability and queue stability are not guaranteed.

## Editorial safeguards

- Use image-to-video for scenes where subject motion adds meaning (walking, turning, opening, moving vehicles/objects).
- Keep factual diagrams and evidence graphics in the animated overlay renderer.
- Avoid asking the model to invent documentary evidence. Clearly label AI reconstructions as `REKA ADEGAN • ILUSTRASI AI`.
- Prefer short 4–6 second clips; the renderer loops/holds to fit the narration duration.
- The workflow remains review-only and does not publish automatically.


## Free-first automated generation (manual dispatch, review only)

The repository now includes a configurable Gradio Space adapter and a manual GitHub Actions workflow:
`.github/workflows/generate-peta-sunyi-i2v-review.yml`.

The workflow has two stages:
1. Plan/validation always runs without contacting a GPU.
2. Generation runs only when the operator explicitly sets `confirm_generation=true`.

It requires these GitHub settings:
- Secret `HF_TOKEN`: the fine-grained Hugging Face token. The token needs `Billing > Read billing usage and payment method status` for ZeroGPU quota reads.
- Variables `HF_I2V_SPACE_ID` and `HF_I2V_API_NAME`: must be filled only after inspecting the selected Space's actual API.
- Optional variables `HF_I2V_IMAGE_PARAM` (default `image`), `HF_I2V_PROMPT_PARAM` (default `prompt`) and `HF_I2V_NEGATIVE_PROMPT_PARAM`.

Do not guess a Space ID, endpoint name, or input parameter names. Inspect the Space's “Use via API” page / `view_api()` first. The adapter submits exactly once per scene; it has no generation retry and no Inference Provider or paid fallback.

### Episode motion plan

Add an optional `motion_generation` block to a long-form episode JSON. Choose no more than three scenes:

```json
{
  "motion_generation": {
    "scenes": [
      {
        "shot": "03A",
        "image_asset": "peta-sunyi-03A.jpg",
        "output": "scene-03.mp4",
        "prompt": "Subtle natural movement in the scene; preserve the original subject and composition.",
        "negative_prompt": "No new people, no extra objects, no text, no scene cuts.",
        "estimated_gpu_seconds": 60
      }
    ]
  }
}
```

Source images are downloaded from `visual-assets/peta-sunyi/<episode_id>/<image_asset>`; generated MP4s are uploaded to `visual-assets/peta-sunyi/<episode_id>/video/<output>`. The long-form renderer maps each generated clip to the scene with the matching `shot`.

### Quota and spending safeguards

- The quota manager reads the authenticated account's live ZeroGPU quota using `huggingface_hub.get_zero_gpu_quota()`; it does not assume a fixed daily allowance.
- Maximum three clips per episode, 240 estimated GPU-seconds per run, and a persistent 240-second internal cap per UTC day stored in Supabase.
- A 60-second reserve is required beyond the estimated run total, and quota is rechecked immediately before each submission.
- The daily ledger reserves the estimate before submission; if a job fails after reservation, the reservation is intentionally retained for safety.
- If the API reports prior over-quota usage, the workflow fails closed.
- No automatic generation retries, no Inference Providers, no paid fallback, no credit purchase, and no automatic publishing.
- The 240-second UTC-day cap is an internal guardrail stored in the existing Supabase `visual-assets` bucket; the provider's live quota is an additional independent gate.
- Generation remains disabled until the Space ID, API endpoint, parameter mapping and episode motion plan have been verified.

The adapter has not yet been connected to a specific model Space or used to generate a clip. A successful plan/test run does not prove that a provider is available or that generation will succeed.
