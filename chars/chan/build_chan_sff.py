from io import BytesIO
from pathlib import Path
import struct
from PIL import Image

ROOT = Path(__file__).parent
WALK_DIR = ROOT / "caminar"
IDLE_DIR = ROOT / "estaticochan"
PUNCH_DIR = ROOT / "golpeMySQL"
MONGO_DIR = ROOT / "golpeMongo"
KICK_DIR = ROOT / "patada"
KICK_STRONG_DIR = ROOT / "patadafuerte"
HIT_DIR = ROOT / "dparada"
JUMP_DIR = ROOT / "salto"
CROUCH_DIR = ROOT / "agachar"
CROUCH_IDLE_DIR = ROOT / "estaticaAgachada"
CROUCH_WALK_DIR = ROOT / "caminarAgachada"
OUTPUT = ROOT / "chan.sff"

# The jump clip (salto) is a continuous jump: crouch/launch (frames 1..13),
# airborne (14..19), then landing (20..27). The remaining frames repeat a
# second hop, so only the first 27 frames are used.
JUMP_START_END, JUMP_AIR_END, JUMP_LAND_END = 13, 19, 27

# The punch clip is 192 frames, but only frames 1..121 contain the actual
# punch motion (the rest is a static rest pose). Subsample every 4th frame so
# the punch lasts a playable amount of time (~31 frames) instead of 3+ seconds.
PUNCH_FIRST, PUNCH_LAST, PUNCH_STEP = 0, 121, 4
MONGO_STEP = 2
KICK_STEP = 2
KICK_STRONG_STEP = 4
HIT_STEP = 2

# Crouch clips (continuous numbering: agachar 1..40, estatica 41..70,
# caminar 71..180). The crouch-down transition is the crouching part of
# "agachar" (frames 20..40), the static crouch is "estatica" (41..70), and the
# crouch-walk is the walking part of "caminar" (frames 76..124).
CROUCH_DOWN_FIRST, CROUCH_DOWN_LAST, CROUCH_DOWN_STEP = 19, 40, 2
CROUCH_WALK_FIRST, CROUCH_WALK_LAST, CROUCH_WALK_STEP = 5, 54, 2

# The source frames are 720x1280 with the character content occupying a
# region that varies per frame. We crop every set to the union of its strong
# alpha bounding boxes (so all frames stay anchored the same way) and resize
# so the character content is the same on-screen height as the rest of the
# cast (~104 px tall, like Chava/Hector).
TARGET_CONTENT_H = 104


def process_set(files):
    images = [Image.open(path).convert("RGBA") for path in files]
    boxes = []
    for im in images:
        b = im.getchannel("A").point(lambda v: 255 if v > 128 else 0).getbbox()
        if b:
            boxes.append(b)
    x0 = min(b[0] for b in boxes)
    y0 = min(b[1] for b in boxes)
    x1 = max(b[2] for b in boxes)
    y1 = max(b[3] for b in boxes)
    return _process(images, (x0, y0, x1, y1))


def body_centered_crop(files):
    # The character's body can be off-center relative to the union bbox when
    # an attack (like a kick) extends far forward. Compute a crop centered on
    # the body's alpha centroid so the body stays anchored in the middle.
    images = [Image.open(path).convert("RGBA") for path in files]
    boxes = []
    sx = n = 0
    for im in images:
        a = im.getchannel("A").point(lambda v: 255 if v > 128 else 0)
        b = a.getbbox()
        if not b:
            continue
        boxes.append(b)
        px = a.load()
        for y in range(b[1], b[3], 6):
            for x in range(b[0], b[2], 4):
                if px[x, y] > 0:
                    sx += x
                    n += 1
    x0 = min(b[0] for b in boxes)
    y0 = min(b[1] for b in boxes)
    x1 = max(b[2] for b in boxes)
    y1 = max(b[3] for b in boxes)
    cx = sx / n
    half = max(x1 - cx, cx - x0)
    return _process(images, (round(cx - half), y0, round(cx + half), y1))


def _process(images, crop):
    x0, y0, x1, y1 = crop
    content_h = y1 - y0
    scale = TARGET_CONTENT_H / content_h
    frames = []
    for im in images:
        im = im.crop((x0, y0, x1, y1))
        w = max(1, round(im.width * scale))
        im = im.resize((w, TARGET_CONTENT_H), Image.LANCZOS)
        frames.append(im)
    return frames


def slice_frames(frames, start, end, step):
    return frames[start:end:step]


