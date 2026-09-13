import os
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = "scratch/hud_preview"
os.makedirs(OUT_DIR, exist_ok=True)

def get_fonts():
    try:
        font_code = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 11)
        font_code_bold = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 12)
        font_code_sm = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 9)
        font_label = ImageFont.truetype("C:/Windows/Fonts/impact.ttf", 18)
        font_label_sm = ImageFont.truetype("C:/Windows/Fonts/impact.ttf", 14)
    except Exception:
        font_code = ImageFont.load_default()
        font_code_bold = font_code
        font_code_sm = font_code
        font_label = font_code
        font_label_sm = font_code
    return font_code, font_code_bold, font_code_sm, font_label, font_label_sm

font_code, font_code_bold, font_code_sm, font_label, font_label_sm = get_fonts()

# -------------------------------------------------------------
# 1. P1 CONSOLE BACKGROUND (grp=10, num=0) - 530x88
# -------------------------------------------------------------
def make_p1_console():
    W, H = 530, 88
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    # Main metallic casing
    d.rounded_rectangle([0, 0, W-1, H-1], radius=6, fill=(24, 29, 36, 245), outline=(78, 92, 108, 255), width=2)
    d.rounded_rectangle([2, 2, W-3, H-3], radius=4, outline=(40, 48, 58, 255), width=1)
    d.line([8, 2, W-8, 2], fill=(130, 150, 175, 180), width=1)

    # Portrait bay at left: (x=0 to 80)
    # Recessed dark portrait area (72x84 from x=4, y=2 to x=76, y=86)
    d.rectangle([4, 2, 76, 85], fill=(12, 15, 20, 255), outline=(50, 65, 80, 255), width=1)

    # Divider between portrait and lifebar console
    d.line([80, 2, 80, H-3], fill=(78, 92, 108, 255), width=2)
    d.line([81, 2, 81, H-3], fill=(30, 35, 45, 255), width=1)

    # Rivets
    for rx, ry in [(W-8, 7), (W-8, H-8)]:
        d.ellipse([rx-3, ry-3, rx+3, ry+3], fill=(15, 18, 22, 255), outline=(130, 145, 165, 255), width=1)
        d.point((rx, ry), fill=(220, 230, 240, 255))

    # Circuit traces
    cc = (30, 75, 85, 140)
    d.line([120, 12, 160, 12], fill=cc, width=1)
    d.line([160, 12, 168, 18], fill=cc, width=1)
    d.ellipse([167, 17, 171, 21], fill=cc)

    # Header: { while (!dead) }  🐞  Mini Student  // TODO: survive()
    d.text((90, 6), "{ while (!dead) }", fill=(210, 240, 160, 255), font=font_code_bold)
    
    bx, by = 215, 8
    d.ellipse([bx+2, by+2, bx+7, by+7], fill=(220, 40, 40, 255))
    d.point((bx+4, by+4), fill=(20, 20, 20, 255))
    
    sx, sy = 240, 4
    d.rectangle([sx+2, sy, sx+6, sy+2], fill=(120, 70, 30))
    d.rectangle([sx+2, sy+3, sx+5, sy+5], fill=(255, 210, 175))
    d.rectangle([sx+1, sy+6, sx+6, sy+9], fill=(40, 100, 180))
    d.rectangle([sx+2, sy+10, sx+3, sy+11], fill=(50, 60, 75))
    d.rectangle([sx+5, sy+10, sx+6, sy+11], fill=(50, 60, 75))

    d.text((275, 6), "// TODO: survive()", fill=(80, 180, 100, 220), font=font_code)

    # OS buttons top right
    ox, oy = W - 55, 5
    d.rectangle([ox, oy, ox+11, oy+10], fill=(38, 45, 55), outline=(90, 105, 120))
    d.line([ox+2, oy+7, ox+8, oy+7], fill=(200, 210, 220), width=1)
    d.rectangle([ox+14, oy, ox+25, oy+10], fill=(38, 45, 55), outline=(90, 105, 120))
    d.rectangle([ox+16, oy+2, ox+23, oy+8], outline=(200, 210, 220), width=1)
    d.rectangle([ox+28, oy, ox+39, oy+10], fill=(190, 40, 40), outline=(225, 90, 90))
    d.line([ox+31, oy+3, ox+36, oy+7], fill=(255, 255, 255), width=1)
    d.line([ox+36, oy+3, ox+31, oy+7], fill=(255, 255, 255), width=1)

    # Health Bar Label "VIDA" badge on left of bar
    d.rounded_rectangle([86, 24, 134, 48], radius=3, fill=(245, 190, 10, 255), outline=(20, 20, 20, 255), width=2)
    d.text((92, 26), "VIDA", fill=(25, 20, 5, 255), font=font_label)

    # Health Bar Recessed Slot: x=138 to 522 (w=384, h=24)
    slot_x0, slot_y0, slot_x1, slot_y1 = 138, 24, 522, 48
    d.rounded_rectangle([slot_x0, slot_y0, slot_x1, slot_y1], radius=3, fill=(10, 14, 18, 255), outline=(0, 200, 90, 180), width=2)

    # Status / code line at bottom
    d.text((90, 54), "{ compile_status: OK | stack: allocated }", fill=(70, 170, 230, 240), font=font_code_sm)
    d.text((360, 54), "// memory: 0x7FFE", fill=(130, 210, 180, 240), font=font_code_sm)

    # Bottom cables
    d.arc([150, H-18, 250, H+1], start=0, end=180, fill=(35, 145, 225, 230), width=2)
    d.arc([270, H-16, 380, H+2], start=0, end=180, fill=(215, 45, 45, 230), width=2)

    im.save(os.path.join(OUT_DIR, "bg_p1.png"))
    return im

