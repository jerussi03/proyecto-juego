from pathlib import Path
import sys
from PIL import Image, ImageDraw, ImageOps

pattern = sys.argv[1] if len(sys.argv) > 1 else "*"
files = sorted(Path("stages/utc-real/source").glob(pattern))
cell_w, cell_h = 320, 210
sheet = Image.new("RGB", (cell_w * 4, cell_h * ((len(files) + 3) // 4)), (20, 25, 28))
draw = ImageDraw.Draw(sheet)
for index, path in enumerate(files):
    x = index % 4 * cell_w
    y = index // 4 * cell_h
    image = Image.open(path).convert("RGB")
    sheet.paste(ImageOps.fit(image, (cell_w, cell_h - 25)), (x, y + 25))
    draw.text((x + 5, y + 5), path.name, fill="white")
suffix = pattern.replace("*", "todos").replace(".", "-")
sheet.save(f"stages/utc-real/contacto-{suffix}.jpg", quality=88)
