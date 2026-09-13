"""Prepara escenarios de Ikemen GO a partir de fotografias oficiales de UTC.

No genera ni rellena imagenes: cada salida es un recorte y reescalado de una
fotografia descargada desde el sitio de la Universidad Tecnologica de la Costa.
"""

from io import BytesIO
from pathlib import Path
import struct

from PIL import Image, ImageEnhance, ImageOps


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "stages" / "utc-real" / "source"
OUT = ROOT / "stages" / "utc-real"

STAGES = [
    ("utc_pasillo", "UTC: Pasillo de Rectoría", "Pasillo de Rectoría", "rectoria-5.jpg", (0.29, 0.24, 0.75, 0.70), 0.96),
    ("utc_vinculacion", "UTC: Vinculación", "Vinculación Empresarial", "vinculacion.jpg", (0.15, 0.30, 0.85, 1.0), 0.98),
]


def png_payload(image: Image.Image) -> bytes:
    buffer = BytesIO()
    image.convert("RGBA").save(buffer, format="PNG", optimize=True)
    return b"\0\0\0\0" + buffer.getvalue()


def write_sff(path: Path, background: Image.Image, preview: Image.Image) -> None:
    """Fondo de 640x480 unidades de mundo con suelo anclado al eje Y."""
    sprites = [
        # At scale .375 the photo spans x=-240..240, with ground at y=324.
        (0, 0, background.convert("RGBA"), 640, 864),
        (9000, 1, preview.convert("RGBA"), 0, 0),
    ]
    local_data = bytearray()
    records = []
    for group, number, image, axis_x, axis_y in sprites:
        payload = png_payload(image)
        offset = len(local_data)
        local_data.extend(payload)
        records.append(struct.pack(
            "<HHHHhhHBBIIHH", group, number, image.width, image.height,
            axis_x, axis_y, 0, 12, 32, offset, len(payload), 0, 0,
        ))

    table_offset = 512
    data_offset = table_offset + len(records) * 28
    data_offset += (16 - data_offset % 16) % 16
    header = bytearray(512)
    header[:12] = b"ElecbyteSpr\0"
    header[12:16] = bytes((0, 1, 0, 2))
    header[36:40] = struct.pack("<I", table_offset)
    header[40:44] = struct.pack("<I", len(records))
    header[52:56] = struct.pack("<I", data_offset)
    header[56:60] = struct.pack("<I", len(local_data))
    with path.open("wb") as file:
        file.write(header)
        file.write(b"".join(records))
        file.write(b"\0" * (data_offset - table_offset - len(records) * 28))
        file.write(local_data)


def stage_def(internal: str, name: str, display: str) -> str:
    return f'''[Info]
name = "{name}"
displayname = "{display}"
versiondate = 09,13,2026
mugenversion = 1.1
author = "Universidad Tecnologica de la Costa / adaptacion"

[Camera]
startx = 0
starty = 0
boundleft = {-71 if internal == 'utc_pasillo' else -58}
boundright = {71 if internal == 'utc_pasillo' else 58}
boundhigh = -22
boundlow = 0
verticalfollow = .2
floortension = 60
tension = 65
overdrawhigh = 0
overdrawlow = 0
cuthigh = 0
cutlow = 0
; Reduce photo world scale and compensate camera zoom: fighters become
; one third larger relative to the architecture, keeping the same framing.
startzoom = {0.8 / 0.75 if internal == 'utc_pasillo' else 1.05:.4f}
zoomout = {0.8 / 0.75 if internal == 'utc_pasillo' else 1.05:.4f}
zoomin = {0.9 / 0.75 if internal == 'utc_pasillo' else 1.10:.4f}

[PlayerInfo]
p1startx = -65
p1starty = 0
p1facing = 1
p2startx = 65
p2starty = 0
p2facing = -1
p3startx = -95
p3starty = 0
p3facing = 1
p4startx = 95
p4starty = 0
p4facing = -1
leftbound = {-210 if internal == 'utc_pasillo' else -195}
rightbound = {210 if internal == 'utc_pasillo' else 195}

[Bound]
screenleft = 20
screenright = 20

[StageInfo]
zoffset = {216 if internal == 'utc_pasillo' else 224}
autoturn = 1
resetBG = 1
localcoord = 320, 240
xscale = 1
yscale = 1
portraitscale = 1

[Shadow]
intensity = 80
color = 0,0,0
yscale = .25
fade.range = 0,0

[Reflection]
intensity = 0

[Music]
bgmusic =
bgmvolume = 100

[BGdef]
spr = utc-real/{internal}.sff
debugbg = 0

[Begin Action 9000]
9000,1,0,0,-1

[BG 0]
type = normal
spriteno = 0,0
layerno = 0
start = 0,{216 if internal == 'utc_pasillo' else 224}
delta = 1,1
zoomdelta = 1,1
mask = 0
scalestart = {'.375, .375' if internal == 'utc_pasillo' else '.34, .34'}
'''


def make_background(path: Path, crop: tuple[float, float, float, float], brightness: float) -> Image.Image:
    image = Image.open(path).convert("RGB")
    w, h = image.size
    image = image.crop((round(crop[0]*w), round(crop[1]*h), round(crop[2]*w), round(crop[3]*h)))
    image = image.resize((1280, 960), Image.Resampling.LANCZOS)
    image = ImageEnhance.Brightness(image).enhance(brightness)
    return ImageEnhance.Contrast(image).enhance(1.03)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    previews = []
    for internal, name, display, source_name, centering, brightness in STAGES:
        background = make_background(SOURCE / source_name, centering, brightness)
        preview = ImageOps.fit(background, (240, 100), Image.Resampling.LANCZOS)
        background.save(OUT / f"{internal}.png", optimize=True)
        preview.save(OUT / f"{internal}-preview.png", optimize=True)
        write_sff(OUT / f"{internal}.sff", background, preview)
        (ROOT / "stages" / f"{internal}.def").write_text(stage_def(internal, name, display), encoding="utf-8")
        previews.append((display, preview))
        print(f"{internal}: {source_name}")

    sheet = Image.new("RGB", (480, 130), (20, 24, 28))
    from PIL import ImageDraw
    draw = ImageDraw.Draw(sheet)
    for index, (name, preview) in enumerate(previews):
        x, y = (index % 4) * 240, (index // 4) * 260
        sheet.paste(preview, (x, y + 25))
        draw.text((x + 7, y + 6), name, fill="white")
    sheet.save(OUT / "contacto-escenarios.jpg", quality=90)


if __name__ == "__main__":
    main()
