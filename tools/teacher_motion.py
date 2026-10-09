"""Install the cast's registered movement poses without replacing gameplay.

One standing calibration is used for each atlas. Crouches are never stretched
to standing height, and airborne tucked legs retain a virtual standing floor.
Only sprite data and non-attacking AIR actions are changed by this module.
"""
from io import BytesIO
from pathlib import Path
import argparse
import json
import re
import struct
import time

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
TEACHERS = ('chan_kof', 'felix', 'alejandro', 'daniela', 'gameros', 'armando',
            'vladimir', 'jaime', 'leonardo', 'cesar')
HEADER = '<HHHHhhHBBIIHH'


def read_sff(path):
    """Resolve linked sprites too, retaining the axes of the referring slot."""
    blob = path.read_bytes()
    offset, count = struct.unpack_from('<II', blob, 36)
    ldata = struct.unpack_from('<I', blob, 52)[0]
    tdata = struct.unpack_from('<I', blob, 60)[0]
    entries = [struct.unpack_from(HEADER, blob, offset + i * 28) for i in range(count)]
    output = {}
    for entry in entries:
        key = entry[:2]
        original = entry
        visited = set()
        while entry[10] == 0:
            assert entry[6] not in visited, ('cyclic sprite link', path, key)
            visited.add(entry[6])
            entry = entries[entry[6]]
        assert entry[7] in (10, 11, 12), (path, key, 'expected PNG', entry[7])
        start = (tdata if entry[12] & 1 else ldata) + entry[9]
        image = Image.open(BytesIO(blob[start + 4:start + entry[10]])).convert('RGBA')
        output[key] = (image, original[4], original[5])
    return output


def write_sff(path, sprites):
    """Repack PNG sprites once; discard obsolete payloads from old upserts.

RGBA PNGs contain their own colors, so no external palette records are needed.
Keeping the original SFF2 header preserves its engine version information.
"""
    original = path.read_bytes()
    assert original[:12] == b'ElecbyteSpr\x00' and original[15] == 2, path
    header = bytearray(original[:512])
    table = bytearray()
    payload = bytearray()
    for (group, index), (image, ax, ay) in sorted(sprites.items()):
        stream = BytesIO()
        image.convert('RGBA').save(stream, format='PNG')
        raw = struct.pack('<I', image.width * image.height * 4) + stream.getvalue()
        table.extend(struct.pack(HEADER, group, index, image.width, image.height,
                                 ax, ay, 0, 11, 32, len(payload), len(raw), 0, 0))
        payload.extend(raw)
    struct.pack_into('<IIIIIIII', header, 36, 512, len(sprites), 0, 0,
                     512 + len(table), len(payload), 0, 0)
    # A cloud-sync reader can briefly hold the destination on Windows. Finish
    # the new file first so an interrupted write never truncates the fighter.
    pending = path.with_name(path.name + '.tmp')
    pending.write_bytes(header + table + payload)
    for attempt in range(6):
        try:
            pending.replace(path)
            break
        except OSError as error:
            if attempt == 5 or error.errno not in (13, 16, 22):
                raise
            time.sleep(.2 * 2 ** attempt)


def extract_atlas(path, row_count, standing_height, reference=(0, 0)):
    """Extract connected bodies, never detached shadows or neighboring limbs."""
    rgba = np.array(Image.open(path).convert('RGBA'))
    height, width = rgba.shape[:2]
    _, labels, stats, centers = cv2.connectedComponentsWithStats(
        (rgba[:, :, 3] >= 110).astype(np.uint8), 8)
    figures = [i for i in range(1, len(stats)) if stats[i, 4] > 700]
    assert len(figures) == row_count * 6, (path, 'complete bodies', len(figures))
    figures.sort(key=lambda i: centers[i, 1])
    rows = [sorted(figures[r * 6:(r + 1) * 6], key=lambda i: centers[i, 0])
            for r in range(row_count)]
    component = rows[reference[0]][reference[1]]
    scale = standing_height / stats[component, 3]
    frames = []
    metrics = dict(source=path.name, standing_height=standing_height, scale=scale, rows=[])
    for row, members in enumerate(rows):
        poses, row_metrics = [], []
        for column, component in enumerate(members):
            x, y, w, h, _ = map(int, stats[component])
            assert x > 0 and y > 0 and x + w < width and y + h < height, (path, row, column, 'clipped')
            keep = cv2.dilate((labels == component).astype(np.uint8), np.ones((3, 3), np.uint8), iterations=1)
            pixels = rgba.copy()
            pixels[:, :, 3] *= keep
            box = (max(0, x - 2), max(0, y - 2), min(width, x + w + 2), min(height, y + h + 2))
            image = Image.fromarray(pixels).crop(box)
            image.putalpha(image.getchannel('A').point(lambda a: a if a >= 100 else 0))
            image = image.resize((max(1, round(image.width * scale)),
                                  max(1, round(image.height * scale))), Image.Resampling.NEAREST)
            bbox = image.getchannel('A').getbbox()
            # A per-cell origin retains physical steps/swings, without registering
            # the center of an outstretched foot as the center of the fighter.
            ax = round(((column + .5) * width / 6 - box[0]) * scale)
            ay = bbox[3]
            poses.append((image, ax, ay))
            row_metrics.append(dict(size=list(image.size), axis=[ax, ay], opaque_box=list(bbox)))
        frames.append(poses)
        metrics['rows'].append(row_metrics)
    return frames, metrics


