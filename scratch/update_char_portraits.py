import os
from io import BytesIO
from pathlib import Path
import struct
from PIL import Image

def png_to_payload(img_path):
    im = Image.open(img_path).convert("RGBA")
    buf = BytesIO()
    im.save(buf, format="PNG", optimize=True)
    payload = b"\0\0\0\0" + buf.getvalue()
    return im.width, im.height, payload

def update_sff_portraits(sff_path, portrait_updates):
    sff_path = Path(sff_path)
    bak_path = sff_path.with_suffix(".sff.bak")

    # Read from bak if exists to always build from clean base
    src_path = bak_path if bak_path.exists() else sff_path
    with open(src_path, "rb") as f:
        raw = f.read()

    hdr = raw[:512]
    table_off = struct.unpack("<I", hdr[36:40])[0]
    num_sprites = struct.unpack("<I", hdr[40:44])[0]
    ldata_off = struct.unpack("<I", hdr[52:56])[0]

    sprites = []
    found_keys = set()
    for i in range(num_sprites):
        rec = raw[table_off + i*28 : table_off + (i+1)*28]
        grp, num, w, h, ax, ay, link, fmt, depth, off, sz, pal_idx, flags = struct.unpack("<HHHHhhHBBIIHH", rec)
        payload = raw[ldata_off + off : ldata_off + off + sz]
        
        if (grp, num) in portrait_updates:
            img_path, new_ax, new_ay = portrait_updates[(grp, num)]
            new_w, new_h, new_payload = png_to_payload(img_path)
            sprites.append({
                "grp": grp, "num": num, "w": new_w, "h": new_h, "ax": new_ax, "ay": new_ay,
                "link": 0, "fmt": 12, "depth": 32, "payload": new_payload,
                "pal_idx": 0, "flags": 0
            })
            found_keys.add((grp, num))
            print(f"[{sff_path.name}] Updated sprite ({grp}, {num}) -> {new_w}x{new_h} axis=({new_ax},{new_ay})")
        else:
            sprites.append({
                "grp": grp, "num": num, "w": w, "h": h, "ax": ax, "ay": ay,
                "link": link, "fmt": fmt, "depth": depth, "payload": payload,
                "pal_idx": pal_idx, "flags": flags
            })

    for key, (img_path, new_ax, new_ay) in portrait_updates.items():
        if key not in found_keys:
            grp, num = key
            new_w, new_h, new_payload = png_to_payload(img_path)
            sprites.append({
                "grp": grp, "num": num, "w": new_w, "h": new_h, "ax": new_ax, "ay": new_ay,
                "link": 0, "fmt": 12, "depth": 32, "payload": new_payload,
                "pal_idx": 0, "flags": 0
            })
            print(f"[{sff_path.name}] Added sprite ({grp}, {num}) -> {new_w}x{new_h}")

    new_num_sprites = len(sprites)
    new_table_off = 512
    new_pal_off = 512
    new_ldata_off = new_table_off + new_num_sprites * 28
    new_ldata_len = sum(len(s["payload"]) for s in sprites)
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
    for s in sprites:
        sz = len(s["payload"])
        rec = struct.pack(
            "<HHHHhhHBBIIHH",
            s["grp"], s["num"], s["w"], s["h"], s["ax"], s["ay"],
            s["link"], s["fmt"], s["depth"], cur_off, sz, s["pal_idx"], s["flags"]
        )
        out.extend(rec)
        cur_off += sz

    for s in sprites:
        out.extend(s["payload"])

    with open(sff_path, "wb") as f:
        f.write(out)
    print(f"Successfully wrote {sff_path} ({len(out)} bytes)")

# Update Chava: exactly scratch/chava_9000_1.png and clean 24x24 icon
update_sff_portraits("chars/chava/chava.sff", {
    (9000, 0): ("scratch/chava_icon_24.png", 0, 0),
    (9000, 1): ("scratch/chava_9000_1.png", 0, 0),
})

# Update Hector: 24x24 icon and 120x140 portrait
update_sff_portraits("chars/hector/hector.sff", {
    (9000, 0): ("scratch/hector_icon_24.png", 0, 0),
    (9000, 1): ("scratch/hector_9000_1.png", 0, 0),
})

print("SFF portraits rebuilt successfully!")
