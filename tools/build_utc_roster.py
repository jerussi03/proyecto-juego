"""Pack original 72-pose teacher sheets using the existing UTC KOF controls.

Image creation is done with ImageGen. This script only extracts sprite cells,
registers axes, writes the engine archive and connects animation references.
"""
from pathlib import Path
import argparse
import json
import re
import shutil
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageOps
import build_felix as sprites
import build_alejandro as animations

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'chars/chava'
ROSTER = json.loads((ROOT / 'data/utc-roster.json').read_text(encoding='utf-8'))
SHEETS = ['basics.png', 'combat.png', 'reactions.png']
OLD_MOVES = ['Codigo compilado', 'Codigo, alternativa U', 'Gancho compilacion',
             'Mochilazo de avance', 'Barrida de semestre', 'Asistente IA',
             'Entrega final', 'Compilacion final + IA']


def extract(path, sheet_index, output, fixed_scale=None):
    sheet = np.array(Image.open(path).convert('RGBA'))
    height, width = sheet.shape[:2]
    count, labels, stats, centers = cv2.connectedComponentsWithStats(
        (sheet[:, :, 3] >= 110).astype(np.uint8), 8)
    candidates = [i for i in range(1, count) if stats[i, cv2.CC_STAT_AREA] > 1000]
    assert len(candidates) == 24, (path, 'expected 24 separate figures', len(candidates))
    candidates.sort(key=lambda i: centers[i, 1])
    rows = []
    # One standing calibration for the entire sheet. Never stretch a crouch or
    # a tucked jump to standing height, or shrink a raised arm back to 102px.
    first_row=sorted(candidates[:6],key=lambda i:centers[i,0])
    reference=first_row[1 if sheet_index==2 else 0]
    sheet_scale=fixed_scale or 102/stats[reference,3]
    for row in range(4):
        members = sorted(candidates[row * 6:row * 6 + 6], key=lambda i: centers[i, 0])
        heights = [stats[i, 3] for i in members]
        scale = sheet_scale
        baseline = max(int(stats[i, 1] + stats[i, 3]) for i in members)
        poses = []
        for column, component in enumerate(members):
            mask = cv2.dilate((labels == component).astype(np.uint8),
                             np.ones((3, 3), np.uint8), iterations=2)
            rgba = sheet.copy()
            rgba[:, :, 3] *= mask
            image = Image.fromarray(rgba, 'RGBA')
            box = image.getbbox()
            assert box, (path, row, column)
            body = image.crop(box)
            body.putalpha(body.getchannel('A').point(lambda a: a if a >= 40 else 0))
            body = body.resize((round(body.width * scale), round(body.height * scale)),
                               Image.Resampling.NEAREST)
            ax = round(((column + .5) * width / 6 - box[0]) * scale)
            foot = baseline if sheet_index == 1 and row == 2 else stats[component, 1] + stats[component, 3]
            ay = round((foot - box[1]) * scale)
            poses.append((body, ax, ay))
            body.save(output / f'pose-{sheet_index}-{row}-{column}.png')
        rows.append(poses)
    return rows


def preview(frames, destination):
    image = Image.new('RGB', (1080, 1440), (26, 35, 43))
    draw = ImageDraw.Draw(image)
    names = ['Idle', 'Walk', 'Punch', 'Uppercut', 'Kick', 'Sweep', 'Jump',
             'Guard / hit', 'Introduction', 'Fall', 'Get up', 'Victory']
    for sheet, rows in enumerate(frames):
        for row, poses in enumerate(rows):
            y = (sheet * 4 + row) * 120
            for col, (body, ax, ay) in enumerate(poses):
                x = col * 180
                draw.line((x, y + 110, x + 179, y + 110), fill=(65, 95, 105))
                image.paste(body, (x + 80 - ax, y + 110 - ay), body)
                draw.text((x + 3, y + 2), names[sheet * 4 + row] + ' ' + str(col + 1), fill='white')
    image.save(destination)


def teacher_pose(group, item, frames, portraits):
    if group == 120:
        return frames[1][3][item % 3]
    if group == 5050:
        # MUGEN sprite 5050,4 is the resting KO pose, so use the flat frame.
        return frames[2][1][[0, 1, 2, 3, 5, 4][min(item, 5)]]
    return animations.pose_for(group, item, frames, portraits)


