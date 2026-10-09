"""Build Félix from Chava's tested KOF controls and original Félix sprite sheets.

The common controls come from Chava. When themed special art is available,
build_teacher_specials installs the character's own moves after base packing.
"""
from io import BytesIO
from pathlib import Path
import json
import re
import shutil
import struct
import cv2
import numpy as np
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'chars/chava'
TARGET = ROOT / 'chars/felix'
ART = TARGET / 'art'
SHEETS = [ART / 'felix-idle-walk-punch-uppercut.png',
          ART / 'felix-kick-sweep-jump-guard.png']
HEADER = '<HHHHhhHBBIIHH'


def reaction_sprites(root, name, existing=None):
    """Register articulated hit/fall/get-up poses without changing gameplay.

    Chan and Felix originally used standing guard frames for the entire hit
    animation range, including the indefinitely held floor/KO sprite. Their
    third atlas contains real floor silhouettes and a complete recovery.
    One standing calibration is shared by all 24 poses; low or horizontal
    bodies are never stretched back to the height of a standing fighter.
    """
    from teacher_motion import extract_atlas, read_sff, standing_height
    path = root / 'chars' / name / 'art/reactions-v4/sheet.png'
    if not path.exists():
        return {}
    existing = existing or read_sff(root / 'chars' / name / f'{name}.sff')
    height = standing_height(existing)
    rows, metrics = extract_atlas(path, 4, height)
    frames = {}
    for row, poses in enumerate(rows):
        for index, (image, ax, ay) in enumerate(poses):
            if row == 1 and index < 3 or row == 3 and index in (2, 3):
                # Common fall states move the character origin. Keep the
                # airborne center of mass above that origin; floor poses use
                # their actual bottom edge, so they lie on the stage surface.
                box = image.getchannel('A').getbbox()
                ay = round((box[1] + box[3]) / 2 + height * .42)
            frames[8910 + row, index] = (image, ax, ay)
    for index, source in enumerate((1, 2, 2, 3, 4, 5)):
        frames[5000, index] = frames[8910, source]
    for index, source in enumerate((0, 1, 2, 3, 5, 4)):
        frames[5050, index] = frames[8911, source]
    for index in range(6):
        frames[5120, index] = frames[8912, index]
    metrics['families'] = {'8910': 'hit and dizzy', '8911': 'fall and impact',
                           '8912': 'get up', '8913': 'defense and KO'}
    metrics['registered'] = {f'{g},{n}': {'size': list(image.size), 'axis': [ax, ay]}
                             for (g, n), (image, ax, ay) in frames.items()}
    (path.parent / 'registration.json').write_text(json.dumps(metrics, indent=2), encoding='utf-8')
    return frames


def reaction_air(text, name, frames):
    """Replace only common reaction actions, retaining standard state IDs."""
    if (8910, 0) not in frames:
        return text

    def action(number, sequence, label):
        out = f'[Begin Action {number}]\n; UTC articulated reaction: {label}.\n'
        for group, index, ticks in sequence:
            image, ax, ay = frames[group, index]
            x0, y0, x1, y1 = image.getchannel('A').getbbox()
            out += f'Clsn2: 1\nClsn2[0] = {x0-ax},{y0-ay},{x1-ax},{y1-ay}\n'
            out += f'{group},{index}, 0,0, {ticks}\n'
        return out + '\n'

    plans = {}
    idle_box = frames[0, 0][0].getchannel('A').point(lambda a: 255 if a >= 100 else 0).getbbox()
    idle_height = idle_box[3] - idle_box[1]
    recovery_finish = ([(0, 0, 3)] if
                       frames[8912, 5][0].getchannel('A').point(
                           lambda a: 255 if a >= 100 else 0).getbbox()[3] < idle_height * .95 else [])
    for strength in range(3):
        plans[5000 + strength] = ([(8910, 1 if strength == 0 else 2, 4)], 'standing head hit')
        plans[5005 + strength] = ([(8910, 1, 5), (0, 1, 4)], 'standing head recovery')
        plans[5010 + strength] = ([(8910, 3, 5)], 'standing body hit')
        plans[5015 + strength] = ([(8910, 3, 4), (0, 1, 4)], 'standing body recovery')
        plans[5020 + strength] = ([(8910, 4, 5)], 'crouching hit')
        plans[5025 + strength] = ([(8910, 4, 4), (8913, 1, 4)], 'crouching hit recovery')
        plans[5050 + strength] = ([(8911, 0, 5), (8911, 1, 5), (8911, 2, -1)], 'backward knockdown')
        plans[5060 + strength] = ([(8911, 1, 4), (8911, 2, -1)], 'horizontal falling')
        plans[5100 + strength] = ([(8911, 3, 2), (8911, 4, 2), (8911, 5, 3)], 'ground impact then settle')
        plans[5110 + strength] = ([(8911, 5, -1)], 'lying on the floor')
        plans[5120 + strength] = ([(8912, i, t) for i, t in enumerate((5, 5, 5, 5, 4, 3))] + recovery_finish,
                                   'lying, roll, sit, kneel, rise, stand')
        plans[5150 + strength] = ([(8913, 4, -1)], 'defeated on back')
        plans[5160 + strength] = ([(8911, 4, 5)], 'floor bounce')
        plans[5170 + strength] = ([(8911, 3, 2), (8911, 4, 2), (8911, 5, 3)], 'second impact')
    plans.update({
        5030: ([(8913, 3, 5)], 'air hit recoil'),
        5035: ([(8911, 1, 5)], 'air hit transition'),
        5040: ([(8911, 0, 4), (8911, 1, -1)], 'air hit into fall'),
        5070: ([(8911, 0, 4), (8911, 1, -1)], 'fall transition'),
        5080: ([(8911, 5, 4)], 'trip on floor'),
        5090: ([(8911, 0, 5)], 'trip airborne'),
        5140: ([(8913, 5, -1)], 'defeated on side'),
        5200: ([(8913, 3, 4), (8913, 2, 4), (40, 3, 4)], 'recover guard in the air'),
        5300: ([(8910, 5, 12), (8910, 3, 12), (8910, 5, 12)], 'dizzy, unsteady guard'),
    })
    for number in (120, 140, 150):
        plans[number] = ([(8913, 0, 4)], 'standing guard')
    plans[130] = ([(8913, 0, -1)], 'hold standing guard')
    for number in (121, 141, 151):
        plans[number] = ([(8913, 1, 4)], 'crouching guard')
    plans[131] = ([(8913, 1, -1)], 'hold crouching guard')
    for number in (122, 142, 152):
        plans[number] = ([(8913, 2, 4)], 'air guard')
    plans[132] = ([(8913, 2, -1)], 'hold air guard')
    for number, (sequence, label) in plans.items():
        block = action(number, sequence, label)
        pattern = rf'(?ims)^\[Begin Action {number}\].*?(?=^\[Begin Action |\Z)'
        text = re.sub(pattern, lambda _: block, text) if re.search(pattern, text) else text.rstrip() + '\n\n' + block
    return text.rstrip() + '\n'