def standing_height(sprites):
    box = sprites[0, 0][0].getchannel('A').getbbox()
    return box[3] - box[1]


def motion_sprites(root, name, existing=None):
    path = root / 'chars' / name / 'art/motion-v4/sheet.png'
    if not path.exists():
        return {}
    existing = existing or read_sff(root / 'chars' / name / f'{name}.sff')
    height = standing_height(existing)
    frames, metrics = extract_atlas(path, 4, height, reference=(2, 0))
    output = {}
    for row, poses in enumerate(frames):
        for index, pose in enumerate(poses):
            image, ax, ay = pose
            if row == 3 and index in (2, 3, 4):
                ay = image.getchannel('A').getbbox()[1] + height
            output[8900 + row, index] = (image, ax, ay)
            metrics['rows'][row][index]['axis'] = [ax, ay]
    # Keep legacy sprite slots valid for throws, common states and specials.
    for group, row in ((20, 0), (22, 0), (100, 1), (102, 1), (10, 2), (40, 3)):
        for index in range(8 if group in (20, 22, 100, 102) else 6):
            source = index % 6
            output[group, index] = output[8900 + row, source]
    (path.parent / 'registration.json').write_text(json.dumps(metrics, indent=2), encoding='utf-8')
    return output


def uniform_sprites(root, name, existing=None):
    path = root / 'chars' / name / 'art/uniform-v4/sheet.png'
    if not path.exists():
        return {}
    existing = existing or read_sff(root / 'chars' / name / f'{name}.sff')
    height = standing_height(existing)
    frames, metrics = extract_atlas(path, 5, height)
    output = {}
    for row, poses in enumerate(frames):
        group = 8770 + row if row < 4 else 8760
        for index, (image, ax, ay) in enumerate(poses):
            if row in (2, 3):
                # All six phases share the same crown height relative to the
                # fighter's air origin. The engine owns the jump trajectory.
                ay = image.getchannel('A').getbbox()[1] + height
            output[group, index] = (image, ax, ay)
            metrics['rows'][row][index]['axis'] = [ax, ay]
    (path.parent / 'registration.json').write_text(json.dumps(metrics, indent=2), encoding='utf-8')
    return output


def identity_sprites(root, name, existing=None):
    path = root / 'chars' / name / 'art/identity-v4/sheet.png'
    if not path.exists():
        return {}
    existing = existing or read_sff(root / 'chars' / name / f'{name}.sff')
    frames, metrics = extract_atlas(path, 1, standing_height(existing))
    (path.parent / 'registration.json').write_text(json.dumps(metrics, indent=2), encoding='utf-8')
    return {(8760, index): pose for index, pose in enumerate(frames[0])}


def _action(number, sequence, sprites, label):
    out = f'\n[Begin Action {number}]\n; Registered UTC motion: {label}.\n'
    for group, index, duration in sequence:
        image, ax, ay = sprites[group, index]
        box = image.getchannel('A').getbbox()
        top, bottom = box[1] - ay, box[3] - ay
        mid = top + round((bottom - top) * .55)
        out += f'Clsn2: 2\nClsn2[0] = -18,{top},18,{mid}\nClsn2[1] = -21,{mid},21,{bottom}\n'
        out += f'{group},{index}, 0,0, {duration}\n'
    return out + '\n'


