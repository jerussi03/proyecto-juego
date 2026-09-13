from io import BytesIO
from pathlib import Path
import shutil
import struct
from PIL import Image, ImageDraw, ImageEnhance, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SFF_SRC = ROOT / "data" / "ikemen1" / "system.sff"
SFF_BAK = ROOT / "data" / "ikemen1" / "system.sff.bak"
BTN_DIR = ROOT / "scratch" / "title_buttons"

def png_to_payload(im):
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    buf = BytesIO()
    im.save(buf, format="PNG", optimize=True)
    payload = b"\0\0\0\0" + buf.getvalue()
    return im.width, im.height, payload

def build():
    with open(SFF_SRC, "rb") as f:
        raw = f.read()

    hdr = raw[:512]
    table_off = struct.unpack("<I", hdr[36:40])[0]
    num_sprites = struct.unpack("<I", hdr[40:44])[0]
    pal_table_off = struct.unpack("<I", hdr[44:48])[0]
    num_pals = struct.unpack("<I", hdr[48:52])[0]
    ldata_off = struct.unpack("<I", hdr[52:56])[0]

    # Preserve palette block between 512 and table_off
    pal_block = raw[512:table_off]

    sprite_dict = {}
    sprite_order = []

    for i in range(num_sprites):
        rec = raw[table_off + i*28 : table_off + (i+1)*28]
        grp, num, w, h, ax, ay, link, fmt, depth, off, sz, pal_idx, flags = struct.unpack("<HHHHhhHBBIIHH", rec)
        payload = raw[ldata_off + off : ldata_off + off + sz]
        item = {
            "grp": grp, "num": num, "w": w, "h": h, "ax": ax, "ay": ay,
            "link": link, "fmt": fmt, "depth": depth, "payload": payload,
            "pal_idx": pal_idx, "flags": flags
        }
        sprite_dict[(grp, num)] = item
        sprite_order.append((grp, num))

    print(f"Loaded {len(sprite_dict)} sprites and {num_pals} palettes from original system.sff")

    # Custom sprites
    def add_custom(grp, num, img_obj, ax=0, ay=0):
        w, h, payload = png_to_payload(img_obj)
        item = {
            "grp": grp, "num": num, "w": w, "h": h, "ax": ax, "ay": ay,
            "link": 0, "fmt": 12, "depth": 32, "payload": payload,
            "pal_idx": 0, "flags": 0
        }
        sprite_dict[(grp, num)] = item
        if (grp, num) not in sprite_order:
            sprite_order.append((grp, num))

    # 1. Base Title Background (1280x720)
    bg_im = Image.open(BTN_DIR / "user_new_bg_1280x720.png")
    add_custom(100, 0, bg_im, ax=0, ay=0)

    # 2. Button sprites (kept for compatibility with the motif).
    names = ['historia', 'practica', 'versus', 'opciones', 'salir']
    TARGET_W = 320
    TARGET_H = 70

    def fit_btn(im):
        if im.mode != "RGBA":
            im = im.convert("RGBA")
        scale = min((TARGET_W - 6) / im.width, (TARGET_H - 6) / im.height)
        nw = int(round(im.width * scale))
        nh = int(round(im.height * scale))
        resized = im.resize((nw, nh), Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
        ox = (TARGET_W - nw) // 2
        oy = (TARGET_H - nh) // 2
        canvas.paste(resized, (ox, oy), resized)
        return canvas

    for idx, name in enumerate(names, start=1):
        bu = Image.open(BTN_DIR / f"{name}_unsel_new.png")
        bs = Image.open(BTN_DIR / f"{name}_sel_new.png")
        bu_sc = fit_btn(bu)
        bs_sc = fit_btn(bs)

        add_custom(101, idx, bu_sc, ax=0, ay=0)  # Unselected
        add_custom(102, idx, bs_sc, ax=0, ay=0)  # Selected

    # 3. Complete title-screen compositions. Each image contains the fixed
    # monitor frame and all five buttons, with exactly one button highlighted.
    # Drawing one full image avoids the engine's generic menu layout shifting
    # or overlapping parts of the custom artwork.

    # 3. Complete title-screen compositions. Each image contains the fixed
    # monitor frame and all five buttons, with exactly one button highlighted.
    # The left panel uses the sci-fi chamber frame as background for mode previews.
    FRAME_W, FRAME_H = 544, 279
    FRAME_X, FRAME_Y = 196, 120

    frame_path = ROOT / "data" / "ikemen1" / "mode_frame_bg.png"
    historia_preview_path = ROOT / "data" / "ikemen1" / "historia_preview.jpg"
    practica_preview_path = ROOT / "data" / "ikemen1" / "practica_preview.png"
    versus_preview_path = ROOT / "data" / "ikemen1" / "versus_preview.png"

    frame_raw = None
    frame_overlay = None
    if frame_path.exists():
        frame_raw = Image.open(frame_path).crop((7, 37, 662, 373)).convert("RGBA")
        import numpy as np
        arr = np.array(frame_raw)
        arr[26:310, 26:629, 3] = 0
        frame_overlay = Image.fromarray(arr)

    for idx, name in enumerate(names, start=1):
        screen = Image.open(BTN_DIR / f"menu_option_{idx}_{name}.png").convert("RGBA")

        if frame_raw is not None:
            # Cleanly cover the old window area with the matrix pattern
            clean_matrix = screen.crop((200, 340, 740, 550))
            screen.paste(clean_matrix.crop((0, 0, 540, 210)), (200, 118))

            if idx == 1 and historia_preview_path.exists():
                preview = Image.open(historia_preview_path).convert("RGBA")
                p_cover = preview.resize((604, 337), Image.Resampling.LANCZOS)
                frame_mode = Image.new("RGBA", frame_raw.size, (0, 0, 0, 0))
                frame_mode.alpha_composite(p_cover, (26, 26))
                frame_mode.alpha_composite(frame_overlay, (0, 0))
            elif idx == 2 and practica_preview_path.exists():
                preview = Image.open(practica_preview_path).convert("RGBA")
                # Crop inner art from border
                inner_art = preview.crop((12, 10, 785, 385))
                p_cover = inner_art.resize((604, 290), Image.Resampling.LANCZOS)
                frame_mode = Image.new("RGBA", frame_raw.size, (0, 0, 0, 0))
                frame_mode.alpha_composite(p_cover, (26, 24))
                frame_mode.alpha_composite(frame_overlay, (0, 0))
            elif idx == 3 and versus_preview_path.exists():
                preview = Image.open(versus_preview_path).convert("RGBA")
                p_cover = preview.resize((604, 296), Image.Resampling.LANCZOS)
                frame_mode = Image.new("RGBA", frame_raw.size, (0, 0, 0, 0))
                frame_mode.alpha_composite(p_cover, (26, 22))
                frame_mode.alpha_composite(frame_overlay, (0, 0))
            else:
                frame_mode = frame_raw.copy()

            scaled = frame_mode.resize((FRAME_W, FRAME_H), Image.Resampling.LANCZOS)
            screen.alpha_composite(scaled, (FRAME_X, FRAME_Y))

        add_custom(103, idx, screen, ax=0, ay=0)

    # Use the supplied VS submenu artwork without generating a replacement.
    add_custom(104, 0, Image.open(BTN_DIR / "versus_submenu.png"), ax=0, ay=0)

    # Cut the supplied sheet into aligned active / inactive buttons.
    sheet = Image.open(BTN_DIR / "versus_buttons_sheet.png").convert("RGBA")
    normal = [sheet.crop((20, 43, 252, 110)), sheet.crop((261, 43, 462, 110))]
    active = [sheet.crop((19, 120, 253, 206)), sheet.crop((260, 120, 462, 206)), sheet.crop((469, 244, 657, 321))]
    # The sheet only includes the green Regresar: derive its inactive state
    # by removing saturation, keeping the supplied lettering and arrow.
    normal.append(ImageEnhance.Color(active[2]).enhance(0))
    positions = [(618, 196), (618, 262), (618, 328)]
    for selected in range(3):
        screen = Image.open(BTN_DIR / "versus_submenu.png").convert("RGBA")
        draw = ImageDraw.Draw(screen)
        draw.rectangle((612, 190, 866, 393), fill=(10, 26, 33, 255))
        for row in range(3):
            button = (active if row == selected else normal)[row]
            button = button.resize((244, 61), Image.Resampling.LANCZOS)
            screen.alpha_composite(button, positions[row])
        screen.save(BTN_DIR / f"versus_state_{selected + 1}.png")
        add_custom(104, selected + 1, screen, ax=0, ay=0)

    # Reconstruct SFF v2
    ldata = bytearray()
    new_records = []

    for key in sprite_order:
        item = sprite_dict[key]
        off = len(ldata)
        payload = item["payload"]
        ldata.extend(payload)
        sz = len(payload)

        rec = struct.pack(
            "<HHHHhhHBBIIHH",
            item["grp"], item["num"], item["w"], item["h"],
            item["ax"], item["ay"], item["link"], item["fmt"],
            item["depth"], off, sz, item["pal_idx"], item["flags"]
        )
        new_records.append(rec)

    new_num_sprites = len(new_records)
    new_table_off = 512 + len(pal_block)
    new_table_bytes = b"".join(new_records)
    new_ldata_off = new_table_off + len(new_table_bytes)

    # Pad ldata_off to 16-byte alignment
    pad = (16 - (new_ldata_off % 16)) % 16
    new_table_bytes += b"\0" * pad
    new_ldata_off += pad

    # Update header
    new_hdr = bytearray(hdr)
    new_hdr[36:40] = struct.pack("<I", new_table_off)
    new_hdr[40:44] = struct.pack("<I", new_num_sprites)
    new_hdr[44:48] = struct.pack("<I", pal_table_off)
    new_hdr[48:52] = struct.pack("<I", num_pals)
    new_hdr[52:56] = struct.pack("<I", new_ldata_off)
    new_hdr[56:60] = struct.pack("<I", len(ldata))

    with open(SFF_SRC, "wb") as f:
        f.write(new_hdr)
        f.write(pal_block)
        f.write(new_table_bytes)
        f.write(ldata)

    print(f"Successfully wrote {new_num_sprites} sprites and {num_pals} palettes to {SFF_SRC} ({SFF_SRC.stat().st_size} bytes)")

if __name__ == "__main__":
    build()
