"""Generate 24 varied, source-labeled synthetic dashboard images."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1] / "data" / "evaluation" / "dashboard_matrix"
FONT_PATH = Path("/System/Library/Fonts/Supplemental/Arial.ttf")


def font(size: int):
    return ImageFont.truetype(str(FONT_PATH), size) if FONT_PATH.exists() else ImageFont.load_default()


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    statuses = ("PRESSURE HIGH", "SYSTEM NORMAL", "LINK FAILURE", "SMOKE DETECTED")
    readings = ("114 psi", "62 psi", "0 Mbps", "8 ppm")
    rows = []
    for variant in range(6):
        for index, (status, reading) in enumerate(zip(statuses, readings)):
            background = "#edf2f7" if variant % 2 else "#111827"
            foreground = "#222b38" if variant % 2 else "#f9fafb"
            if variant == 4:
                foreground = "#9ca3af" if variant % 2 == 0 else "#8b95a3"
            image = Image.new("RGB", (900, 500), background)
            draw = ImageDraw.Draw(image)
            heading = ("PUMP 2", "PUMP 2", "NETWORK CORE", "SERVER ROOM 4")[index]
            if variant in (0, 2, 4):
                draw.text((35, 30), heading, font=font(30), fill=foreground)
                draw.rectangle((30, 110, 870, 350), outline=foreground, width=2)
                draw.text((55, 145), status, font=font(52 if variant != 4 else 26), fill=foreground)
                draw.text((55, 260), reading, font=font(38 if variant != 4 else 18), fill=foreground)
            else:
                draw.text((470, 40), heading, font=font(28), fill=foreground)
                draw.rectangle((25, 40, 435, 455), outline=foreground, width=2)
                draw.text((55, 150), status, font=font(31 if variant != 5 else 19), fill=foreground)
                draw.text((55, 230), reading, font=font(30 if variant != 5 else 16), fill=foreground)
            if variant in (2, 3, 5):
                draw.text((60, 410), "ALERTS  |  SERVICE STATUS", font=font(18), fill=foreground)
            filename = f"dashboard_{variant}_{index}.png"
            image.save(ROOT / filename)
            rows.append({"image": filename, "variant": variant, "status": status, "reading": reading,
                         "ground_truth_origin": "rendered synthetic text"})
    (ROOT / "manifest.jsonl").write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
    print(f"Generated {len(rows)} dashboards in {ROOT}")


if __name__ == "__main__":
    main()
