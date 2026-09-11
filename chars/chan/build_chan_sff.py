from io import BytesIO
from pathlib import Path
import struct
from PIL import Image

ROOT = Path(__file__).parent
FRAME_DIR = ROOT / "caminar"
OUTPUT = ROOT / "chan.sff"

# The source frames are 720x1280 with the character content roughly in
# (0,116)-(720,1164). Crop to a fixed box so every frame is anchored the
# same way, then resize so the character matches the other cast members
# (~105 px tall, like Chava/Hector).
CROP = (0, 110, 720, 1165)
TARGET_HEIGHT = 105


def clean_frame(path):
    im = Image.open(path).convert("RGBA")
    im = im.crop(CROP)
    width, height = im.size
    target_width = max(1, round(width * TARGET_HEIGHT / height))
    return im.resize((target_width, TARGET_HEIGHT), Image.LANCZOS)


frames = [clean_frame(path) for path in sorted(FRAME_DIR.glob("*.png"))]
if len(frames) != 31:
    raise SystemExit(f"Expected 31 transparent frames, found {len(frames)}")
print(f"Processed {len(frames)} frames at {frames[0].size[0]}x{frames[0].size[1]}")

table_offset = 512
sprite_count = len(frames) + 1
data_offset = table_offset + sprite_count * 28
payloads = []
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
output.extend(sprite_header(0, 0, frames[0], current_offset, len(payloads[0])))
current_offset += len(payloads[0])
for number, (frame, payload) in enumerate(zip(frames, payloads)):
    output.extend(sprite_header(20, number, frame, current_offset, len(payload)))
    current_offset += len(payload)
output.extend(payloads[0])
for payload in payloads:
    output.extend(payload)
OUTPUT.write_bytes(output)
print(f"Created {OUTPUT} with {len(frames)} walking frames")