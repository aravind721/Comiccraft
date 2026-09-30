import base64
import io
import re
import uuid
from pathlib import Path

import requests
from PIL import Image

from app.config import get_settings

BASE_DIR = Path(__file__).resolve().parent.parent
PANELS_DIR = BASE_DIR / "static" / "panels"


def _safe_name(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9_-]+", "-", value).strip("-").lower()
    return value[:60] or "panel"


def _hf_generate(prompt: str) -> Image.Image:
    settings = get_settings()
    if not settings.hf_api_key:
        raise RuntimeError("HF_API_KEY is not configured. Add it to your .env file.")

    url = f"https://router.huggingface.co/hf-inference/models/{settings.hf_image_model}"
    response = requests.post(
        url,
        headers={"Authorization": f"Bearer {settings.hf_api_key}"},
        json={"inputs": prompt},
        timeout=180,
    )
    if not response.ok:
        raise RuntimeError(
            f"Hugging Face image generation failed ({response.status_code}): "
            f"{response.text[:500]}"
        )
    return Image.open(io.BytesIO(response.content)).convert("RGB")


def generate_image(image_prompt: str, panel_number: int) -> str:
    image = _hf_generate(image_prompt)
    filename = f"panel-{panel_number}-{_safe_name(str(uuid.uuid4()))}.jpg"
    path = PANELS_DIR / filename
    image.save(path, "JPEG", quality=92, optimize=True)
    return f"/static/panels/{filename}"


def generate_test_image(prompt: str) -> str:
    return generate_image(prompt, 0)