def install_reactions(name='felix'):
    """Apply just reaction art to an existing fighter, keeping its moves intact."""
    from teacher_motion import read_sff, write_sff
    folder = ROOT / 'chars' / name
    path = folder / f'{name}.sff'
    frames = read_sff(path)
    reaction = reaction_sprites(ROOT, name, frames)
    if not reaction:
        return False
    frames.update(reaction)
    write_sff(path, frames)
    air = folder / f'{name}.air'
    air.write_text(reaction_air(air.read_text(encoding='utf-8'), name, frames), encoding='utf-8')
    return True


def load_frames():
    frames = []
    for path in SHEETS:
        sheet = Image.open(path).convert('RGBA')
        assert sheet.size == (1536, 1024), path
        sheet_frames = []
        for row in range(4):
            poses = []
            for column in range(6):
                # Long kicks can cross the nominal cell boundary. Include
                # that extension and isolate the figure's connected silhouette.
                right = min(sheet.width, (column + 1) * 256 + 80)
                cell = sheet.crop((column * 256, row * 256, right, (row + 1) * 256))
                alpha = np.asarray(cell.getchannel('A'))
                count, labels, stats, centers = cv2.connectedComponentsWithStats(
                    (alpha >= 110).astype(np.uint8), 8)
                choices = [i for i in range(1, count) if stats[i, cv2.CC_STAT_AREA] > 300]
                assert choices, (path, row, column)
                component = min(choices, key=lambda i: abs(centers[i, 0] - 120))
                silhouette = cv2.dilate((labels == component).astype(np.uint8),
                                         np.ones((3, 3), np.uint8), iterations=2)
                rgba = np.array(cell)
                rgba[:, :, 3] *= silhouette
                cell = Image.fromarray(rgba, 'RGBA')
                box = cell.getchannel('A').getbbox()
                assert box, (path, row, column)
                # Remove very faint antialiasing from the transparent edges.
                body = cell.crop(box)
                body.putalpha(body.getchannel('A').point(lambda a: a if a >= 40 else 0))
                body = body.resize((round(body.width * .45), round(body.height * .45)),
                                   Image.Resampling.NEAREST)
                axis_x = round((112 - box[0]) * .45)
                axis_y = round((250 - box[1]) * .45)
                poses.append((body, axis_x, axis_y))
                body.save(ART / f'pose-{len(frames)}-{row}-{column}.png')
            sheet_frames.append(poses)
        frames.append(sheet_frames)
    return frames


def pose_for(group, item, frames, portraits):
    # Group and item stay fixed so all existing AIR action timings, CLSN and
    # CNS references remain valid. Sheet 0: idle/walk/punch/uppercut.
    # Sheet 1: kick/sweep/jump/guard and reactions.
    def pick(sheet, row, frame):
        return frames[sheet][row][frame % 6]
    if group == 0:
        return pick(0, 0, item)
    if group == 10:
        return pick(1, 1, 0)  # Crouch stays crouched; no standing uppercut frames.
    if group in {20, 22, 100, 102}:
        return pick(0, 1, item)
    if group == 40:
        return pick(1, 2, item)
    if group in {120, 181}:
        return pick(1, 3, item)
    if group in {200, 201, 210, 211, 230, 400, 401, 410, 600, 601, 610}:
        return pick(0, 2 if group not in {400, 401, 410} else 3, item)
    if group in {240, 630, 640}:
        return pick(1, 0, item)
    if group in {430, 440}:
        return pick(1, 1, item)
    if group == 3000:
        return pick(0, 3, item)
    if 5000 <= group <= 5200:
        return pick(1, 3, item)
    if group == 9000:
        return portraits[item], 0, 0
    return None  # Preserve technology effects, projectiles and interface art.


