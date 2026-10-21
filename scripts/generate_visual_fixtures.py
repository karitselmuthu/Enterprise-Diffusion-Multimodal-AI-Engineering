"""Regenerate labeled synthetic dashboard and PDF fixtures."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

ROOT = Path(__file__).resolve().parents[1] / "data" / "evaluation"
FONT_PATH = Path("/System/Library/Fonts/Supplemental/Arial.ttf")


def font(size: int):
    return ImageFont.truetype(str(FONT_PATH), size) if FONT_PATH.exists() else ImageFont.load_default()


def dashboard(name: str, heading: str, status: str, detail: str, accent: str) -> None:
    image = Image.new("RGB", (900, 500), "#111827")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((28, 28, 872, 472), radius=20, fill="#1f2937", outline="#4b5563", width=3)
    draw.text((60, 58), heading, font=font(42), fill="white")
    draw.line((60, 125, 840, 125), fill="#6b7280", width=2)
    draw.rounded_rectangle((60, 165, 840, 335), radius=16, fill=accent)
    draw.text((88, 202), status, font=font(52), fill="white")
    draw.text((64, 380), detail, font=font(32), fill="#e5e7eb")
    image.save(ROOT / name)


def pdf_note() -> None:
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    font_object = writer._add_object(DictionaryObject({
        NameObject("/Type"): NameObject("/Font"),
        NameObject("/Subtype"): NameObject("/Type1"),
        NameObject("/BaseFont"): NameObject("/Helvetica"),
    }))
    page[NameObject("/Resources")] = DictionaryObject({
        NameObject("/Font"): DictionaryObject({NameObject("/F1"): font_object})
    })
    content = DecodedStreamObject()
    content.set_data(b"BT /F1 18 Tf 72 720 Td (Valve leak reported in west zone.) Tj ET")
    page[NameObject("/Contents")] = writer._add_object(content)
    with (ROOT / "valve_report.pdf").open("wb") as output:
        writer.write(output)


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    dashboard("smoke_dashboard.png", "SERVER ROOM 4", "SMOKE DETECTED", "Sensor 7  |  Alarm active", "#991b1b")
    dashboard("pressure_dashboard.png", "PUMP 2", "PRESSURE HIGH", "Gauge 114 psi  |  Alarm active", "#92400e")
    dashboard("normal_dashboard.png", "PUMP 2", "SYSTEM NORMAL", "Gauge 62 psi  |  No active alarms", "#166534")
    dashboard("network_dashboard.png", "NETWORK CORE", "LINK FAILURE", "Switch 12  |  Port 8 down", "#7c2d12")
    pdf_note()


if __name__ == "__main__":
    main()
