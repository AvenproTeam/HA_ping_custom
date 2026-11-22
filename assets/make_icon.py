"""Generate GC-6612Pro Ping brand icons (light and dark variants).

Usage: python assets/make_icon.py custom_components/gc6612pro_ping/brand
Requires: pip install resvg-py pillow
"""

import io
import sys
from pathlib import Path

import resvg_py
from PIL import Image

PALETTES = {
    "light": {
        "top": "#4f5f76",
        "front": "#33404f",
        "side": "#27313d",
        "edge": "#6a7b93",
    },
    "dark": {
        "top": "#8a9ab0",
        "front": "#66768c",
        "side": "#55647a",
        "edge": "#a9b7c9",
    },
}


def svg(p: dict) -> str:
    ports = []
    for i in range(12):
        x = 54 + i * 24
        ports.append(
            f'<rect x="{x}" y="336" width="22" height="64" rx="3" fill="#2eb35a"/>'
            f'<rect x="{x + 5}" y="345" width="12" height="16" rx="2" fill="#16602f"/>'
            f'<circle cx="{x + 11}" cy="381" r="6" fill="#7fe0a0"/>'
        )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <!-- chassis -->
  <polygon points="32,300 404,300 468,220 96,220" fill="{p["top"]}"/>
  <polygon points="404,300 468,220 468,344 404,424" fill="{p["side"]}"/>
  <rect x="32" y="300" width="372" height="124" fill="{p["front"]}"/>
  <line x1="32" y1="300" x2="404" y2="300" stroke="{p["edge"]}" stroke-width="4"/>
  <line x1="404" y1="300" x2="468" y2="220" stroke="{p["edge"]}" stroke-width="4"/>
  <!-- terminal blocks -->
  {"".join(ports)}
  <!-- power inlet -->
  <rect x="352" y="336" width="40" height="64" rx="6" fill="#111418"/>
  <rect x="360" y="347" width="6" height="17" rx="2" fill="#9aa4b1"/>
  <rect x="378" y="347" width="6" height="17" rx="2" fill="#9aa4b1"/>
  <rect x="369" y="373" width="6" height="15" rx="2" fill="#9aa4b1"/>
  <!-- ping badge -->
  <circle cx="400" cy="176" r="84" fill="#03a9f4"/>
  <g fill="none" stroke="#ffffff" stroke-width="14" stroke-linecap="round">
    <path d="M370 176 A30 30 0 0 1 400 206"/>
    <path d="M370 154 A52 52 0 0 1 422 206"/>
    <path d="M370 132 A74 74 0 0 1 444 206"/>
  </g>
  <circle cx="370" cy="206" r="11" fill="#ffffff"/>
</svg>"""


def render(svg_text: str, size: int) -> Image.Image:
    png = bytes(resvg_py.svg_to_bytes(svg_string=svg_text, width=size, height=size))
    return Image.open(io.BytesIO(png)).convert("RGBA")


def trimmed_square(img: Image.Image, size: int) -> Image.Image:
    """Crop to content and pad to a centred transparent square."""
    box = img.getbbox()
    content = img.crop(box)
    side = max(content.size)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(content, ((side - content.width) // 2, (side - content.height) // 2))
    return canvas.resize((size, size), Image.LANCZOS)


def main(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for variant, palette in PALETTES.items():
        prefix = "" if variant == "light" else "dark_"
        big = render(svg(palette), 2048)
        (Path(__file__).parent / f"{prefix}icon.svg").write_text(svg(palette))
        trimmed_square(big, 256).save(out_dir / f"{prefix}icon.png", optimize=True)
        trimmed_square(big, 512).save(out_dir / f"{prefix}icon@2x.png", optimize=True)


if __name__ == "__main__":
    main(Path(sys.argv[1]))
