import os
from PIL import Image

OUT = "scratch"
os.makedirs(OUT, exist_ok=True)

# 1. Chava High-Res Source
chava_src = Image.open("chars/chava/sprites_clean/portrait_clean_transparent.png")
# Chava's head in 1024x1024:
# Hair top: y=17, Eyes: y~270, Chin: y~490, Chest: y~850
# Horizontal center: x~520

# 1A. Chava Select Portrait (120x140) - grp=9000, num=1
# Crop box (width 720, height 840, aspect ratio 12:14)
# From x=160 to 880, y=10 to 850
crop_select = chava_src.crop((160, 10, 880, 850))
chava_select = crop_select.resize((120, 140), Image.LANCZOS)
chava_select.save(os.path.join(OUT, "chava_new_select_120x140.png"))
print("Generated chava_new_select_120x140.png")

# 1B. Chava Fight HUD Portrait (88x80) - grp=9000, num=0
# Focus on head, glasses, smile and collar
# From x=220 to 820 (width 600), y=10 to 555 (height 545, aspect 600:545 ~ 88:80)
crop_hud = chava_src.crop((220, 10, 820, 555))
chava_hud = crop_hud.resize((88, 80), Image.LANCZOS)
chava_hud.save(os.path.join(OUT, "chava_new_hud_88x80.png"))
print("Generated chava_new_hud_88x80.png")

# 2. Hector Fight HUD Portrait (88x80) - grp=9000, num=0
hector_src = Image.open("scratch/hector_9000_1.png")
# In Hector 120x140:
# Head is from x=15 to 105 (width 90), y=5 to 87 (height 82)
hector_crop = hector_src.crop((16, 5, 104, 85)) # 88x80
hector_hud = hector_crop.resize((88, 80), Image.LANCZOS)
hector_hud.save(os.path.join(OUT, "hector_new_hud_88x80.png"))
print("Generated hector_new_hud_88x80.png")
