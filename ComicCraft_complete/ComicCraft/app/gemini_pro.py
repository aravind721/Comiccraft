import json
import re
from typing import List

from google import genai
from google.genai import types

from app.config import get_settings
from app.schemas import PanelOutline, StoryPanel


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


def generate_story(
    outline: List[PanelOutline],
    story_prompt: str,
    character_name: str,
    tone: str,
) -> List[StoryPanel]:
    settings = get_settings()
    outline_json = json.dumps([p.model_dump() for p in outline], ensure_ascii=False)

    prompt = f"""
Expand this five-panel comic outline into polished comic narration.

Original story idea: {story_prompt}
Main character: {character_name}
Tone: {tone}

Outline:
{outline_json}

Return ONLY valid JSON as an array of five objects. Preserve panel_number, title,
scene_description, and image_prompt exactly from the outline. Add:
- caption: a short atmospheric/cinematic caption
- narration: 1-3 sentences describing the action or emotion
- dialogue: concise character dialogue; use an empty string when dialogue is not needed.

Keep the story age-appropriate, coherent, and concise. Do not use markdown.
"""
    response = _client().models.generate_content(
        model=settings.gemini_story_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.85,
            response_mime_type="application/json",
        ),
    )
    data = _extract_json(response.text)
    if not isinstance(data, list) or len(data) != 5:
        raise RuntimeError("Gemini did not return five story panels.")

    return [StoryPanel.model_validate(item) for item in data]
