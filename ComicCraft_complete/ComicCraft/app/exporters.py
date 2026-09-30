import re
import uuid
from pathlib import Path
from urllib.parse import urlparse

from fpdf import FPDF
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
EXPORTS_DIR = BASE_DIR / "static" / "exports"


def _local_image(url_path: str) -> Path:
    parsed = urlparse(url_path)
    relative = parsed.path.lstrip("/")
    path = BASE_DIR / relative
    if not path.exists():
        raise FileNotFoundError(f"Comic image not found: {path}")
    return path


def _clean_text(value: str) -> str:
    value = re.sub(r"\s+", " ", value or "").strip()
    return value


class ComicPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, "ComicCraft", align="C")
        self.ln(8)


def save_pdf(layout, character_name: str) -> str:
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"comic-{uuid.uuid4().hex[:10]}.pdf"
    output = EXPORTS_DIR / filename

    pdf = ComicPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)

    for index, panel in enumerate(layout):
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        title = f"Panel {panel['panel_number']}: {panel['title']}"
        pdf.multi_cell(0, 9, title)
        pdf.ln(3)

        image_path = _local_image(panel["image"])
        with Image.open(image_path) as img:
            width, height = img.size
            max_w, max_h = 180, 105
            ratio = min(max_w / width, max_h / height)
            display_w = width * ratio
            display_h = height * ratio

        x = (210 - display_w) / 2
        pdf.image(str(image_path), x=x, w=display_w, h=display_h)
        pdf.ln(6)

        pdf.set_font("Helvetica", "I", 10)
        pdf.multi_cell(0, 6, _clean_text(panel["scene_description"]))
        pdf.ln(2)

        pdf.set_font("Helvetica", "B", 11)
        if panel.get("caption"):
            pdf.multi_cell(0, 6, f"Caption: {_clean_text(panel['caption'])}")
        if panel.get("narration"):
            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(0, 6, f"Narration: {_clean_text(panel['narration'])}")
        if panel.get("dialogue"):
            pdf.set_font("Helvetica", "B", 11)
            pdf.multi_cell(0, 6, f"Dialogue: {_clean_text(panel['dialogue'])}")

    pdf.output(str(output))
    return f"/static/exports/{filename}"
