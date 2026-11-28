#!/usr/bin/env python3
"""Free-first Peta Sunyi I2V runner with quota checks and manual execution gate."""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import sys
from urllib.parse import quote

import requests

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from hf_i2v_provider import GradioImageToVideoProvider

MAX_CLIPS_PER_EPISODE = 3
MAX_ESTIMATED_GPU_SECONDS_PER_RUN = 240
DEFAULT_RESERVE_GPU_SECONDS = 60


def validate_plan(config: dict) -> list[dict]:
    episode_id = config.get("episode_id", "")
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]{1,79}", episode_id):
        raise ValueError("episode_id is missing or invalid.")
    section = config.get("motion_generation")
    if not isinstance(section, dict):
        raise ValueError("Episode config needs a motion_generation object.")
    jobs = section.get("scenes")
    if not isinstance(jobs, list) or not jobs:
        raise ValueError("motion_generation.scenes must contain at least one scene.")
    if len(jobs) > MAX_CLIPS_PER_EPISODE:
        raise ValueError(f"Maximum {MAX_CLIPS_PER_EPISODE} I2V clips per episode.")
    seen_shots, seen_outputs = set(), set()
    normalized = []
    for index, job in enumerate(jobs, 1):
        if not isinstance(job, dict):
            raise ValueError(f"Scene job {index} must be an object.")
        shot = str(job.get("shot", "")).strip()
        image_asset = str(job.get("image_asset", "")).strip()
        output = str(job.get("output", f"scene-{index:02d}.mp4")).strip()
        prompt = str(job.get("prompt", "")).strip()
        if not shot or not image_asset or not prompt:
            raise ValueError(f"Scene job {index} needs shot, image_asset and prompt.")
        if pathlib.PurePosixPath(image_asset).name != image_asset or image_asset in (".", ".."):
            raise ValueError(f"Unsafe image_asset path in scene job {index}.")
        if pathlib.PurePosixPath(output).name != output or not output.lower().endswith(".mp4"):
            raise ValueError(f"Output must be a plain .mp4 filename in scene job {index}.")
        if shot in seen_shots or output in seen_outputs:
            raise ValueError("Duplicate shot or output filename in motion_generation.scenes.")
        seen_shots.add(shot)
        seen_outputs.add(output)
        estimate = int(job.get("estimated_gpu_seconds", 60))
        if estimate < 1 or estimate > MAX_ESTIMATED_GPU_SECONDS_PER_RUN:
            raise ValueError("estimated_gpu_seconds must be between 1 and 240.")
        normalized.append({
            **job, "shot": shot, "image_asset": image_asset,
            "output": output, "prompt": prompt,
            "negative_prompt": str(job.get("negative_prompt", "")),
            "estimated_gpu_seconds": estimate,
        })
    total = sum(job["estimated_gpu_seconds"] for job in normalized)
    if total > MAX_ESTIMATED_GPU_SECONDS_PER_RUN:
        raise ValueError(
            f"Estimated GPU budget {total}s exceeds the {MAX_ESTIMATED_GPU_SECONDS_PER_RUN}s per-run cap."
        )
    return normalized


def read_quota(token: str):
    try:
        from huggingface_hub import get_zero_gpu_quota
    except ImportError as exc:
        raise RuntimeError("Install huggingface_hub before using the quota manager.") from exc
    return get_zero_gpu_quota(token=token)


def quota_snapshot(quota) -> dict:
    return {
        "base": float(quota.base),
        "remaining": float(quota.remaining),
        "overquota_used": float(quota.overquota_used or 0),
        "resets_at": quota.resets_at.isoformat() if quota.resets_at else None,
    }


def assert_quota_safe(quota, estimated_seconds: int, reserve_seconds: int = DEFAULT_RESERVE_GPU_SECONDS):
    snap = quota_snapshot(quota)
    if snap["overquota_used"] > 0:
        raise RuntimeError("Paid/over-quota usage is already present; refusing to submit any job.")
    required = estimated_seconds + reserve_seconds
    if snap["remaining"] < required:
        raise RuntimeError(
            f"Insufficient free ZeroGPU quota: remaining={snap['remaining']:.0f}s, "
            f"required={required}s including reserve. No job was submitted."
        )
    return snap


def storage_url(base_url: str, object_path: str) -> str:
    return base_url.rstrip("/") + "/storage/v1/object/visual-assets/" + quote(object_path, safe="/")


def download_source_image(base_url: str, key: str, episode_id: str,
                          image_asset: str, target: pathlib.Path):
    url = storage_url(base_url, f"peta-sunyi/{episode_id}/{image_asset}")
    response = requests.get(url, headers={"apikey": key, "Authorization": f"Bearer {key}"}, timeout=(15, 120))
    response.raise_for_status()
    target.write_bytes(response.content)
    if not target.is_file() or target.stat().st_size == 0:
        raise RuntimeError(f"Source image is empty: {image_asset}")


