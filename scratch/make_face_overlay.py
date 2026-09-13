from PIL import Image, ImageDraw, ImageFont

def make_face_components():
    W, H = 104, 100
    try:
        font_arcade_lg = ImageFont.truetype("C:/Windows/Fonts/impact.ttf", 16)
    except:
        font_arcade_lg = ImageFont.load_default()

    # 1. Background (grp=50, num=0/1): Dark monitor backing
    im_bg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d_bg = ImageDraw.Draw(im_bg)
    # Dark CRT monitor screen inside [8, 16, 96, 96]
    d_bg.rectangle([6, 14, 98, 98], fill=(12, 16, 22, 255))
    # Subtle scanlines
    for y in range(16, 96, 3):
        d_bg.line([8, y, 96, y], fill=(18, 26, 36, 180), width=1)
    im_bg.save("scratch/hud_preview/face_bg.png")

    # 2. Front Overlay Frame (grp=51, num=0/1)
    im_top = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d_top = ImageDraw.Draw(im_top)

    # Metallic casing around the box
    # Top plaque area [0..104, 0..16]
    # Left border [0..8, 14..100]
    # Right border [96..104, 14..100]
    # Bottom border [0..104, 96..100]

    # Draw outer frame with transparent center cutout:
    # Outer rectangle
    d_top.rounded_rectangle([2, 14, W-3, H-2], radius=4, fill=(24, 29, 36, 255), outline=(78, 92, 108, 255), width=2)
    # Cutout the center window: [8, 16, 96, 96]
    d_top.rectangle([8, 16, 96, 96], fill=(0, 0, 0, 0))

    # Inner bevel around the cutout window
    d_top.rectangle([7, 15, 97, 97], outline=(38, 46, 56, 255), width=1)

    # Cybernetic corner brackets
    col_bracket = (0, 255, 180, 255)
    # Top-left
    d_top.line([4, 15, 16, 15], fill=col_bracket, width=2)
    d_top.line([4, 15, 4, 27], fill=col_bracket, width=2)
    # Top-right
    d_top.line([W-5, 15, W-17, 15], fill=col_bracket, width=2)
    d_top.line([W-5, 15, W-5, 27], fill=col_bracket, width=2)
    # Bottom-left
    d_top.line([4, H-3, 16, H-3], fill=col_bracket, width=2)
    d_top.line([4, H-3, 4, H-15], fill=col_bracket, width=2)
    # Bottom-right
    d_top.line([W-5, H-3, W-17, H-3], fill=col_bracket, width=2)
    d_top.line([W-5, H-3, W-5, H-15], fill=col_bracket, width=2)

    # Golden Arcade "VIDA" Plaque at top [16, 0, 88, 16]
    d_top.rounded_rectangle([18, 0, 86, 16], radius=3, fill=(245, 190, 10, 255), outline=(20, 20, 20, 255), width=2)
    # Drop shadow on VIDA text
    d_top.text((37, 1), "VIDA", fill=(30, 20, 0, 255), font=font_arcade_lg)
    d_top.text((36, 0), "VIDA", fill=(255, 255, 255, 255), font=font_arcade_lg)

    im_top.save("scratch/hud_preview/face_frame.png")
    print("face_bg.png and face_frame.png generated successfully")

make_face_components()