# -------------------------------------------------------------
# 2. P2 CONSOLE BACKGROUND (grp=10, num=1) - 530x88 (Mirrored)
# -------------------------------------------------------------
def make_p2_console():
    W, H = 530, 88
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    # Main metallic casing
    d.rounded_rectangle([0, 0, W-1, H-1], radius=6, fill=(24, 29, 36, 245), outline=(78, 92, 108, 255), width=2)
    d.rounded_rectangle([2, 2, W-3, H-3], radius=4, outline=(40, 48, 58, 255), width=1)
    d.line([8, 2, W-8, 2], fill=(130, 150, 175, 180), width=1)

    # Portrait bay at right: (x=450 to 530)
    # Recessed dark portrait area (72x84 from x=454, y=2 to x=526, y=86)
    d.rectangle([454, 2, 526, 85], fill=(12, 15, 20, 255), outline=(50, 65, 80, 255), width=1)

    # Divider between lifebar and portrait
    d.line([450, 2, 450, H-3], fill=(78, 92, 108, 255), width=2)
    d.line([449, 2, 449, H-3], fill=(30, 35, 45, 255), width=1)

    # Rivets
    for rx, ry in [(7, 7), (7, H-8)]:
        d.ellipse([rx-3, ry-3, rx+3, ry+3], fill=(15, 18, 22, 255), outline=(130, 145, 165, 255), width=1)
        d.point((rx, ry), fill=(220, 230, 240, 255))

    # OS buttons top left for P2
    ox, oy = 15, 5
    d.rectangle([ox, oy, ox+11, oy+10], fill=(38, 45, 55), outline=(90, 105, 120))
    d.line([ox+2, oy+7, ox+8, oy+7], fill=(200, 210, 220), width=1)
    d.rectangle([ox+14, oy, ox+25, oy+10], fill=(38, 45, 55), outline=(90, 105, 120))
    d.rectangle([ox+16, oy+2, ox+23, oy+8], outline=(200, 210, 220), width=1)
    d.rectangle([ox+28, oy, ox+39, oy+10], fill=(190, 40, 40), outline=(225, 90, 90))
    d.line([ox+31, oy+3, ox+36, oy+7], fill=(255, 255, 255), width=1)
    d.line([ox+36, oy+3, ox+31, oy+7], fill=(255, 255, 255), width=1)

    # Header: // TODO: survive()  Mini Student  🐞  { while (!dead) }
    d.text((95, 6), "// TODO: survive()", fill=(80, 180, 100, 220), font=font_code)
    
    sx, sy = 240, 4
    d.rectangle([sx+2, sy, sx+6, sy+2], fill=(120, 70, 30))
    d.rectangle([sx+2, sy+3, sx+5, sy+5], fill=(255, 210, 175))
    d.rectangle([sx+1, sy+6, sx+6, sy+9], fill=(180, 40, 80))
    d.rectangle([sx+2, sy+10, sx+3, sy+11], fill=(50, 60, 75))
    d.rectangle([sx+5, sy+10, sx+6, sy+11], fill=(50, 60, 75))

    bx, by = 265, 8
    d.ellipse([bx+2, by+2, bx+7, by+7], fill=(220, 40, 40, 255))
    d.point((bx+4, by+4), fill=(20, 20, 20, 255))

    d.text((285, 6), "{ while (!dead) }", fill=(210, 240, 160, 255), font=font_code_bold)

    # Health Bar Recessed Track for P2: x=8 to 392 (w=384, h=24)
    slot_x0, slot_y0, slot_x1, slot_y1 = 8, 24, 392, 48
    d.rounded_rectangle([slot_x0, slot_y0, slot_x1, slot_y1], radius=3, fill=(10, 14, 18, 255), outline=(0, 200, 90, 180), width=2)

    # Health Bar Label "VIDA" badge on right of bar
    d.rounded_rectangle([396, 24, 444, 48], radius=3, fill=(245, 190, 10, 255), outline=(20, 20, 20, 255), width=2)
    d.text((402, 26), "VIDA", fill=(25, 20, 5, 255), font=font_label)

    # Status / code line at bottom
    d.text((15, 54), "{ try { stack.pop(); } catch(KO) { ... }", fill=(70, 170, 230, 240), font=font_code_sm)
    d.text((285, 54), "| compile_status [ OK ] }", fill=(130, 210, 180, 240), font=font_code_sm)

    # Bottom cables
    d.arc([150, H-18, 250, H+1], start=0, end=180, fill=(35, 145, 225, 230), width=2)
    d.arc([270, H-16, 380, H+2], start=0, end=180, fill=(215, 45, 45, 230), width=2)

    im.save(os.path.join(OUT_DIR, "bg_p2.png"))
    return im

