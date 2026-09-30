import json
import re
from typing import List

from google import genai
from google.genai import types

from app.config import get_settings
from app.schemas import PanelOutline


def _client() -> genai.Client:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured. Add it to your .env file.")
    return genai.Client(api_key=settings.gemini_api_key)


def _extract_json(text: str):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("[")
        end = text.rfind("]")
        if start >= 0 and end > start:
            return json.loads(text[start:end + 1])
        raise


def generate_outline(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
) -> List[PanelOutline]:
    settings = get_settings()
    prompt = f"""
Create a cohesive five-panel comic outline.

User story idea: {story_prompt}
Main character: {character_name}
Setting: {setting}
Tone: {tone}
Art style: {art_style}

Return ONLY valid JSON, as an array of exactly five objects.
Each object must contain:
- panel_number: integer 1 through 5
- title: short panel title
- scene_description: 1-3 sentences describing what happens visually
- image_prompt: a detailed image-generation prompt. Include the character's
  appearance consistently, setting, action, composition, lighting, and the requested
  art style. Do not put speech bubbles or written text in the image.

Make the five panels form one continuous story with a beginning, development,
climax, and ending.
"""
    response = _client().models.generate_content(
        model=settings.gemini_outline_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.8,
            response_mime_type="application/json",
        ),
    )
    data = _extract_json(response.text)
    if not isinstance(data, list) or len(data) != 5:
        raise RuntimeError("Gemini did not return exactly five panels.")

    return [PanelOutline.model_validate(item) for item in data]
