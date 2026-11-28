#!/usr/bin/env python3
"""Configurable Gradio/Hugging Face Space adapter for image-to-video."""
from __future__ import annotations

import pathlib
import shutil
import tempfile
from urllib.parse import urlparse

import requests


class GradioImageToVideoProvider:
    """Call one inspected Gradio endpoint. No retries are performed."""

    def __init__(self, space_id: str, api_name: str, token: str,
                 image_param: str = "image", prompt_param: str = "prompt",
                 negative_prompt_param: str = ""):
        if not space_id or "/" not in space_id:
            raise ValueError("HF_I2V_SPACE_ID must be a Hugging Face Space id (owner/name).")
        if not api_name or not api_name.startswith("/"):
            raise ValueError("HF_I2V_API_NAME must start with '/'.")
        self.space_id = space_id
        self.api_name = api_name
        self.image_param = image_param
        self.prompt_param = prompt_param
        self.negative_prompt_param = negative_prompt_param
        try:
            from gradio_client import Client
        except ImportError as exc:
            raise RuntimeError("Install gradio_client before using the HF provider.") from exc
        self.client = Client(space_id, token=token, verbose=False)

    def generate(self, image_path: pathlib.Path, prompt: str,
                 negative_prompt: str = "") -> pathlib.Path:
        from gradio_client import handle_file

        kwargs = {
            self.image_param: handle_file(str(image_path)),
            self.prompt_param: prompt,
        }
        if self.negative_prompt_param and negative_prompt:
            kwargs[self.negative_prompt_param] = negative_prompt

        # Deliberately one submission only: no automatic retry can consume extra quota.
        result = self.client.predict(api_name=self.api_name, **kwargs)
        return self._materialize_video(result)

    @staticmethod
    def _materialize_video(value) -> pathlib.Path:
        """Find the first returned video file/path/url and copy it to a stable temp path."""
        if isinstance(value, (list, tuple)):
            for item in value:
                try:
                    return GradioImageToVideoProvider._materialize_video(item)
                except (TypeError, ValueError, FileNotFoundError):
                    continue
        if isinstance(value, dict):
            for key in ("video", "path", "url", "name"):
                if key in value:
                    try:
                        return GradioImageToVideoProvider._materialize_video(value[key])
                    except (TypeError, ValueError, FileNotFoundError):
                        pass
        for attr in ("path", "url"):
            candidate = getattr(value, attr, None)
            if candidate:
                try:
                    return GradioImageToVideoProvider._materialize_video(candidate)
                except (TypeError, ValueError, FileNotFoundError):
                    pass
        if isinstance(value, pathlib.Path):
            source = value
        elif isinstance(value, str):
            parsed = urlparse(value)
            if parsed.scheme in ("http", "https"):
                response = requests.get(value, timeout=(15, 180), stream=True)
                response.raise_for_status()
                suffix = pathlib.Path(parsed.path).suffix or ".mp4"
                fd, temp_name = tempfile.mkstemp(prefix="peta-sunyi-i2v-", suffix=suffix)
                import os
                os.close(fd)
                target = pathlib.Path(temp_name)
                with target.open("wb") as handle:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            handle.write(chunk)
                if target.stat().st_size == 0:
                    target.unlink(missing_ok=True)
                    raise ValueError("Provider returned an empty video.")
                return target
            source = pathlib.Path(value)
        else:
            raise TypeError(f"Unsupported provider output type: {type(value).__name__}")
        if not source.is_file() or source.stat().st_size == 0:
            raise FileNotFoundError("Provider output is not an existing, non-empty file.")
        fd, temp_name = tempfile.mkstemp(prefix="peta-sunyi-i2v-", suffix=source.suffix or ".mp4")
        import os
        os.close(fd)
        target = pathlib.Path(temp_name)
        shutil.copyfile(source, target)
        return target