def build(spec):
    name = spec['id']
    target = ROOT / 'chars' / name
    art = target / 'art'
    assert all((art / file).is_file() for file in SHEETS), name
    frames = [extract(art / file, i, art) for i, file in enumerate(SHEETS)]
    for file in ('chava.cmd', 'chava.cns', 'chava.air', 'chava.snd',
                 'kof-extra.cns', 'chava-movelist.dat'):
        shutil.copy2(SOURCE / file, target / file.replace('chava', name))
    definition = (SOURCE / 'chava.def').read_text(encoding='utf-8')
    definition = definition.replace('Chava', spec['name']).replace('CHAVA', spec['name'].upper())
    definition = definition.replace('protagonista de Ingenieria en Sistemas', spec['subject'])
    definition = definition.replace('chava.', name + '.').replace('chava-', name + '-')
    (target / (name + '.def')).write_text(definition, encoding='utf-8')
    moves = target / (name + '-movelist.dat')
    text = moves.read_text(encoding='utf-8').replace('CHAVA / CONTROLES KOF', spec['name'].upper() + ' / CONTROLES KOF')
    for old, new in zip(OLD_MOVES, spec['moves']):
        text = text.replace(old, new)
    moves.write_text(text, encoding='utf-8')
    reference = Image.open(ROOT / 'data/story/portraits' / spec['reference']).convert('RGBA')
    face = reference.crop(spec['face'])
    portraits = {0: ImageOps.fit(face, (24, 24), method=Image.Resampling.LANCZOS),
                 1: ImageOps.fit(face, (120, 140), method=Image.Resampling.LANCZOS)}
    extra = {(8100, i): frames[2][0][i] for i in range(6)}
    if name == 'daniela':
        victor_dir = art / 'victor'
        victor_dir.mkdir(exist_ok=True)
        victor = extract(art / 'victor-desk.png', 0, victor_dir, fixed_scale=.32)
        extra.update({(8200 + row, i): victor[row][i] for row in range(4) for i in range(6)})
    result, changed = sprites.replace_sff((SOURCE / 'chava.sff').read_bytes(),
                                          frames, portraits, teacher_pose, extra)
    (target / (name + '.sff')).write_bytes(result)
    air = target / (name + '.air')
    text = air.read_text(encoding='utf-8')
    block = re.search(r'(?ims)^\[Begin Action 190\].*?(?=^\[Begin Action |\Z)', text)
    intro = re.sub(r'(?m)^\s*\d+\s*,\s*\d+\s*,[^\n]*\n', '', block[0])
    intro += ''.join(f'8100,{i}, 0,0, 6\n' for i in range(6)) + '\n'
    air.write_text(text[:block.start()] + intro + text[block.end():], encoding='utf-8')
    if name == 'daniela':
        with air.open('a', encoding='utf-8') as out:
            out.write('\n; Victor: background companion, no collision boxes.\n[Begin Action 8200]\n')
            out.write(''.join(f'8200,{i}, 0,0, 6\n' for i in range(6)))
            out.write('\n[Begin Action 8201]\n')
            for group, ticks in [(8201, 20), (8203, 25), (8202, 24), (8201, 20)]:
                out.write(''.join(f'{group},{i}, 0,0, {ticks}\n' for i in range(6)))
        cns = target / (name + '.cns')
        with cns.open('a', encoding='utf-8') as out:
            out.write((ROOT / 'tools/victor-companion.cns').read_text(encoding='utf-8'))
    preview(frames, art / 'preview.png')
    (art / 'manifest.json').write_text(json.dumps({
        'reference': spec['reference'], 'poses': 72, 'sheets': SHEETS,
        'sprite_slots_replaced': changed, 'dedicated_animations': ['intro', 'fall', 'getup', 'victory'],
        'gameplay_reference': 'UTC KOF controls (Chava)',
        'limitations': 'Special effect sprites, sound and attack logic share UTC prototype resources.'
    }, indent=2, ensure_ascii=False), encoding='utf-8')
    print(name, '72 poses;', changed, 'sprite slots')
    from build_teacher_specials import apply_character
    apply_character(name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('characters', nargs='*')
    parser.add_argument('--import-sheets', type=Path)
    args = parser.parse_args()
    if args.import_sheets:
        jobs = json.loads(args.import_sheets.read_text(encoding='utf-8'))
        for job in jobs:
            art = ROOT / 'chars' / job['id'] / 'art'
            art.mkdir(parents=True, exist_ok=True)
            for sheet in job['sheets']:
                shutil.copy2(sheet['path'], art / sheet['file'])
            prompt_file = art / ('VICTOR-PROMPT.json' if job['sheets'][0]['file'] == 'victor-desk.png' else 'PROMPTS.json')
            prompt_file.write_text(json.dumps(job['sheets'], ensure_ascii=False, indent=2), encoding='utf-8')
    for spec in ROSTER:
        if not args.characters or spec['id'] in args.characters:
            build(spec)


if __name__ == '__main__':
    main()