# -------------------------------------------------------------
# 3. SEGMENTED LIFEBAR FILL (380x20)
# -------------------------------------------------------------
def make_segmented_bar(fill_color, core_color, outline_color, name):
    W, H = 380, 20
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    # 25 segmented pill blocks (width 13, gap 2)
    num_blocks = 25
    block_w = 13
    gap = 2

    for i in range(num_blocks):
        bx0 = i * (block_w + gap) + 2
        bx1 = bx0 + block_w
        if bx1 > W:
            break
        # Segment block
        d.rounded_rectangle([bx0, 1, bx1, H-2], radius=3, fill=fill_color, outline=outline_color, width=1)
        # Inner glow line
        d.rounded_rectangle([bx0+2, 3, bx1-2, H-4], radius=2, fill=core_color)
        # Vertical sheen line
        d.line([bx0+3, 4, bx1-3, 4], fill=(255, 255, 255, 200), width=1)

    im.save(os.path.join(OUT_DIR, f"{name}.png"))
    return im

# -------------------------------------------------------------
# 4. POWERBAR "STACK" (grp=40,0 / grp=43,0)
# -------------------------------------------------------------
def make_power_bg():
    W, H = 220, 28
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    # Frame
    d.rounded_rectangle([0, 0, W-1, H-1], radius=4, fill=(20, 25, 32, 240), outline=(60, 75, 90, 255), width=2)
    # STACK label
    d.text((8, 5), "STACK", fill=(0, 190, 255, 255), font=font_label_sm)
    # Energy slot
    d.rounded_rectangle([54, 4, W-6, H-5], radius=2, fill=(8, 12, 16, 255), outline=(0, 140, 220, 180), width=1)
    
    im.save(os.path.join(OUT_DIR, "power_bg.png"))
    return im

def make_power_fill():
    W, H = 158, 18
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    for x in range(W):
        r = int(0 + (x / W) * 20)
        g = int(140 + (x / W) * 90)
        b = 255
        d.line([x, 1, x, H-2], fill=(r, g, b, 245))
    
    d.line([2, 2, W-3, 2], fill=(210, 245, 255, 220), width=1)
    d.line([2, 3, W-3, 3], fill=(160, 225, 255, 180), width=1)
    d.text((10, 3), "stack.pop(); 100%", fill=(10, 20, 40, 230), font=font_code_sm)
    
    im.save(os.path.join(OUT_DIR, "power_fill.png"))
    return im

