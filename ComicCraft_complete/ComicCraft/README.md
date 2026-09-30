# ComicCraft — AI Comic Story Creator

ComicCraft is a FastAPI web application based on the supplied project documentation. It creates a five-panel comic through this pipeline:

1. User enters story prompt, character, setting, tone and art style.
2. Gemini generates a structured five-panel outline.
3. Gemini expands the outline into narration, captions and dialogue.
4. Hugging Face image generation creates one illustration per panel.
5. The panels are displayed in a Jinja2 web interface.
6. FPDF2 exports the comic to a PDF.

## Project structure

```text
ComicCraft/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── routes.py
│   ├── config.py
│   ├── schemas.py
│   ├── gemini_flash.py
│   ├── gemini_pro.py
│   ├── image_generator.py
│   ├── layout_builder.py
│   └── exporters.py
├── static/
│   ├── css/style.css
│   ├── panels/
│   └── exports/
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── comic_preview.html
│   ├── export_success.html
│   ├── image_test.html
│   └── error.html
├── tests/test_app.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Windows + VS Code setup

### 1. Install prerequisites

Install:

- Python 3.11 or newer
- VS Code
- Git (optional)

Open the `ComicCraft` folder in VS Code.

### 2. Create the virtual environment

Open **Terminal → New Terminal** in VS Code:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Create the environment file

Copy `.env.example` to `.env`.

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Open `.env` and set:

```text
GEMINI_API_KEY=your_real_gemini_key
HF_API_KEY=your_real_huggingface_token
```

Keep `.env` private. It is ignored by Git.

## 5. Run the application

```powershell
uvicorn app.main:app --reload
```

Open:

- Web app: http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

## 6. Test the image generator

After configuring `HF_API_KEY`, open:

```text
http://127.0.0.1:8000/test-image
```

You can also provide your own prompt:

```text
http://127.0.0.1:8000/test-image?prompt=A%20robot%20detective%20in%20a%20rainy%20city
```

## 7. Test the JSON API

Open `/docs`, select `POST /generate-comic/json`, and use:

```json
{
  "story_prompt": "A brave fox explores an enchanted forest and discovers a hidden glowing library.",
  "character_name": "Finn",
  "setting": "Enchanted forest",
  "tone": "Adventurous",
  "art_style": "Comic book"
}
```

The API returns the panel layout and PDF URL.

## 8. Run automated tests

The tests do not call paid AI APIs:

```powershell
pytest -q
```

## Important model note

The supplied project documentation specified:

- `models/gemini-1.5-flash`
- `models/gemini-1.5-pro`
- `runwayml/stable-diffusion-v1-5`

Model availability changes over time. This implementation therefore puts model names in `.env` instead of hard-coding them throughout the application. If a provider has retired a model, change the corresponding environment variable to a currently available model in your provider account.

## Troubleshooting

### `GEMINI_API_KEY is not configured`

Make sure `.env` exists in the project root and contains:

```text
GEMINI_API_KEY=...
```

Restart Uvicorn after changing `.env`.

### Gemini model not found

Change:

```text
GEMINI_OUTLINE_MODEL=...
GEMINI_STORY_MODEL=...
```

to model IDs currently available to your Gemini API account.

### Hugging Face image generation fails

Check:

- `HF_API_KEY` is valid
- the selected model supports inference
- your Hugging Face account has access to that model
- the provider is not temporarily loading/rate-limiting the model

### PDF contains no image

Make sure the generated image files exist under:

```text
static/panels/
```

### Port 8000 is already in use

Run:

```powershell
uvicorn app.main:app --reload --port 8001
```

Then open http://127.0.0.1:8001

## Security notes

Do not commit `.env` or expose API keys in frontend JavaScript. AI calls are made server-side. For production, add authentication, rate limiting, persistent storage, background jobs, and stricter input/content controls.