def replace_sff(original, frames, portraits, pose_picker=None, extra_poses=None):
    data = bytearray(original)
    table_offset, count = struct.unpack_from('<II', data, 36)
    ldata = struct.unpack_from('<I', data, 52)[0]
    table = bytearray(data[table_offset:table_offset + count * 28])
    extra_poses = extra_poses or {}
    for group, item in extra_poses:
        assert not any(struct.unpack_from('<HH', table, i * 28) == (group, item)
                       for i in range(count)), (group, item)
        table.extend(struct.pack(HEADER, group, item, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
        count += 1
    payload = bytearray()
    new_table_offset = len(data)
    new_data_start = new_table_offset + len(table)
    changed = 0
    for index in range(count):
        offset = index * 28
        group, item = struct.unpack_from('<HH', table, offset)
        pose = extra_poses.get((group, item))
        if pose is None:
            pose = (pose_picker or pose_for)(group, item, frames, portraits)
        if pose is None:
            continue
        art, axis_x, axis_y = pose
        stream = BytesIO()
        art.save(stream, format='PNG')
        raw = struct.pack('<I', art.width * art.height * 4) + stream.getvalue()
        record = struct.pack(HEADER, group, item, art.width, art.height,
                             axis_x, axis_y, 0, 11, 32,
                             new_data_start + len(payload) - ldata,
                             len(raw), 0, 0)
        table[offset:offset + 28] = record
        payload.extend(raw)
        changed += 1
    struct.pack_into('<II', data, 36, new_table_offset, count)
    struct.pack_into('<I', data, 56, new_data_start + len(payload) - ldata)
    assert changed >= 170, changed
    return data + table + payload, changed


def main():
    ART.mkdir(parents=True, exist_ok=True)
    assert all(path.is_file() for path in SHEETS)
    for name in ('chava.cmd', 'chava.cns', 'chava.air', 'chava.snd',
                 'kof-extra.cns', 'chava-movelist.dat'):
        destination = name.replace('chava', 'felix')
        shutil.copy2(SOURCE / name, TARGET / destination)
    move_list = TARGET / 'felix-movelist.dat'
    descriptions = move_list.read_text(encoding='utf-8')
    for old, new in {
        'CHAVA / CONTROLES KOF': 'FÉLIX / SOPORTE KOF',
        'Codigo compilado': 'Diagnostico rapido',
        'Codigo, alternativa U': 'Diagnostico alternativo',
        'Gancho compilacion': 'Reinicio forzado',
        'Mochilazo de avance': 'Entrada de soporte',
        'Barrida de semestre': 'Barrida de cables',
        'Asistente IA': 'Asistente de soporte',
        'Entrega final': 'Reparacion final',
        'Compilacion final + IA': 'Soporte de emergencia',
    }.items():
        descriptions = descriptions.replace(old, new)
    move_list.write_text(descriptions, encoding='utf-8')
    definition = (SOURCE / 'chava.def').read_text(encoding='utf-8')
    # The fight font omits É, so use the unaccented display name in combat.
    definition = definition.replace('Chava', 'Felix').replace('CHAVA', 'FELIX')
    definition = definition.replace('protagonista de Ingenieria en Sistemas', 'profesor de Soporte')
    definition = definition.replace('chava.', 'felix.').replace('chava-', 'felix-')
    (TARGET / 'felix.def').write_text(definition, encoding='utf-8')
    frames = load_frames()
    design = Image.open(ROOT / 'data/story/portraits/felix_soporte.jpeg').convert('RGBA')
    face = design.crop((225, 125, 455, 415))
    portraits = {0: ImageOps.fit(face, (24, 24), method=Image.Resampling.LANCZOS),
                 1: ImageOps.fit(face, (120, 140), method=Image.Resampling.LANCZOS)}
    sff, changed = replace_sff((SOURCE / 'chava.sff').read_bytes(), frames, portraits)
    (TARGET / 'felix.sff').write_bytes(sff)
    (ART / 'manifest.json').write_text(json.dumps({
        'design_reference': 'felix_soporte.jpeg',
        'sheets': [path.name for path in SHEETS],
        'poses': 48, 'sprite_slots_replaced': changed,
        'gameplay_reference': 'Chava KOF controls',
        'limitations': 'Specials and voice still reuse Chava placeholders; falling and victory reuse nearest poses.'
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Félix: 48 poses, {changed} fighter sprite slots replaced')
    from build_teacher_specials import apply_character
    apply_character('felix')


if __name__ == '__main__':
    main()