def apply_air(text, name, sprites):
    if (8900, 0) not in sprites:
        return text
    from teacher_identity import IDENTITIES
    tempo = IDENTITIES[name]['tempo']
    walk_ticks, run_ticks = max(3, round(5 * tempo)), max(2, round(3 * tempo))
    plans = {
        20: ([(8900, i, walk_ticks) for i in range(6)], 'walk, complete alternating stride'),
        21: ([(8900, i, walk_ticks + 1) for i in reversed(range(6))], 'backward steps'),
        100: ([(8901, i, run_ticks) for i in range(6)], 'run, separate gait'),
        10: ([(8902, i, 3) for i in (0, 1, 2)], 'lower into crouch'),
        11: ([(8902, i, 12) for i in (2, 3)], 'crouched breathing'),
        12: ([(8902, i, 3) for i in (3, 4, 5)], 'rise from crouch'),
        6: ([(8902, 2, 4)], 'low turn'),
        40: ([(8903, 0, 3), (8903, 1, 2)], 'jump anticipation'),
        47: ([(8903, 5, 4), (8902, 4, 3), (0, 0, 2)], 'landing then stand'),
    }
    for number in (41, 42, 43):
        plans[number] = ([(8903, 2, 6), (8903, 3, -1)], 'airborne rise and apex')
    for number in (44, 45, 46):
        plans[number] = ([(8903, 3, 4), (8903, 4, -1)], 'airborne descent')
    for number in (121, 141, 151):
        plans[number] = ([(8902, 2, 4)], 'crouching guard')
    plans[131] = ([(8902, 2, -1)], 'hold crouching guard')
    for number in (122, 142, 152):
        plans[number] = ([(8903, 2, 4)], 'air guard')
    plans[132] = ([(8903, 2, -1)], 'hold air guard')
    for number, (sequence, label) in plans.items():
        block = _action(number, sequence, sprites, label)
        pattern = rf'(?ims)^\[Begin Action {number}\].*?(?=^\[Begin Action |\Z)'
        text = re.sub(pattern, lambda _: block.lstrip(), text) if re.search(pattern, text) else text.rstrip() + '\n' + block
    return text.rstrip() + '\n'


def register_grounded(sprites, text):
    """Put the visible supporting foot on the floor in grounded actions.

    Some original imports used a row's shared bottom, leaving individual poses
    two pixels above/below the stage. Axes, rather than body scale, fix that.
    Airborne, knockback and companion sprites retain their own origins.
    """
    grounded = {0, 5, 6, 10, 11, 12, 20, 21, 100, 120, 121, 130, 131,
                140, 141, 150, 151, 170, 180, 181, 190,
                200, 210, 230, 240, 400, 410, 430, 440,
                5000, 5001, 5002, 5005, 5006, 5007,
                5010, 5011, 5012, 5015, 5016, 5017,
                5020, 5021, 5022, 5025, 5026, 5027,
                5110, 5111, 5112, 5120, 5121, 5122, 5150, 5151, 5152}
    for match in re.finditer(r'(?ims)^\[Begin Action (\d+)\].*?(?=^\[Begin Action |\Z)', text):
        if int(match[1]) not in grounded:
            continue
        for frame in re.finditer(r'(?m)^\s*(\d+)\s*,\s*(\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,', match[0]):
            key = int(frame[1]), int(frame[2])
            if key not in sprites:
                continue
            image, ax, ay = sprites[key]
            box = image.getchannel('A').point(lambda a: 255 if a >= 100 else 0).getbbox()
            sprites[key] = image, ax, box[3] + int(frame[4])
    return sprites


def finish_getup(text, name):
    # Hector's last original recovery pose still bends both knees. Retain it,
    # then show the existing full standing pose before common states restore
    # control. No body is rescaled just to make that bent pose taller.
    if name != 'hector':
        return text
    pattern = r'(?ims)^\[Begin Action 5120\].*?(?=^\[Begin Action |\Z)'
    def ending(match):
        block = match[0]
        if '; UTC full standing recovery' not in block:
            block = block.rstrip() + '\n; UTC full standing recovery\n0,0, 0,0, 3\n\n'
        return block
    return re.sub(pattern, ending, text)


def install(name):
    folder = ROOT / 'chars' / name
    path = folder / f'{name}.sff'
    sprites = read_sff(path)
    from teacher_reactions import legacy_reaction_sprites
    sprites.update(legacy_reaction_sprites(ROOT, name, sprites))
    sprites.update(motion_sprites(ROOT, name, sprites))
    sprites.update(uniform_sprites(ROOT, name, sprites))
    sprites.update(identity_sprites(ROOT, name, sprites))
    # Use a genuinely crouched source pose for the first/last low-normal
    # frames. Old atlases sometimes returned to a standing guard mid-crouch.
    if (8902, 2) in sprites:
        for index in (0, 5):
            sprites[8771, index] = sprites[8902, 2]
        sprites[5000, 4] = sprites[8902, 2]
    air = folder / f'{name}.air'
    text = finish_getup(apply_air(air.read_text(encoding='utf-8'), name, sprites), name)
    write_sff(path, register_grounded(sprites, text))
    air.write_text(text, encoding='utf-8')
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('characters', nargs='*')
    args = parser.parse_args()
    for name in args.characters or TEACHERS:
        install(name)
        print(name, 'registered motion and body-consistent poses')
