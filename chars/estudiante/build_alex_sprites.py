"""Build the hand-authored, transparent animation sprites for Alex.

This deliberately does not blend generated artwork. Every gameplay frame is
drawn from a pose definition, so hands, legs, the backpack and laptop stay
attached to the same character throughout an animation.
"""
from __future__ import annotations

import io
import math
import os
import struct
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).parent
OUT = ROOT / "sprites_alex_v2"
OUT.mkdir(exist_ok=True)
REAL = ROOT / "sprites_transparent"
W, H, GROUND = 320, 400, 360

INK = (20, 28, 39, 255)
HOODIE = (31, 104, 91, 255)
HOODIE_LIGHT = (46, 137, 118, 255)
DENIM = (38, 62, 103, 255)
SKIN = (191, 123, 82, 255)
HAIR = (37, 29, 30, 255)
WHITE = (238, 242, 244, 255)
BAG = (69, 57, 70, 255)
CYAN = (54, 225, 243, 255)
BLUE = (76, 120, 255, 255)
PAPER = (250, 246, 225, 255)


def layer_line(draw, points, color, width, outline=INK):
    draw.line(points, fill=outline, width=width + 8, joint="curve")
    draw.line(points, fill=color, width=width, joint="curve")
    for x, y in (points[0], points[-1]):
        draw.ellipse((x-width//2-4, y-width//2-4, x+width//2+4, y+width//2+4), fill=outline)
        draw.ellipse((x-width//2, y-width//2, x+width//2, y+width//2), fill=color)


def shoe(draw, x, y, facing=1):
    points = [(x-25, y-5), (x+23, y-5), (x+32*facing, y+9), (x-22, y+10)]
    draw.polygon(points, fill=INK)
    inner = [(x-20, y-3), (x+20, y-3), (x+25*facing, y+5), (x-18, y+6)]
    draw.polygon(inner, fill=WHITE)
    draw.line((x-6, y, x+14, y), fill=HOODIE, width=4)


def backpack(draw, x, y, swing=0):
    x += swing
    draw.rounded_rectangle((x-47, y-10, x+4, y+74), radius=14, fill=INK)
    draw.rounded_rectangle((x-41, y-4, x-2, y+68), radius=11, fill=BAG)
    draw.arc((x-37, y+15, x-7, y+53), 200, 80, fill=(142, 124, 144, 255), width=4)
    draw.line((x-9, y+5, x+10, y+44), fill=INK, width=10)
    draw.line((x-9, y+5, x+10, y+44), fill=(114, 96, 117, 255), width=4)


def face(draw, cx, cy, tilt=0, expression="calm"):
    draw.ellipse((cx-31, cy-37, cx+31, cy+35), fill=INK)
    draw.ellipse((cx-27, cy-33, cx+27, cy+31), fill=SKIN)
    draw.pieslice((cx-29, cy-38, cx+29, cy+7), 180, 360, fill=HAIR)
    draw.ellipse((cx-20, cy-29, cx+17, cy-7), fill=HAIR)
    brow = 5 if expression in ("focus", "hit") else 0
    draw.line((cx-17, cy-3-brow, cx-5, cy-5), fill=INK, width=3)
    draw.line((cx+5, cy-5, cx+17, cy-3-brow), fill=INK, width=3)
    if expression == "hit":
        draw.line((cx-10, cy+17, cx+12, cy+9), fill=INK, width=4)
    else:
        draw.arc((cx-11, cy+7, cx+13, cy+23), 10, 170, fill=INK, width=3)


def paper(draw, x, y, angle=0):
    # A readable white assignment card with a red "10", intentionally kept
    # graphic rather than AI-rendered text.
    pts = [(x-20, y-28), (x+24, y-23), (x+20, y+28), (x-24, y+23)]
    draw.polygon(pts, fill=INK)
    pts2 = [(x-16, y-24), (x+20, y-20), (x+16, y+24), (x-20, y+19)]
    draw.polygon(pts2, fill=PAPER)
    for yy in (-11, -4, 3):
        draw.line((x-11, y+yy, x+8, y+yy+2), fill=(100, 113, 125, 255), width=2)
    draw.ellipse((x+1, y+5, x+16, y+20), outline=(205, 54, 55, 255), width=3)
    draw.text((x+4, y+5), "10", fill=(190, 38, 39, 255), stroke_width=0)


def laptop(draw, x, y, open_amount=1.0):
    # Screen and base share a hinge; this avoids the floating-laptop problem.
    draw.polygon([(x-34, y), (x+31, y-4), (x+37, y+7), (x-29, y+11)], fill=INK)
    draw.polygon([(x-29, y+2), (x+27, y-1), (x+31, y+4), (x-25, y+7)], fill=(104, 116, 132, 255))
    top = y - int(50 * open_amount)
    draw.polygon([(x-26, y), (x-20, top), (x+25, top-4), (x+31, y-4)], fill=INK)
    draw.polygon([(x-20, y-5), (x-16, top+4), (x+20, top), (x+24, y-8)], fill=(31, 64, 91, 255))
    draw.line((x-13, top+12, x+16, top+9), fill=CYAN, width=3)


def hologram(draw, x, y, phase):
    glow = (0, 203, 255, 70)
    draw.ellipse((x-68, y-95, x+68, y+90), fill=glow)
    for ox, oy, ww in ((-43,-55,50), (-8,-82,63), (22,-35,52), (-48,20,60)):
        xx = x + ox + phase * 3
        yy = y + oy
        draw.rounded_rectangle((xx, yy, xx+ww, yy+22), radius=3, outline=CYAN, width=3)
        draw.line((xx+6, yy+8, xx+ww-7, yy+8), fill=BLUE, width=2)
        draw.line((xx+6, yy+15, xx+ww-16, yy+15), fill=CYAN, width=2)
    draw.arc((x-43, y-38, x+43, y+48), 190, 350, fill=CYAN, width=5)
    draw.ellipse((x-8, y-5, x+8, y+11), fill=CYAN)


def base_sprite(kind, phase=0):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x, gy = 145, GROUND
    bob = 0
    crouch = kind in {"crouch", "slide"}
    air = kind == "air"
    hit = kind == "hit"
    if kind == "idle":
        bob = (0, -2, -4, -2, 1)[phase % 5]
    if hit:
        x -= (3, 12, 5)[phase % 3]
    if air:
        gy = 295
    if crouch:
        gy = 360

    # Leg poses are first so torso and arms read cleanly in front.
    if kind == "walk":
        poses = [((125, 256), (101, 309), (90, gy)), ((157, 256), (176, 308), (190, gy))]
        walk = (-10, 2, 10, -2)[phase % 4]
        poses[0] = ((125,256), (101+walk,309), (90+walk*2,gy))
        poses[1] = ((157,256), (176-walk,308), (190-walk*2,gy))
    elif kind == "slide":
        if phase == 0:
            poses = [((133,295), (157,328), (193,gy-5)), ((145,298), (111,337), (69,gy))]
        elif phase == 1:
            poses = [((133,295), (174,324), (244,gy-5)), ((145,298), (96,340), (38,gy))]
        else:
            poses = [((133,295), (160,330), (212,gy-5)), ((145,298), (110,337), (66,gy))]
    elif crouch:
        poses = [((126, 285), (105, 330), (82, gy)), ((156, 285), (182, 332), (209, gy))]
    elif air:
        poses = [((126, 249), (102, 281), (72, 286)), ((154, 249), (183, 274), (212, 253))]
        if phase == 1:
            poses = [((126,249), (97,274), (57,273)), ((154,249), (180,286), (221,284))]
        elif phase == 2:
            poses = [((126,249), (116,290), (93,304)), ((154,249), (173,264), (205,233))]
    elif hit:
        poses = [((126, 256), (95, 306), (77, gy)), ((154, 256), (172, 315), (194, gy))]
    else:
        poses = [((126, 253), (108, 309), (92, gy)), ((155, 253), (174, 308), (190, gy))]
    for hip, knee, foot in poses:
        layer_line(d, [hip, knee, foot], DENIM, 25)
        shoe(d, foot[0], foot[1], 1 if foot[0] >= x else -1)

    torso_y = (156 if not crouch else 203) + bob
    hip_y = (264 if not crouch else 291) + bob
    if air: torso_y, hip_y = 144, 251
    backpack(d, x-38, torso_y+15, -phase*2 if kind == "walk" else 0)
    torso = [(x-35, torso_y+18), (x-21, torso_y-1), (x+22, torso_y-1), (x+37, torso_y+25), (x+24, hip_y), (x-27, hip_y)]
    d.polygon(torso, fill=INK)
    d.polygon([(px+(2 if px<x else -2), py+5) for px,py in torso], fill=HOODIE)
    d.line((x-10, torso_y+7, x+4, torso_y+25), fill=HOODIE_LIGHT, width=4)
    d.arc((x-14, torso_y-3, x+14, torso_y+18), 10, 170, fill=WHITE, width=3)
    face(d, x, torso_y-40, expression="hit" if hit else ("focus" if kind in {"bag", "super"} else "calm"))

    shoulder_l, shoulder_r = (x-25, torso_y+24), (x+25, torso_y+24)
    if kind == "homework":
        if phase == 0:
            layer_line(d, [shoulder_l, (x+18, torso_y+48), (x+43, torso_y+43)], SKIN, 16)
            layer_line(d, [shoulder_r, (x+45, torso_y+70), (x+66, torso_y+59)], SKIN, 16)
            paper(d, x+53, torso_y+34)
        elif phase == 1:
            layer_line(d, [shoulder_l, (x+54, torso_y+38), (255, torso_y+31)], SKIN, 16)
            layer_line(d, [shoulder_r, (x+45, torso_y+72), (x+71, torso_y+63)], SKIN, 16)
            paper(d, 270, torso_y+24)
        else:
            layer_line(d, [shoulder_l, (x+32, torso_y+52), (x+18, torso_y+72)], SKIN, 16)
            layer_line(d, [shoulder_r, (x+45, torso_y+65), (x+60, torso_y+68)], SKIN, 16)
            paper(d, x+43, torso_y+66)
    elif kind == "bag":
        swing = (-20, 35, 6)[phase % 3]
        hand = (x+swing+65, torso_y+42)
        layer_line(d, [shoulder_r, (x+50, torso_y+15), hand], SKIN, 17)
        layer_line(d, [shoulder_l, (x+25, torso_y+69), (x+56, torso_y+75)], SKIN, 16)
        backpack(d, x+swing+70, torso_y+3, 0)
        # impact books only on contact frame
        if phase == 1:
            d.rectangle((x+swing+12, torso_y-18, x+swing+27, torso_y+6), fill=PAPER, outline=INK, width=3)
            d.polygon([(x+swing+20, torso_y-26),(x+swing+40, torso_y-15),(x+swing+27, torso_y-2)], fill=(229,179,64,255))
    elif kind == "slide":
        reach = (75, 128, 91)[phase % 3]
        layer_line(d, [shoulder_r, (x+42, 300), (x+reach-24, 324)], SKIN, 15)
        layer_line(d, [shoulder_l, (x+8, 304), (x+reach-45, 322)], SKIN, 15)
        laptop(d, x+reach, 326, (0.35, 0.8, 0.5)[phase % 3])
    elif kind == "air":
        layer_line(d, [shoulder_r, (x+53, torso_y+31), (x+79, torso_y+58)], SKIN, 16)
        layer_line(d, [shoulder_l, (x+21, torso_y+62), (x+58, torso_y+70)], SKIN, 16)
        backpack(d, x+100, torso_y+42, 0)
    elif kind == "super":
        layer_line(d, [shoulder_r, (x+54, torso_y+43), (x+79, torso_y+40)], SKIN, 15)
        layer_line(d, [shoulder_l, (x+26, torso_y+66), (x+67, torso_y+50)], SKIN, 15)
        laptop(d, x+82, torso_y+46, 0.9)
        hologram(d, x-75, torso_y-26, phase)
    elif kind == "guard":
        recoil = (0, -7, 4)[phase % 3]
        layer_line(d, [shoulder_l, (x-7+recoil, torso_y+38), (x+25+recoil, torso_y+13)], SKIN, 16)
        layer_line(d, [shoulder_r, (x+23+recoil, torso_y+44), (x+34+recoil, torso_y+18)], SKIN, 16)
    elif hit:
        layer_line(d, [shoulder_l, (x-41, torso_y+43), (x-55, torso_y+75)], SKIN, 16)
        layer_line(d, [shoulder_r, (x+37, torso_y+36), (x+55, torso_y+6)], SKIN, 16)
    else:
        layer_line(d, [shoulder_l, (x-41, torso_y+65), (x-34, hip_y-4)], SKIN, 16)
        layer_line(d, [shoulder_r, (x+42, torso_y+62), (x+51, hip_y-6)], SKIN, 16)

    return im


def rendered_pose(source_name, scale=1.0, shift_x=0, shift_y=0, mirror=False):
    """Place a complete illustrated pose on a transparent canvas.

    We deliberately move and scale the *whole* drawing. The former builder
    cropped and blended isolated limbs, producing broken anatomy. The source
    PNGs already have alpha; their magenta RGB is fully transparent.
    """
    source = Image.open(REAL / source_name).convert("RGBA")
    if mirror:
        source = source.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    bbox = source.getbbox()
    pose = source.crop(bbox)
    if scale != 1.0:
        pose = pose.resize((round(pose.width * scale), round(pose.height * scale)), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", source.size, (0, 0, 0, 0))
    x = (canvas.width - pose.width) // 2 + shift_x
    y = canvas.height - pose.height + shift_y
    canvas.alpha_composite(pose, (x, y))
    return canvas


def save(name, kind, phase=0):
    # Every attack's active frame is a real, complete illustration of Alex.
    # Surrounding frames are intentional anticipation/recovery poses, not
    # generated body-part blends.
    source, scale, sx, sy, mirror = "stance_base.png", 1.0, 0, 0, False
    if kind == "idle":
        scale = (1.0, 1.008, 1.016, 1.008, 1.0)[phase % 5]
    elif kind == "walk":
        source = "walk_forward.png"
        scale = (1.0, 0.99, 1.01, 0.99)[phase % 4]
        sx = (-8, 4, 8, -4)[phase % 4]
        mirror = phase in (1, 3)
    elif kind == "crouch":
        source, scale = "attack_laptop_slide.png", 0.83
    elif kind == "guard":
        source, scale, sx = "stance_base.png", 0.96, (-8, -14, -5)[phase % 3]
    elif kind == "homework":
        source = ("stance_base.png", "attack_homework.png", "stance_base.png")[phase % 3]
        scale, sx = ((0.95, 0, 1.0)[phase % 3], (-28, 0, 20)[phase % 3])
    elif kind == "bag":
        source = ("stance_base.png", "attack_backpack.png", "stance_base.png")[phase % 3]
        scale, sx = ((0.95, 0, 1.0)[phase % 3], (-34, 0, 24)[phase % 3])
    elif kind == "slide":
        source = ("stance_base.png", "attack_laptop_slide.png", "stance_base.png")[phase % 3]
        scale, sx = ((0.82, 0.95, 0.88)[phase % 3], (-40, 0, 22)[phase % 3])
    elif kind == "air":
        source = ("jump_midair.png", "attack_aerial_backpack.png", "jump_midair.png")[phase % 3]
        scale, sx, sy = ((0.98, 1.0, 0.98)[phase % 3], (-12, 0, 12)[phase % 3], (-64, -80, -58)[phase % 3])
    elif kind == "super":
        source = ("stance_base.png", "super_ai_summon.png", "super_ai_summon.png")[phase % 3]
        scale, sx = ((0.96, 1.0, 1.03)[phase % 3], (-18, 0, 10)[phase % 3])
    elif kind == "victory":
        source = "win_pose.png"
    elif kind == "hit":
        source, scale, sx = "hit_reaction.png", (0.98, 1.0, 0.98)[phase % 3], (16, -12, 6)[phase % 3]
    rendered_pose(source, scale, sx, sy, mirror).save(OUT / name)


# Movement. These are actual pose cycles, not shifted copies of one illustration.
for n in range(5): save(f"spr_0_{n}.png", "idle", n)
for n in range(4): save(f"spr_20_{n}.png", "walk", n)
save("spr_11_0.png", "crouch")
save("spr_11_1.png", "crouch")
save("spr_41_0.png", "air", 0); save("spr_41_1.png", "air", 1); save("spr_41_2.png", "air", 2)
for n in range(3): save(f"spr_120_{n}.png", "guard", n)
save("spr_121_0.png", "guard"); save("spr_122_0.png", "guard")
for n in range(3): save(f"spr_200_{n}.png", "homework", n)
for n in range(3): save(f"spr_210_{n}.png", "bag", n)
for n in range(3): save(f"spr_400_{n}.png", "slide", n)
for n in range(3): save(f"spr_600_{n}.png", "air", n)
for n in range(3): save(f"spr_1000_{n}.png", "super", n)
for n in range(3): save(f"spr_5000_{n}.png", "hit", n)
save("spr_181_0.png", "victory")


def pack_png(path: Path, target_height: int):
    im = Image.open(path).convert("RGBA")
    bbox = im.getbbox()
    im = im.crop(bbox)
    scale = target_height / im.height
    im = im.resize((round(im.width * scale), target_height), Image.Resampling.LANCZOS)
    out = io.BytesIO(); im.save(out, format="PNG")
    return im.width, im.height, im.width // 2, im.height, out.getvalue()


table = [
    *((f"spr_0_{n}.png", 0, n, 110) for n in range(5)),
    ("spr_0_0.png",5,0,110), ("spr_11_0.png",6,0,75),
    ("spr_11_0.png",11,0,75), ("spr_11_1.png",11,1,75),
    *((f"spr_20_{n}.png",20,n,110) for n in range(4)),
    *((f"spr_20_{n}.png",21,n,110) for n in range(4)),
    *((f"spr_41_{n}.png",41,n,100) for n in range(3)),
    *((f"spr_120_{n}.png",120,n,110) for n in range(3)),
    ("spr_121_0.png",121,0,75), ("spr_122_0.png",122,0,100),
    ("spr_181_0.png",181,0,110),
    *((f"spr_200_{n}.png",200,n,110) for n in range(3)),
    *((f"spr_210_{n}.png",210,n,110) for n in range(3)),
    *((f"spr_400_{n}.png",400,n,70) for n in range(3)),
    *((f"spr_600_{n}.png",600,n,110) for n in range(3)),
    *((f"spr_1000_{n}.png",1000,n,110) for n in range(3)),
    *((f"spr_5000_{n}.png",5000,n,110) for n in range(3)),
]

sprites = []
for file_name, group, item, height in table:
    width, h, ax, ay, png = pack_png(OUT / file_name, height)
    sprites.append((group, item, width, h, ax, ay, struct.pack("<I", width*h*4) + png))

header_size, pal_size, node_size = 512, 16, 28
pal_offset = header_size
table_offset = pal_offset + pal_size
data_offset = table_offset + node_size * len(sprites)
palette = b"\0\0\0\xff" * 256
data = bytearray(); nodes = bytearray()
for group, item, width, height, ax, ay, block in sprites:
    offset = len(palette) + len(data)
    data.extend(block)
    nodes.extend(struct.pack("<HHHHhhHBBIIHH", group, item, width, height, ax, ay, 0, 12, 32, offset, len(block), 0, 0))
header = bytearray(header_size)
header[:12] = b"ElecbyteSpr\0"
header[12:16] = bytes([0,1,0,2]); header[24:28] = bytes([0,1,0,2])
struct.pack_into("<IIIIIIII", header, 36, table_offset, len(sprites), pal_offset, 1, data_offset, len(palette)+len(data), data_offset+len(palette)+len(data), 0)
pal = struct.pack("<HHHHII", 0,0,256,0,0,len(palette))
with open(ROOT / "estudiante.sff", "wb") as f:
    f.write(header); f.write(pal); f.write(nodes); f.write(palette); f.write(data)
print(f"Built {len(sprites)} transparent Alex sprites into estudiante.sff")
