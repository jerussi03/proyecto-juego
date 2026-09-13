import os
from PIL import Image, ImageOps

PREVIEW_DIR = "scratch/hud_preview"

# Create a 1280x720 canvas
canvas = Image.new("RGBA", (1280, 720), (18, 22, 28, 255))

# Load assets
bg_p1 = Image.open(os.path.join(PREVIEW_DIR, "bg_p1.png"))
bg_p2 = Image.open(os.path.join(PREVIEW_DIR, "bg_p2.png"))
life_100 = Image.open(os.path.join(PREVIEW_DIR, "life_100.png"))
power_bg = Image.open(os.path.join(PREVIEW_DIR, "power_bg.png"))
power_fill = Image.open(os.path.join(PREVIEW_DIR, "power_fill.png"))
face_bg = Image.open(os.path.join(PREVIEW_DIR, "face_bg.png"))
face_frame = Image.open(os.path.join(PREVIEW_DIR, "face_frame.png"))
win_on = Image.open(os.path.join(PREVIEW_DIR, "win_star_on.png"))
win_off = Image.open(os.path.join(PREVIEW_DIR, "win_star_off.png"))

# Character portraits
chava_face = Image.open("scratch/chava_new_hud_88x80.png")
hector_face = Image.open("scratch/hector_new_hud_88x80.png")

# P1 placement
# pos: 585, 25. With axis=(480, 0), top-left = (105, 25)
canvas.paste(bg_p1, (105, 25), bg_p1)
# Life fill: slot at x: 64, y: 26 inside 480x88 -> canvas (105+64, 25+26) = (169, 51)
canvas.paste(life_100, (169, 51), life_100)

# P1 Powerbar: pos 585, 118. With axis=(220, 0), top-left = (365, 118)
canvas.paste(power_bg, (365, 118), power_bg)
canvas.paste(power_fill, (365 + 56, 118 + 5), power_fill)

# P1 Face Frame: pos 8, 15
canvas.paste(face_bg, (8, 15), face_bg)
canvas.paste(chava_face, (8 + 8, 15 + 16), chava_face)
canvas.paste(face_frame, (8, 15), face_frame)

# P1 Stars
canvas.paste(win_on, (325, 120), win_on)
canvas.paste(win_on, (295, 120), win_on)
canvas.paste(win_off, (265, 120), win_off)

# P2 placement
# pos: 695, 25. With axis=(0, 0), top-left = (695, 25)
canvas.paste(bg_p2, (695, 25), bg_p2)
# Life fill: slot at x: 18, y: 26 inside 480x88 -> canvas (695+18, 25+26) = (713, 51)
canvas.paste(life_100, (713, 51), life_100)

# P2 Powerbar: pos 695, 118. With axis=(0, 0), top-left = (695, 118)
canvas.paste(power_bg, (695, 118), power_bg)
canvas.paste(power_fill, (695 + 56, 118 + 5), power_fill)

# P2 Face Frame: pos 1164, 15
hector_flipped = ImageOps.mirror(hector_face)
canvas.paste(face_bg, (1164, 15), face_bg)
canvas.paste(hector_flipped, (1164 + 8, 15 + 16), hector_flipped)
canvas.paste(face_frame, (1164, 15), face_frame)

# P2 Stars
canvas.paste(win_on, (930, 120), win_on)
canvas.paste(win_off, (960, 120), win_off)

# Timer (Center at 640, 30)
from PIL import ImageDraw, ImageFont
d = ImageDraw.Draw(canvas)
try:
    font_timer = ImageFont.truetype("C:/Windows/Fonts/impact.ttf", 36)
except:
    font_timer = ImageFont.load_default()

d.text((625, 38), "99", fill=(10, 15, 20), font=font_timer)
d.text((624, 36), "99", fill=(255, 220, 40), font=font_timer)

canvas.save("scratch/hud_preview/hud_mockup.png")
print("Updated mockup saved to scratch/hud_preview/hud_mockup.png")
