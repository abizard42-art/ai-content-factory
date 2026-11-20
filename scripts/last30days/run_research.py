#!/usr/bin/env python3
"""Run pinned Last30Days research and upload private Markdown reports to Supabase."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

UPSTREAM_COMMIT = "262391603f3c2807606bffa0170547273fc273e5"
BUCKET = "research-reports"
KEYLESS_SOURCES = "reddit,hackernews,polymarket,grounding,github,youtube"

PROFILES = {
    "peta-sunyi": {
        "register": "creator",
        "prompt": (
            "Riset peluang konten Peta Sunyi: sejarah lokal Indonesia, tempat bersejarah, "
            "misteri yang dapat diverifikasi, folklore yang dipisahkan dari fakta, kisah lokasi, "
            "arsip, dan pertanyaan komunitas. Cari sudut cerita yang kuat untuk video dokumenter "
            "sinematik; jangan mengubah rumor menjadi fakta."
        ),
    },
    "sejarah-dunia": {
        "register": "creator",
        "prompt": (
            "Riset Sejarah Dunia: peristiwa, tokoh, peradaban, budaya berbagai negara, fakta unik, "
            "pertanyaan audiens, dan topik sejarah yang sedang ramai dibicarakan. Utamakan sudut "
            "cerita yang akurat, menarik, dan bisa dikembangkan menjadi video edukasi."
        ),
    },
    "ai-content-factory": {
        "register": "creator",
        "prompt": (
            "Riset AI Content Factory: perkembangan alat AI, workflow otomatisasi konten, "
            "YouTube Shorts/TikTok, kebutuhan kreator, keluhan pengguna, celah kompetitor, "
            "dan peluang peningkatan sistem produksi konten."
        ),
    },
    "business-opportunity": {
        "register": "exec",
        "prompt": (
            "Riset radar peluang bisnis untuk pasar Indonesia. Temukan masalah berulang, keluhan "
            "nyata, kebutuhan yang belum terpenuhi, solusi yang ada, kesediaan membayar, tingkat "
            "persaingan, dan bukti permintaan. Prioritaskan peluang bermodal awal rendah, dapat "
            "dijalankan dari rumah secara online oleh satu orang atau tim kecil. Bedakan sinyal "
            "viral dari bukti permintaan bisnis; jangan mengklaim willingness-to-pay tanpa bukti."
        ),
    },
}


def request_json(url: str, method: str, headers: dict[str, str], body: bytes | None = None):
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            payload = response.read()
            return response.status, payload
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()


def ensure_private_bucket(base: str, secret: str) -> None:
    url = f"{base}/storage/v1/bucket/{BUCKET}"
    headers = {"apikey": secret, "Authorization": f"Bearer {secret}"}
    status, payload = request_json(url, "GET", headers)
    if status == 404:
        create_headers = {**headers, "Content-Type": "application/json"}
        body = json.dumps({"id": BUCKET, "name": BUCKET, "public": False}).encode()
        create_status, _ = request_json(
            f"{base}/storage/v1/bucket", "POST", create_headers, body
        )
        if create_status not in (200, 201, 409):
            raise RuntimeError(f"Gagal membuat private bucket (HTTP {create_status}).")
        status, payload = request_json(url, "GET", headers)
    if status != 200:
        raise RuntimeError(f"Gagal memeriksa bucket Supabase (HTTP {status}).")
    try:
        bucket = json.loads(payload)
    except (TypeError, json.JSONDecodeError) as exc:
        raise RuntimeError("Respons pemeriksaan bucket tidak valid.") from exc
    if bucket.get("public") is not False:
        raise RuntimeError(
            "Bucket research-reports tidak terverifikasi private; upload dihentikan."
        )


def upload_private_report(base: str, secret: str, object_path: str, report: Path) -> None:
    encoded_path = urllib.parse.quote(object_path, safe="/")
    url = f"{base}/storage/v1/object/{BUCKET}/{encoded_path}"
    headers = {
        "apikey": secret,
        "Authorization": f"Bearer {secret}",
        "Content-Type": "text/markdown; charset=utf-8",
        "x-upsert": "true",
        "cache-control": "no-store",
    }
    status, _ = request_json(url, "POST", headers, report.read_bytes())
    if status not in (200, 201):
        raise RuntimeError(f"Upload laporan privat gagal (HTTP {status}).")


def build_topic(scope: str, focus: str) -> str:
    base = PROFILES[scope]["prompt"]
    if focus.strip():
        base += f"\nFokus tambahan dari pengguna: {focus.strip()}"
    base += (
        "\nAnalisis bukti dan percakapan dalam 30 hari terakhir. Cantumkan tanggal, "
        "tautan sumber yang benar-benar dikumpulkan, metrik engagement bila tersedia, "
        "pola keluhan/pertanyaan, kontra-bukti, tingkat keyakinan, dan hal yang masih perlu "
        "diverifikasi. Jangan mengarang angka, kutipan, atau sumber."
    )
    return base


def run_one(scope: str, focus: str, engine: Path, base: str, secret: str, run_id: str):
    profile = PROFILES[scope]
    topic = build_topic(scope, focus)
    with tempfile.TemporaryDirectory(prefix=f"last30days-{scope}-") as tmp:
        report = Path(tmp) / f"{scope}.md"
        env = os.environ.copy()
        # Force the free/local route. No provider or metered-source credentials are passed.
        for key in (
            "LAST30DAYS_API_KEY", "LAST30DAYS_API_BASE", "OPENAI_API_KEY",
            "XAI_API_KEY", "X_BEARER_TOKEN", "OPENROUTER_API_KEY",
            "PERPLEXITY_API_KEY", "PARALLEL_API_KEY", "SCRAPECREATORS_API_KEY",
            "BRAVE_API_KEY", "APIFY_API_TOKEN", "GEMINI_API_KEY",
            "GOOGLE_API_KEY", "GOOGLE_GENAI_API_KEY", "AUTH_TOKEN", "CT0",
            "TRUTHSOCIAL_TOKEN",
        ):
            env[key] = ""
        env["LAST30DAYS_MEMORY_DIR"] = ""
        env["LAST30DAYS_STORE"] = "0"
        env["LAST30DAYS_LIBRARY_CONTEXT"] = "off"
        env["LAST30DAYS_DEFAULT_SEARCH"] = ""
        env["LAST30DAYS_NATIVE_SEARCH"] = "0"
        command = [
            sys.executable, str(engine), topic,
            "--research-only", "--emit=md",
            f"--register={profile['register']}",
            f"--search={KEYLESS_SOURCES}",
            "--no-browser-cookies",
            "--auto-resolve",
            "--output", str(report),
        ]
        print(f"Menjalankan riset scope: {scope}")
        result = subprocess.run(command, env=env, stdout=subprocess.DEVNULL, check=False)
        if result.returncode != 0:
            raise RuntimeError(
                f"Engine Last30Days gagal untuk {scope} (exit {result.returncode})."
            )
        if not report.is_file() or report.stat().st_size < 300:
            raise RuntimeError(f"Laporan {scope} kosong atau tidak lengkap.")
        if report.stat().st_size > 10 * 1024 * 1024:
            raise RuntimeError(f"Laporan {scope} melebihi batas 10 MB.")
        date = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
        object_path = f"{scope}/{date}/run-{run_id}.md"
        upload_private_report(base, secret, object_path, report)
        print(f"PRIVATE_REPORT_SAVED={BUCKET}/{object_path}")
        print(f"REPORT_BYTES={report.stat().st_size}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", choices=["all", *PROFILES], required=True)
    parser.add_argument("--topic", default="")
    parser.add_argument("--engine", required=True, type=Path)
    args = parser.parse_args()

    base = os.environ.get("SUPABASE_URL", "").rstrip("/")
    secret = os.environ.get("SUPABASE_SECRET_KEY", "")
    run_id = os.environ.get("GITHUB_RUN_ID", "manual")
    if not base or not secret:
        raise SystemExit("GitHub Secrets SUPABASE_URL dan SUPABASE_SECRET_KEY wajib tersedia.")
    if not args.engine.is_file():
        raise SystemExit("Engine Last30Days tidak ditemukan.")
    ensure_private_bucket(base, secret)

    scopes = list(PROFILES) if args.scope == "all" else [args.scope]
    failures = []
    for scope in scopes:
        try:
            run_one(scope, args.topic, args.engine, base, secret, run_id)
        except Exception as exc:
            failures.append(f"{scope}: {exc}")
            print(f"ERROR: {scope}: {exc}", file=sys.stderr)
    if failures:
        print(f"Riset selesai dengan {len(failures)} kegagalan.", file=sys.stderr)
        return 1
    print(f"SELESAI: {len(scopes)} laporan tersimpan di bucket private {BUCKET}.")
    print("Tidak ada laporan yang dipublikasikan atau diunggah sebagai Actions artifact.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