def upload_video(base_url: str, key: str, episode_id: str,
                 filename: str, video_path: pathlib.Path):
    object_path = f"peta-sunyi/{episode_id}/video/{filename}"
    url = storage_url(base_url, object_path)
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "video/mp4",
        "x-upsert": "false",
    }
    with video_path.open("rb") as handle:
        response = requests.post(url, headers=headers, data=handle, timeout=(30, 600))
    if response.status_code == 409:
        raise RuntimeError(f"Refusing to overwrite existing motion asset: {object_path}")
    response.raise_for_status()
    return object_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--episode-config", required=True)
    parser.add_argument("--assets-dir", default="work/assets")
    parser.add_argument("--output-dir", default="output/i2v")
    parser.add_argument("--plan-only", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.plan_only == args.execute:
        parser.error("Choose exactly one of --plan-only or --execute.")

    config = json.loads(pathlib.Path(args.episode_config).read_text(encoding="utf-8"))
    jobs = validate_plan(config)
    plan = {
        "episode_id": config["episode_id"],
        "max_clips_per_episode": MAX_CLIPS_PER_EPISODE,
        "clip_count": len(jobs),
        "estimated_gpu_seconds": sum(j["estimated_gpu_seconds"] for j in jobs),
        "per_run_gpu_cap_seconds": MAX_ESTIMATED_GPU_SECONDS_PER_RUN,
        "jobs": [{"shot": j["shot"], "image_asset": j["image_asset"],
                  "output": j["output"], "estimated_gpu_seconds": j["estimated_gpu_seconds"]}
                 for j in jobs],
    }
    print("I2V_PLAN=" + json.dumps(plan, ensure_ascii=False))
    if args.plan_only:
        print("PLAN_ONLY=true; no token, quota or provider request used.")
        return

    token = os.getenv("HF_TOKEN", "")
    space_id = os.getenv("HF_I2V_SPACE_ID", "")
    api_name = os.getenv("HF_I2V_API_NAME", "")
    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_key = os.getenv("SUPABASE_SECRET_KEY", "")
    if not all((token, space_id, api_name, supabase_url, supabase_key)):
        raise RuntimeError("Missing HF_TOKEN, HF_I2V_SPACE_ID, HF_I2V_API_NAME or Supabase secrets.")
    image_param = os.getenv("HF_I2V_IMAGE_PARAM", "image")
    prompt_param = os.getenv("HF_I2V_PROMPT_PARAM", "prompt")
    negative_param = os.getenv("HF_I2V_NEGATIVE_PROMPT_PARAM", "")
    reserve = int(os.getenv("HF_I2V_RESERVE_GPU_SECONDS", DEFAULT_RESERVE_GPU_SECONDS))
    estimated_total = plan["estimated_gpu_seconds"]

    quota = read_quota(token)
    snap = assert_quota_safe(quota, estimated_total, reserve)
    print("HF_ZERO_GPU_QUOTA=" + json.dumps(snap))
    provider = GradioImageToVideoProvider(
        space_id, api_name, token, image_param, prompt_param, negative_param
    )
    assets_dir = pathlib.Path(args.assets_dir)
    output_dir = pathlib.Path(args.output_dir)
    assets_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    completed = []
    for job in jobs:
        # Re-check immediately before every single submission; never retry a submitted job.
        quota = read_quota(token)
        current = assert_quota_safe(quota, job["estimated_gpu_seconds"], reserve)
        print(f"HF_QUOTA_GATE=PASS; shot={job['shot']}; remaining={current['remaining']:.0f}s")
        image_path = assets_dir / job["image_asset"]
        if not image_path.is_file():
            download_source_image(supabase_url, supabase_key, config["episode_id"],
                                  job["image_asset"], image_path)
        video_path = provider.generate(image_path, job["prompt"], job["negative_prompt"])
        target = output_dir / job["output"]
        target.write_bytes(video_path.read_bytes())
        if target.stat().st_size == 0:
            raise RuntimeError(f"Provider returned an empty output for shot {job['shot']}.")
        object_path = upload_video(supabase_url, supabase_key, config["episode_id"],
                                   job["output"], target)
        completed.append({"shot": job["shot"], "motion_video_asset": job["output"],
                          "storage_path": object_path})
        print(f"I2V_CLIP_UPLOADED={object_path}")
        video_path.unlink(missing_ok=True)

    print("I2V_GENERATION_COMPLETE=" + json.dumps(completed, ensure_ascii=False))
    print("REVIEW_ONLY=true; NO_PUBLISHING=true; NO_PAID_FALLBACK=true")


if __name__ == "__main__":
    main()
