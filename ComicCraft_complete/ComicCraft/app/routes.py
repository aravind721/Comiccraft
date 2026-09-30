from pathlib import Path
from typing import Any

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.exporters import save_pdf
from app.gemini_flash import generate_outline
from app.gemini_pro import generate_story
from app.image_generator import generate_image, generate_test_image
from app.layout_builder import build_comic_layout
from app.schemas import PromptRequest

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
router = APIRouter()


def generate_comic(data: PromptRequest) -> dict[str, Any]:
    outline = generate_outline(
        data.story_prompt,
        data.character_name,
        data.setting,
        data.tone,
        data.art_style,
    )
    story = generate_story(
        outline,
        data.story_prompt,
        data.character_name,
        data.tone,
    )

    image_paths = []
    for panel in story:
        prompt = (
            f"{panel.image_prompt}. Comic panel illustration. "
            "Consistent character design across the series. "
            "No text, no letters, no watermark, no logo."
        )
        image_paths.append(generate_image(prompt, panel.panel_number))

    layout = build_comic_layout(story, image_paths)
    pdf_path = save_pdf(layout, data.character_name)
    return {
        "character_name": data.character_name,
        "layout": layout,
        "pdf_path": pdf_path,
    }


@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


@router.post("/generate")
async def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):
    try:
        data = PromptRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )
        result = generate_comic(data)
        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context=result,
        )
    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"error": str(exc)},
            status_code=500,
        )


@router.post("/generate-comic/json")
async def generate_comic_json(payload: PromptRequest):
    try:
        result = generate_comic(payload)
        return JSONResponse(content=result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/download/{filename}")
async def download_pdf(filename: str):
    if "/" in filename or "\\" in filename or filename != Path(filename).name:
        raise HTTPException(status_code=400, detail="Invalid filename.")
    path = BASE_DIR / "static" / "exports" / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="PDF not found.")
    return FileResponse(
        path=str(path),
        media_type="application/pdf",
        filename=filename,
    )


@router.get("/export-success")
async def export_success(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={},
    )


@router.get("/test-image")
async def test_image(request: Request, prompt: str = "A brave fox exploring an enchanted forest, comic book illustration"):
    try:
        image = generate_test_image(prompt)
        return templates.TemplateResponse(
            request=request,
            name="image_test.html",
            context={"image": image, "prompt": prompt},
        )
    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"error": str(exc)},
            status_code=500,
        )


@router.get("/health")
async def health():
    return {"status": "ok", "service": "ComicCraft"}