# -------------------------------------------------------------
# 5. FACE PORTRAIT BEZEL FRAME (grp=51,0 and 51,1) - 80x88
# -------------------------------------------------------------
def make_face_frame_p1():
    W, H = 80, 88
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    # Outer border
    # Inner viewport is (4, 2) to (76, 86) -> 72x84
    # Frame bevel border around the viewport
    d.rectangle([0, 0, 3, H-1], fill=(28, 35, 45, 255))
    d.rectangle([76, 0, W-1, H-1], fill=(28, 35, 45, 255))
    d.rectangle([0, 0, W-1, 1], fill=(35, 44, 56, 255))
    d.rectangle([0, 86, W-1, H-1], fill=(20, 25, 33, 255))

    # Inner bevel outline
    d.rectangle([3, 1, 76, 86], outline=(0, 220, 140, 255), width=1)

    # High-tech corner HUD accents
    d.line([3, 1, 15, 1], fill=(0, 255, 200, 255), width=2)
    d.line([3, 1, 3, 15], fill=(0, 255, 200, 255), width=2)
    
    d.line([76, 1, 64, 1], fill=(0, 255, 200, 255), width=2)
    d.line([76, 1, 76, 15], fill=(0, 255, 200, 255), width=2)

    d.line([3, 86, 15, 86], fill=(0, 255, 200, 255), width=2)
    d.line([3, 86, 3, 72], fill=(0, 255, 200, 255), width=2)

    d.line([76, 86, 64, 86], fill=(0, 255, 200, 255), width=2)
    d.line([76, 86, 76, 72], fill=(0, 255, 200, 255), width=2)

    im.save(os.path.join(OUT_DIR, "face_frame_p1.png"))
    return im

def make_face_frame_p2():
    im_p1 = make_face_frame_p1()
    im_p2 = im_p1.transpose(Image.FLIP_LEFT_RIGHT)
    im_p2.save(os.path.join(OUT_DIR, "face_frame_p2.png"))
    return im_p2

def make_face_bg():
    W, H = 80, 88
    im = Image.new("RGBA", (W, H), (14, 18, 24, 255))
    d = ImageDraw.Draw(im)
    # Subtle grid
    for x in range(4, 76, 8):
        d.line([x, 2, x, 86], fill=(20, 28, 38, 255), width=1)
    for y in range(2, 86, 8):
        d.line([4, y, 76, y], fill=(20, 28, 38, 255), width=1)
    im.save(os.path.join(OUT_DIR, "face_bg.png"))
    return im

# -------------------------------------------------------------
# 6. WIN STARS / XP ROUND COUNTER (grp=70,0 / grp=71,0) - 24x24
# -------------------------------------------------------------
def draw_star(draw, cx, cy, r_out, r_in, fill_col, out_col):
    import math
    points = []
    for i in range(10):
        angle = i * (math.pi / 5) - math.pi / 2
        r = r_out if i % 2 == 0 else r_in
        points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    draw.polygon(points, fill=fill_col, outline=out_col)

def make_win_stars():
    im_off = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
    d_off = ImageDraw.Draw(im_off)
    draw_star(d_off, 12, 12, 10, 4, fill_col=(20, 30, 40, 180), out_col=(0, 160, 200, 220))
    im_off.save(os.path.join(OUT_DIR, "win_star_off.png"))

    im_on = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
    d_on = ImageDraw.Draw(im_on)
    draw_star(d_on, 12, 12, 11, 5, fill_col=(0, 255, 200, 120), out_col=None)
    draw_star(d_on, 12, 12, 9, 4, fill_col=(80, 255, 220, 255), out_col=(255, 255, 255, 255))
    im_on.save(os.path.join(OUT_DIR, "win_star_on.png"))

print("Generating unified HUD assets...")
make_p1_console()
make_p2_console()

make_segmented_bar(fill_color=(0, 225, 90, 255), core_color=(180, 255, 180, 255), outline_color=(0, 100, 40, 255), name="life_100")
make_segmented_bar(fill_color=(240, 200, 10, 255), core_color=(255, 250, 170, 255), outline_color=(120, 90, 0, 255), name="life_50")
make_segmented_bar(fill_color=(235, 40, 40, 255), core_color=(255, 180, 180, 255), outline_color=(120, 10, 10, 255), name="life_25")
make_segmented_bar(fill_color=(255, 140, 10, 255), core_color=(255, 220, 120, 255), outline_color=(150, 60, 0, 255), name="life_mid")

make_power_bg()
make_power_fill()
make_face_frame_p1()
make_face_frame_p2()
make_face_bg()
make_win_stars()

print("All unified HUD assets generated successfully!")