walk_frames = process_set(sorted(WALK_DIR.glob("*.png")))
idle_frames = process_set(sorted(IDLE_DIR.glob("*.png")))
punch_files = sorted(PUNCH_DIR.glob("*.png"))[PUNCH_FIRST:PUNCH_LAST:PUNCH_STEP]
punch_frames = process_set(punch_files)
mongo_files = sorted(MONGO_DIR.glob("*.png"))[::MONGO_STEP]
mongo_frames = process_set(mongo_files)
kick_files = sorted(KICK_DIR.glob("*.png"))[::KICK_STEP]
kick_frames = process_set(kick_files)
kick_strong_files = sorted(KICK_STRONG_DIR.glob("*.png"))[::KICK_STRONG_STEP]
kick_strong_frames = body_centered_crop(kick_strong_files)
hit_files = sorted(HIT_DIR.glob("*.png"))[::HIT_STEP]
hit_frames = process_set(hit_files)
salto_frames = process_set(sorted(JUMP_DIR.glob("*.png"))[:JUMP_LAND_END])
jump_start_frames = salto_frames[:JUMP_START_END]
jump_air_frames = salto_frames[JUMP_START_END:JUMP_AIR_END]
jump_land_frames = salto_frames[JUMP_AIR_END:JUMP_LAND_END]

# Crouch frames share one crop/scale so the crouched poses are naturally
# shorter than the standing ones.
crouch_down_files = sorted(CROUCH_DIR.glob("*.png"))[
    CROUCH_DOWN_FIRST:CROUCH_DOWN_LAST:CROUCH_DOWN_STEP]
crouch_idle_files = sorted(CROUCH_IDLE_DIR.glob("*.png"))
crouch_walk_files = sorted(CROUCH_WALK_DIR.glob("*.png"))[
    CROUCH_WALK_FIRST:CROUCH_WALK_LAST:CROUCH_WALK_STEP]
crouch_frames = process_set(crouch_down_files + crouch_idle_files +
                            crouch_walk_files)
crouch_down_frames = crouch_frames[:len(crouch_down_files)]
crouch_idle_frames = crouch_frames[
    len(crouch_down_files):len(crouch_down_files) + len(crouch_idle_files)]
crouch_walk_frames = crouch_frames[
    len(crouch_down_files) + len(crouch_idle_files):]

print(f"walk: {len(walk_frames)} frames at {walk_frames[0].size}")
print(f"idle: {len(idle_frames)} frames at {idle_frames[0].size}")
print(f"punch: {len(punch_frames)} frames at {punch_frames[0].size}")
print(f"mongo punch: {len(mongo_frames)} frames at {mongo_frames[0].size}")
print(f"kick: {len(kick_frames)} frames at {kick_frames[0].size}")
print(f"kick strong: {len(kick_strong_frames)} frames at {kick_strong_frames[0].size}")
print(f"hit: {len(hit_frames)} frames at {hit_frames[0].size}")
print(f"jump start/air/land: {len(jump_start_frames)}/{len(jump_air_frames)}/{len(jump_land_frames)} frames at {salto_frames[0].size}")
print(f"crouch down/idle/walk: {len(crouch_down_frames)}/{len(crouch_idle_frames)}/{len(crouch_walk_frames)} frames at {crouch_frames[0].size}")

frames_by_group = [
    (0, idle_frames),
    (20, walk_frames),
    (200, punch_frames),
    (220, mongo_frames),
    (230, kick_frames),
    (240, kick_strong_frames),
    (5000, hit_frames),
    (40, jump_start_frames),
    (41, jump_air_frames),
    (47, jump_land_frames),
    (8, crouch_walk_frames),
    (10, crouch_down_frames),
    (11, crouch_idle_frames),
]

table_offset = 512
sprite_count = sum(len(f) for _, f in frames_by_group)
data_offset = table_offset + sprite_count * 28
payloads = []
for _, frames in frames_by_group:
    for frame in frames:
        buffer = BytesIO()
        frame.save(buffer, format="PNG", optimize=True)
        payloads.append(b"\0\0\0\0" + buffer.getvalue())


def sprite_header(group, number, frame, payload_offset, payload_size):
    return struct.pack("<HHHHhhHBBIIHH", group, number, frame.width,
                       frame.height, frame.width // 2, frame.height, 0,
                       11, 32, payload_offset, payload_size, 0, 0)


output = bytearray(512)
output[:12] = b"ElecbyteSpr\0"
struct.pack_into("<4B", output, 12, 0, 1, 0, 2)
struct.pack_into("<I", output, 36, table_offset)
struct.pack_into("<I", output, 40, sprite_count)
current_offset = data_offset
payload_idx = 0
for group, frames in frames_by_group:
    for number, frame in enumerate(frames):
        payload = payloads[payload_idx]
        payload_idx += 1
        output.extend(sprite_header(group, number, frame, current_offset,
                                    len(payload)))
        current_offset += len(payload)
for payload in payloads:
    output.extend(payload)
OUTPUT.write_bytes(output)
print(f"Created {OUTPUT} with {sprite_count} sprites")