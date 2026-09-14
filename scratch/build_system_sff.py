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

def safe_save(img, path, retries=10, delay=0.2):
    import time
    for attempt in range(retries):
        try:
            img.save(path)
            return
        except OSError:
            if attempt == retries - 1:
                raise
            time.sleep(delay)

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

    # 1. Base Title Background (1280x720) - Main Menu only
    bg_im = Image.open(BTN_DIR / "user_new_bg_1280x720.png")
    add_custom(100, 0, bg_im, ax=0, ay=0)

    # 1b. General Background (blurred university campus for all other screens)
    gen_bg_path = ROOT / "data" / "ikemen1" / "general_bg_university.png"
    if gen_bg_path.exists():
        gen_bg = Image.open(gen_bg_path).convert("RGBA")
        add_custom(204, 0, gen_bg, ax=0, ay=0)
        add_custom(205, 0, gen_bg, ax=0, ay=0)

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
            elif idx in (4, 5):
                # Reuse supplied menu art: tools for Options and the exit door.
                panel = Image.new('RGBA', (604, 296), (12, 25, 32, 255))
                pd = ImageDraw.Draw(panel)
                for y in range(16, 296, 24):
                    pd.line((18, y, 586, y), fill=(20, 49, 55, 255), width=1)
                button = Image.open(BTN_DIR / f'{name}_sel_new.png').convert('RGBA')
                icon = button.crop((int(button.width * .78), 0, button.width, button.height))
                panel.alpha_composite(ImageOps.contain(icon, (150, 140), Image.Resampling.LANCZOS), (227, 28))
                button = ImageOps.contain(button, (460, 85), Image.Resampling.LANCZOS)
                panel.alpha_composite(button, ((604-button.width)//2, 188))
                frame_mode = Image.new('RGBA', frame_raw.size, (0, 0, 0, 0))
                frame_mode.alpha_composite(panel, (26, 22))
                frame_mode.alpha_composite(frame_overlay, (0, 0))
            else:
                frame_mode = frame_raw.copy()

            scaled = frame_mode.resize((FRAME_W, FRAME_H), Image.Resampling.LANCZOS)
            screen.alpha_composite(scaled, (FRAME_X, FRAME_Y))

        add_custom(103, idx, screen, ax=0, ay=0)

    # Cut the supplied sheet into aligned active / inactive buttons.
    sheet = Image.open(BTN_DIR / "versus_buttons_sheet.png").convert("RGBA")
    normal = [sheet.crop((20, 43, 252, 110)), sheet.crop((261, 43, 462, 110))]
    active = [sheet.crop((19, 120, 253, 206)), sheet.crop((260, 120, 462, 206)), sheet.crop((469, 244, 657, 321))]
    # The sheet only includes the green Regresar: derive its inactive state
    # by removing saturation, keeping the supplied lettering and arrow.
    normal.append(ImageEnhance.Color(active[2]).enhance(0))
    positions_1280 = [(772, 252), (772, 337), (772, 422)]
    btn_size_1280 = (305, 78)

    for selected in range(3):
        screen = Image.open(BTN_DIR / "user_new_bg_1280x720.png").convert("RGBA")
        if frame_raw is not None:
            clean_matrix = screen.crop((200, 340, 740, 550))
            screen.paste(clean_matrix.crop((0, 0, 540, 210)), (200, 118))

        # Keep the same VS illustration and monitor frame coordinates when entering its submenu.
        # Follow the diagonal divider: CPU is on the left, two players on the right.
        if frame_raw is not None and versus_preview_path.exists():
            preview = Image.open(versus_preview_path).convert("RGBA")
            gray = ImageOps.grayscale(preview).convert("RGBA")
            mask = Image.new("L", preview.size, 0)
            width, height = preview.size
            ImageDraw.Draw(mask).polygon(
                [(0, 0), (int(width * .59), 0), (int(width * .435), height), (0, height)],
                fill=255,
            )
            if selected == 0:
                preview = Image.composite(preview, gray, mask)
            elif selected == 1:
                preview = Image.composite(gray, preview, mask)
            else:
                preview = gray
            frame_mode = Image.new("RGBA", frame_raw.size, (0, 0, 0, 0))
            frame_mode.alpha_composite(preview.resize((604, 296), Image.Resampling.LANCZOS), (26, 22))
            frame_mode.alpha_composite(frame_overlay, (0, 0))
            scaled = frame_mode.resize((FRAME_W, FRAME_H), Image.Resampling.LANCZOS)
            screen.alpha_composite(scaled, (FRAME_X, FRAME_Y))

        draw = ImageDraw.Draw(screen)
        draw.rectangle((765, 245, 1083, 506), fill=(10, 26, 33, 255))
        for row in range(3):
            button = (active if row == selected else normal)[row]
            button = button.resize(btn_size_1280, Image.Resampling.LANCZOS)
            screen.alpha_composite(button, positions_1280[row])
        safe_save(screen, BTN_DIR / f"versus_state_{selected + 1}.png")
        if selected == 0:
            safe_save(screen, BTN_DIR / "versus_submenu.png")
            add_custom(104, 0, screen, ax=0, ay=0)
        add_custom(104, selected + 1, screen, ax=0, ay=0)

    # 4. Character Select UI Sprites
    sheet_src_path = ROOT / "scratch" / "select_sheet_source.png"
    if sheet_src_path.exists():
        import math
        src = Image.open(sheet_src_path).convert("RGBA")

        def center_pad(im, target_w=126, target_h=86):
            canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
            ox = (target_w - im.width) // 2
            oy = (target_h - im.height) // 2
            canvas.alpha_composite(im, (ox, oy))
            return canvas

        # 4.1 Title Banner: 'LUCHADORES ELEGIBLES' -> (105, 0)
        banner = src.crop((172, 11, 493, 47))
        banner_1280 = banner.resize((int(banner.width * 1.5), int(banner.height * 1.5)), Image.Resampling.NEAREST)
        add_custom(105, 0, banner_1280, ax=0, ay=0)

        # 4.2 Outer Decorative Frame 1280x720 -> (106, 0)
        tl = src.crop((7, 6, 48, 48)).resize((70, 70), Image.Resampling.NEAREST)
        tr = src.crop((619, 6, 660, 48)).resize((70, 70), Image.Resampling.NEAREST)
        bl = src.crop((7, 330, 48, 373)).resize((70, 70), Image.Resampling.NEAREST)
        br = src.crop((619, 330, 660, 373)).resize((70, 70), Image.Resampling.NEAREST)
        top_rail = src.crop((65, 16, 155, 26)).resize((1280 - 140, 18), Image.Resampling.NEAREST)
        bot_rail = src.crop((55, 354, 125, 364)).resize((1280 - 140, 18), Image.Resampling.NEAREST)
        left_rail = src.crop((9, 50, 20, 320)).resize((18, 720 - 140), Image.Resampling.NEAREST)
        right_rail = src.crop((647, 50, 658, 320)).resize((18, 720 - 140), Image.Resampling.NEAREST)

        frame_1280 = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
        frame_1280.alpha_composite(tl, (0, 0))
        frame_1280.alpha_composite(tr, (1280 - 70, 0))
        frame_1280.alpha_composite(bl, (0, 720 - 70))
        frame_1280.alpha_composite(br, (1280 - 70, 720 - 70))
        frame_1280.alpha_composite(top_rail, (70, 14))
        frame_1280.alpha_composite(bot_rail, (70, 720 - 32))
        frame_1280.alpha_composite(left_rail, (14, 70))
        frame_1280.alpha_composite(right_rail, (1280 - 32, 70))
        add_custom(106, 0, frame_1280, ax=0, ay=0)

        # 4.3 Standard Cell Background -> (150, 0)
        cell_norm = src.crop((24, 55, 144, 139))
        # Keep the empty original tab; the game has no character-level value.
        c_norm = center_pad(cell_norm, 126, 86)
        ImageDraw.Draw(c_norm).rectangle((17, 24, 108, 70), fill=(15, 22, 29, 255))
        add_custom(150, 0, c_norm, ax=0, ay=0)

        # 4.4 Random Select Icon -> (151, 0) & Large Portrait -> (152, 0)
        random_src_path = ROOT / "data" / "ikemen1" / "random_character_source.png"
        if not random_src_path.exists():
            random_src_path = ROOT / "scratch" / "random_character_source.png"
        ri = Image.open(random_src_path).convert("RGBA")
        ri = ri.crop(ri.getbbox())
        # Icon for the cell: fit cleanly within (30, 42) inside (44, 44) canvas
        # At portrait.offset (41, 25), it occupies Y=[25, 69], strictly inside the cell's [24, 70] window.
        ri_icon = ImageOps.contain(ri, (30, 42), Image.Resampling.LANCZOS)
        c_ri = Image.new("RGBA", (44, 44), (0, 0, 0, 0))
        c_ri.alpha_composite(ri_icon, ((44 - ri_icon.width) // 2, (44 - ri_icon.height) // 2))
        add_custom(151, 0, c_ri, ax=0, ay=0)

        # Big profile portrait for background when hovering on Random: (152, 0)
        ri_big = ImageOps.contain(ri, (280, 434), Image.Resampling.LANCZOS)
        c_big = Image.new("RGBA", (280, 434), (0, 0, 0, 0))
        c_big.alpha_composite(ri_big, ((280 - ri_big.width) // 2, (434 - ri_big.height) // 2))
        add_custom(152, 0, c_big, ax=0, ay=0)

        # 4.5 P1 Active Cursor Gold pulse -> (160, 0..7)
        cell_gold = src.crop((523, 57, 645, 142))
        c_gold = center_pad(cell_gold, 126, 86)
        ImageDraw.Draw(c_gold).rectangle((17, 24, 108, 70), fill=(0, 0, 0, 0))
        for i in range(8):
            factor = 1.0 + 0.1 * math.sin(i * math.pi / 4)
            c_gold_pulse = ImageEnhance.Brightness(c_gold).enhance(factor)
            add_custom(160, i, c_gold_pulse, ax=0, ay=0)

        # 4.6 P1 Done Cursor Bronze -> (161, 0)
        cell_bronze = src.crop((271, 144, 397, 226))
        barr = np.array(cell_bronze)
        barr[16:74, 12:114] = [0, 0, 0, 0]
        c_bronze = center_pad(Image.fromarray(barr), 126, 86)
        add_custom(161, 0, c_bronze, ax=0, ay=0)

        # 4.7 P2 Active Cursor Cyan pulse -> (170, 0..7)
        arr_gold = np.array(c_gold, dtype=np.float32)
        r, g, b, a = arr_gold[:,:,0], arr_gold[:,:,1], arr_gold[:,:,2], arr_gold[:,:,3]
        cyan_arr = np.zeros_like(arr_gold)
        cyan_arr[:,:,0] = np.clip(b * 0.6 + 10, 0, 255)
        cyan_arr[:,:,1] = np.clip(g * 0.95 + 10, 0, 255)
        cyan_arr[:,:,2] = np.clip(r * 1.1 + 20, 0, 255)
        cyan_arr[:,:,3] = a
        c_cyan = Image.fromarray(cyan_arr.astype(np.uint8))
        for i in range(8):
            factor = 1.0 + 0.1 * math.sin(i * math.pi / 4)
            c_cyan_pulse = ImageEnhance.Brightness(c_cyan).enhance(factor)
            add_custom(170, i, c_cyan_pulse, ax=0, ay=0)

        # 4.8 P2 Done Cursor Bronze -> (171, 0)
        add_custom(171, 0, c_bronze, ax=0, ay=0)

        # 4.9 Stage Monitor Console -> (112, 0)
        mon = src.crop((264, 232, 405, 374))
        ImageDraw.Draw(mon).rectangle((24, 23, 112, 80), fill=(12, 20, 26, 255))
        mon_standby = mon.resize((282, 284), Image.Resampling.NEAREST)
        add_custom(112, 0, mon_standby, ax=0, ay=0)

        # 4.10 Random Stage Map -> (111, 0)
        map_crop = src.crop((295, 258, 374, 307)).resize((176, 114), Image.Resampling.NEAREST)
        add_custom(111, 0, map_crop, ax=0, ay=0)

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
