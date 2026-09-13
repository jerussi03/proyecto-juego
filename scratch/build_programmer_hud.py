from io import BytesIO
from pathlib import Path
import struct
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SFF_SRC = ROOT / "data" / "fight.sff.bak"
SFF_DST = ROOT / "data" / "fight.sff"
PREVIEW_DIR = ROOT / "scratch" / "hud_preview"

def png_to_payload(img_path):
    im = Image.open(img_path).convert("RGBA")
    buf = BytesIO()
    im.save(buf, format="PNG", optimize=True)
    payload = b"\0\0\0\0" + buf.getvalue()
    return im.width, im.height, payload

def make_transparent_payload(w, h):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    buf = BytesIO()
    im.save(buf, format="PNG", optimize=True)
    payload = b"\0\0\0\0" + buf.getvalue()
    return w, h, payload

def build():
    with open(SFF_SRC, "rb") as f:
        raw = f.read()

    hdr = raw[:512]
    table_off = struct.unpack("<I", hdr[36:40])[0]
    num_sprites = struct.unpack("<I", hdr[40:44])[0]
    ldata_off = struct.unpack("<I", hdr[52:56])[0]

    # Load existing sprites dictionary keyed by (grp, num)
    sprite_list = []
    sprite_dict = {}

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
        sprite_list.append(item)

    print(f"Loaded {len(sprite_list)} sprites from original fight.sff")

    # Define our custom sprites to inject or override
    custom_sprites = {}

    def set_sprite(grp, num, img_name, ax, ay):
        path = PREVIEW_DIR / img_name
        w, h, payload = png_to_payload(path)
        custom_sprites[(grp, num)] = {
            "grp": grp, "num": num, "w": w, "h": h, "ax": ax, "ay": ay,
            "link": 0, "fmt": 12, "depth": 32, "payload": payload,
            "pal_idx": 0, "flags": 0
        }

    def set_empty_sprite(grp, num, w, h):
        w, h, payload = make_transparent_payload(w, h)
        custom_sprites[(grp, num)] = {
            "grp": grp, "num": num, "w": w, "h": h, "ax": 0, "ay": 0,
            "link": 0, "fmt": 12, "depth": 32, "payload": payload,
            "pal_idx": 0, "flags": 0
        }

    # 1. Consoles (530x88)
    set_sprite(10, 0, "bg_p1.png", ax=530, ay=0)
    set_sprite(10, 1, "bg_p2.png", ax=0, ay=0)
    set_empty_sprite(11, 0, 530, 88)
    set_empty_sprite(11, 1, 530, 88)

    # 2. Lifebar fill P1 (axis at right, 380x20)
    set_sprite(12, 0, "life_mid.png", ax=380, ay=0)
    set_sprite(13, 0, "life_100.png", ax=380, ay=0)
    set_sprite(13, 1, "life_50.png", ax=380, ay=0)
    set_sprite(13, 2, "life_25.png", ax=380, ay=0)
    set_sprite(13, 3, "life_25.png", ax=380, ay=0)

    # 3. Lifebar fill P2 (axis at left, 380x20)
    set_sprite(12, 1, "life_mid.png", ax=0, ay=0)
    set_sprite(13, 10, "life_100.png", ax=0, ay=0)
    set_sprite(13, 11, "life_50.png", ax=0, ay=0)
    set_sprite(13, 12, "life_25.png", ax=0, ay=0)
    set_sprite(13, 13, "life_25.png", ax=0, ay=0)

    # 4. Powerbar "STACK"
    set_sprite(40, 0, "power_bg.png", ax=220, ay=0)
    set_sprite(40, 1, "power_bg.png", ax=0, ay=0)
    set_empty_sprite(41, 0, 220, 28)
    set_empty_sprite(41, 1, 220, 28)
    set_sprite(43, 0, "power_fill.png", ax=158, ay=0)
    set_sprite(43, 1, "power_fill.png", ax=0, ay=0)

    # 5. Face Portrait (80x88)
    set_sprite(50, 0, "face_bg.png", ax=0, ay=0)
    set_sprite(50, 1, "face_bg.png", ax=0, ay=0)
    set_sprite(51, 0, "face_frame_p1.png", ax=0, ay=0)
    set_sprite(51, 1, "face_frame_p2.png", ax=0, ay=0)

    # 6. Win Stars
    set_sprite(70, 0, "win_star_off.png", ax=0, ay=0)
    set_sprite(71, 0, "win_star_on.png", ax=0, ay=0)
    set_sprite(72, 0, "win_star_on.png", ax=0, ay=0)

    # Merge custom sprites into dictionary
    for k, v in custom_sprites.items():
        sprite_dict[k] = v

    # Sort sprites by (grp, num) for a clean, deterministic table
    sorted_sprites = sorted(sprite_dict.values(), key=lambda s: (s["grp"], s["num"]))
    print(f"Total sprites after injection: {len(sorted_sprites)}")

    # Rebuild SFF binary
    new_num_sprites = len(sorted_sprites)
    new_table_off = 512
    new_pal_off = 512
    new_ldata_off = new_table_off + new_num_sprites * 28
    new_ldata_len = sum(len(s["payload"]) for s in sorted_sprites)
    new_tdata_off = new_ldata_off + new_ldata_len

    out_hdr = bytearray(raw[:512])
    struct.pack_into("<I", out_hdr, 36, new_table_off)
    struct.pack_into("<I", out_hdr, 40, new_num_sprites)
    struct.pack_into("<I", out_hdr, 44, new_pal_off)
    struct.pack_into("<I", out_hdr, 48, 0)
    struct.pack_into("<I", out_hdr, 52, new_ldata_off)
    struct.pack_into("<I", out_hdr, 56, new_ldata_len)
    struct.pack_into("<I", out_hdr, 60, new_tdata_off)
    struct.pack_into("<I", out_hdr, 64, 0)

    out = bytearray(out_hdr)
    cur_off = 0
    for s in sorted_sprites:
        sz = len(s["payload"])
        rec = struct.pack(
            "<HHHHhhHBBIIHH",
            s["grp"], s["num"], s["w"], s["h"], s["ax"], s["ay"],
            s["link"], s["fmt"], s["depth"], cur_off, sz, s["pal_idx"], s["flags"]
        )
        out.extend(rec)
        cur_off += sz

    for s in sorted_sprites:
        out.extend(s["payload"])

    with open(SFF_DST, "wb") as f:
        f.write(out)

    print(f"Successfully wrote new {SFF_DST} ({len(out)} bytes)")

if __name__ == "__main__":
    build()
