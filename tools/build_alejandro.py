"""Build Alejandro's original animation set with the current UTC KOF controls."""
from pathlib import Path
import json
import re
import shutil
import cv2
import numpy as np
from PIL import Image, ImageOps
import build_felix as sprites

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'chars/chava'
TARGET = ROOT / 'chars/alejandro'
ART = TARGET / 'art'
SHEETS = [ART / 'alejandro-idle-walk-punch-uppercut.png',
          ART / 'alejandro-kick-sweep-jump-guard.png',
          ART / 'alejandro-intro-fall-getup-win.png']


def load_frames():
    """Register whole connected figures, including limbs crossing grid lines."""
    frames = []
    for sheet_number, path in enumerate(SHEETS):
        sheet = np.array(Image.open(path).convert('RGBA'))
        assert sheet.shape[:2] == (1024, 1536), path
        count, labels, stats, centers = cv2.connectedComponentsWithStats(
            (sheet[:, :, 3] >= 110).astype(np.uint8), 8)
        figures = [i for i in range(1, count) if stats[i, cv2.CC_STAT_AREA] > 1000]
        assert len(figures) == 24, (path, len(figures))
        figures.sort(key=lambda i: centers[i, 1])
        first_row=sorted(figures[:6],key=lambda i:centers[i,0])
        reference=first_row[1 if sheet_number==2 else 0]
        sheet_scale=102/stats[reference,3]
        rows = []
        for row in range(4):
            members = sorted(figures[row * 6:(row + 1) * 6], key=lambda i: centers[i, 0])
            baseline = max(int(stats[i, 1] + stats[i, 3]) for i in members)
            poses = []
            for column, component in enumerate(members):
                mask = cv2.dilate((labels == component).astype(np.uint8),
                                  np.ones((3, 3), np.uint8), iterations=2)
                rgba = sheet.copy()
                rgba[:, :, 3] *= mask
                image = Image.fromarray(rgba, 'RGBA')
                box = image.getbbox()
                assert box
                body = image.crop(box)
                body.putalpha(body.getchannel('A').point(lambda a: a if a >= 40 else 0))
                scale = sheet_scale
                body = body.resize((round(body.width * scale), round(body.height * scale)),
                                   Image.Resampling.NEAREST)
                ax = round((column * 256 + (144 if sheet_number == 2 else 128) - box[0]) * scale)
                ay = round((baseline - box[1]) * scale)
                poses.append((body, ax, ay))
                body.save(ART / f'pose-{sheet_number}-{row}-{column}.png')
            rows.append(poses)
        frames.append(rows)
    return frames


def pose_for(group, item, frames, portraits):
    if group == 181:
        return frames[2][3][min(item, 5)]
    if group == 5050:
        return frames[2][1][min(item, 5)]
    if group == 5120:
        return frames[2][2][min(item, 5)]
    if group == 5200:
        return frames[2][2][3]
    if 5000 <= group <= 5040:
        return frames[1][3][3 + item % 3]
    if group == 10:
        return [frames[0][0][0], frames[1][1][0], frames[1][1][0],
                frames[1][1][5], frames[1][1][0], frames[0][0][0]][min(item, 5)]
    if group in {230, 240}:
        return frames[1][0][item % 6]
    return sprites.pose_for(group, item, frames, portraits)


def main():
    ART.mkdir(parents=True, exist_ok=True)
    assert all(path.is_file() for path in SHEETS)
    for name in ('chava.cmd', 'chava.cns', 'chava.air', 'chava.snd',
                 'kof-extra.cns', 'chava-movelist.dat'):
        shutil.copy2(SOURCE / name, TARGET / name.replace('chava', 'alejandro'))
    definition = (SOURCE / 'chava.def').read_text(encoding='utf-8')
    definition = definition.replace('Chava', 'Alejandro').replace('CHAVA', 'ALEJANDRO')
    definition = definition.replace('protagonista de Ingenieria en Sistemas', 'profesor de Angular')
    definition = definition.replace('chava.', 'alejandro.').replace('chava-', 'alejandro-')
    (TARGET / 'alejandro.def').write_text(definition, encoding='utf-8')
    move_list = TARGET / 'alejandro-movelist.dat'
    descriptions = move_list.read_text(encoding='utf-8')
    for old, new in {
        'CHAVA / CONTROLES KOF': 'ALEJANDRO / ANGULAR KOF',
        'Codigo compilado': 'Componente directo',
        'Codigo, alternativa U': 'Componente alternativo',
        'Gancho compilacion': 'Gancho de compilacion',
        'Mochilazo de avance': 'Inyeccion de dependencia',
        'Barrida de semestre': 'Barrida de errores',
        'Asistente IA': 'Servicio automatizado',
        'Entrega final': 'Proyecto en produccion',
        'Compilacion final + IA': 'Compilacion de emergencia',
    }.items():
        descriptions = descriptions.replace(old, new)
    move_list.write_text(descriptions, encoding='utf-8')
    frames = load_frames()
    design = Image.open(ROOT / 'data/story/portraits/alejandro_angular.jpeg').convert('RGBA')
    face = design.crop((345, 5, 635, 320))
    portraits = {0: ImageOps.fit(face, (24, 24), method=Image.Resampling.LANCZOS),
                 1: ImageOps.fit(face, (120, 140), method=Image.Resampling.LANCZOS)}
    extra = {(8100, i): frames[2][0][i] for i in range(6)}
    result, changed = sprites.replace_sff((SOURCE / 'chava.sff').read_bytes(),
                                          frames, portraits, pose_for, extra)
    (TARGET / 'alejandro.sff').write_bytes(result)
    # The introduction keeps its original 36 ticks and collision boxes.
    animation = TARGET / 'alejandro.air'
    text = animation.read_text(encoding='utf-8')
    block = re.search(r'(?ims)^\[Begin Action 190\].*?(?=^\[Begin Action |\Z)', text)
    intro = re.sub(r'(?m)^\s*\d+\s*,\s*\d+\s*,[^\n]*\n', '', block[0])
    intro += ''.join(f'8100,{i}, 0,0, 6\n' for i in range(6)) + '\n'
    text = text[:block.start()] + intro + text[block.end():]
    animation.write_text(text, encoding='utf-8')
    (ART / 'manifest.json').write_text(json.dumps({
        'reference': 'alejandro_angular.jpeg', 'poses': 72,
        'sheets': [p.name for p in SHEETS], 'sprite_slots_replaced': changed,
        'gameplay_reference': 'UTC KOF controls (Chava)',
        'dedicated_animations': ['intro', 'fall', 'getup', 'victory'],
        'limitations': 'Special effects, sound and attack logic still share UTC prototype resources.'
    }, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'Alejandro: 72 poses, {changed} sprite slots, introduction/fall/getup/victory')
    from build_teacher_specials import apply_character
    apply_character('alejandro')


if __name__ == '__main__':
    main()
