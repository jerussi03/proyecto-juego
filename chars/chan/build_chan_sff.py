from io import BytesIO
from pathlib import Path
import struct
from PIL import Image

ROOT = Path(__file__).parent
WALK_DIR = ROOT / "caminar"
IDLE_DIR = ROOT / "estaticochan"
PUNCH_DIR = ROOT / "golpeMySQL"
OUTPUT = ROOT / "chan.sff"

# The punch clip is 192 frames, but only frames 1..121 contain the actual
# punch motion (the rest is a static rest pose). Subsample every 4th frame so
# the punch lasts a playable amount of time (~31 frames) instead of 3+ seconds.
PUNCH_FIRST, PUNCH_LAST, PUNCH_STEP = 0, 121, 4

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
    content_h = y1 - y0
    scale = TARGET_CONTENT_H / content_h
    frames = []
    for im in images:
        im = im.crop((x0, y0, x1, y1))
        w = max(1, round(im.width * scale))
        im = im.resize((w, TARGET_CONTENT_H), Image.LANCZOS)
        frames.append(im)
    return frames


walk_frames = process_set(sorted(WALK_DIR.glob("*.png")))
idle_frames = process_set(sorted(IDLE_DIR.glob("*.png")))
punch_files = sorted(PUNCH_DIR.glob("*.png"))[PUNCH_FIRST:PUNCH_LAST:PUNCH_STEP]
punch_frames = process_set(punch_files)
print(f"walk: {len(walk_frames)} frames at {walk_frames[0].size}")
print(f"idle: {len(idle_frames)} frames at {idle_frames[0].size}")
print(f"punch: {len(punch_frames)} frames at {punch_frames[0].size}")

table_offset = 512
sprite_count = len(idle_frames) + len(walk_frames) + len(punch_frames)
data_offset = table_offset + sprite_count * 28
payloads = []
for frame in idle_frames + walk_frames + punch_frames:
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
for number, (frame, payload) in enumerate(zip(idle_frames, payloads)):
    output.extend(sprite_header(0, number, frame, current_offset, len(payload)))
    current_offset += len(payload)
for number, (frame, payload) in enumerate(
        zip(walk_frames, payloads[len(idle_frames):len(idle_frames) + len(walk_frames)])):
    output.extend(sprite_header(20, number, frame, current_offset, len(payload)))
    current_offset += len(payload)
for number, (frame, payload) in enumerate(
        zip(punch_frames, payloads[len(idle_frames) + len(walk_frames):])):
    output.extend(sprite_header(200, number, frame, current_offset, len(payload)))
    current_offset += len(payload)
for payload in payloads:
    output.extend(payload)
OUTPUT.write_bytes(output)
print(f"Created {OUTPUT} with {sprite_count} sprites")