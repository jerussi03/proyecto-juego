"""Acceptance checks and review strips for the twelve production fighters.

This checks animation meaning, not only whether an AIR/SFF reference exists:
walking has passing poses, running uses another gait, low holds stay low, the
KO is horizontal and getting up returns to standing scale. Every rendered
frame shares the same pixels per game unit and floor. Face/outfit consistency
still requires visual review; these checks do not claim to prove it.
"""
from pathlib import Path
import argparse
import hashlib
import json

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageOps

from test_teacher_normals import parse_air, read_sff

ROOT = Path(__file__).resolve().parents[1]
ROSTER = ('chava', 'hector', 'chan_kof', 'felix', 'alejandro', 'daniela',
          'gameros', 'armando', 'vladimir', 'jaime', 'leonardo', 'cesar')
TEACHERS = ROSTER[2:]
REQUIRED = (0, 10, 11, 12, 20, 21, 40, 41, 44, 47, 100, 130, 131, 132,
            200, 210, 230, 240, 400, 410, 430, 440, 600, 610, 630, 640,
            5000, 5010, 5020, 5050, 5100, 5110, 5120, 5150, 5200)
REVIEW_ACTIONS = (0, 20, 21, 100, 10, 11, 12, 40, 41, 44, 47, 130, 131,
                  200, 210, 240, 400, 440, 600, 640, 5000, 5020, 5050,
                  5100, 5110, 5120)


def bounds(sprite):
    image = sprite['image']
    box = image.getchannel('A').point(lambda a: 255 if a >= 100 else 0).getbbox()
    assert box, 'empty sprite'
    return dict(width=box[2]-box[0], height=box[3]-box[1],
                top=box[1]-sprite['ay'], floor=box[3]-sprite['ay'])


def fingerprint(sprite):
    return hashlib.sha256(sprite['image'].tobytes()).hexdigest()


def foot_span(sprite):
    """Measure shoes near the floor, excluding thin canes and loose pixels."""
    image = sprite['image']
    mask = np.asarray(image.getchannel('A')) >= 100
    yy, _ = np.nonzero(mask)
    floor = int(yy.max())+1
    band = mask[max(0, floor-round(bounds(sprite)['height']*.13)):floor].astype(np.uint8)
    _, _, stats, _ = cv2.connectedComponentsWithStats(band, 8)
    shoes = [s for s in stats[1:] if s[2] >= 5 and s[4] >= 8]
    return int(max(s[0]+s[2] for s in shoes)-min(s[0] for s in shoes)) if shoes else 0


def render_review(name, sprites, actions, output):
    columns = max(len(actions.get(n, [])) for n in REVIEW_ACTIONS)
    cell_w, cell_h = 185, 165
    sheet = Image.new('RGB', (columns*cell_w, len(REVIEW_ACTIONS)*cell_h), '#17212c')
    draw = ImageDraw.Draw(sheet)
    for row, number in enumerate(REVIEW_ACTIONS):
        for column, frame in enumerate(actions.get(number, [])):
            origin = (column*cell_w+64, row*cell_h+145)
            draw.line((column*cell_w, origin[1], (column+1)*cell_w, origin[1]), fill='#738795')
            draw.line((origin[0], row*cell_h+20, origin[0], (row+1)*cell_h), fill='#344a57')
            sprite = sprites.get((frame['group'], frame['index']))
            if not sprite:
                continue
            image, axis_x = sprite['image'], sprite['ax']
            if frame['flip']:
                image = ImageOps.mirror(image)
                axis_x = image.width-axis_x
            sheet.paste(image, (origin[0]-axis_x+frame['x'], origin[1]-sprite['ay']+frame['y']), image)
            draw.text((column*cell_w+4, row*cell_h+3),
                      f'{number}:{column+1} {frame["group"]},{frame["index"]} {frame["duration"]}t', fill='white')
    sheet.save(output/f'{name}-motion.png')


def check_character(name, output):
    folder = ROOT/'chars'/name
    sprites = read_sff(folder/f'{name}.sff')
    actions = parse_air((folder/f'{name}.air').read_text(encoding='utf-8'))
    checks, metrics = {}, {}
    checks['all_required_actions'] = all(actions.get(n) for n in REQUIRED)
    missing = [(n, f['group'], f['index']) for n, frames in actions.items() for f in frames
               if f['group'] >= 0 and (f['group'], f['index']) not in sprites]
    checks['all_air_sprites_exist'] = not missing
    metrics['missing_references'] = missing
    idle_h = bounds(sprites[0, 0])['height']
    metrics['standing_height'] = idle_h

    for number in (11, 131):
        ratios = [bounds(sprites[f['group'], f['index']])['height']/idle_h for f in actions.get(number, [])]
        checks[f'{number}_hold_remains_crouched'] = bool(ratios) and max(ratios) < .85
        metrics[f'{number}_height_ratios'] = [round(x, 3) for x in ratios]

    ko = sprites.get((5050, 4))
    getup_frames = actions.get(5120, [])
    getup_key = (getup_frames[-1]['group'], getup_frames[-1]['index']) if getup_frames else None
    getup = sprites.get(getup_key)
    if ko:
        b = bounds(ko)
        checks['resting_ko_is_horizontal'] = b['width']/b['height'] > 2
        checks['resting_ko_has_own_art'] = all(fingerprint(ko) != fingerprint(sprites[k])
                                               for k in ((0, 0), (120, 0), (120, 1)) if k in sprites)
        metrics['ko'] = b
    else:
        checks['resting_ko_is_horizontal'] = False
    if getup:
        ratio = bounds(getup)['height']/idle_h
        checks['getup_finishes_at_standing_scale'] = .95 <= ratio <= 1.08
        metrics['getup_final_height_ratio'] = round(ratio, 3)
        metrics['getup_final_sprite'] = list(getup_key)
    else:
        checks['getup_finishes_at_standing_scale'] = False

    grounded = (0, 10, 11, 12, 20, 21, 100, 130, 131, 200, 210, 230, 240,
                400, 410, 430, 440, 5110, 5120)
    offsets = [(n, i, f['y']+bounds(sprites[f['group'], f['index']])['floor'])
               for n in grounded for i, f in enumerate(actions.get(n, []))
               if (f['group'], f['index']) in sprites]
    checks['grounded_frames_registered_to_floor'] = all(abs(v) <= 1 for _, _, v in offsets)
    metrics['grounded_outliers'] = [list(x) for x in offsets if abs(x[2]) > 1]

    if name in TEACHERS:
        walk = actions.get(20, [])
        run = actions.get(100, [])
        checks['walk_is_one_six_frame_stride'] = [(f['group'], f['index']) for f in walk] == [(8900, i) for i in range(6)]
        checks['run_uses_dedicated_six_frame_gait'] = [(f['group'], f['index']) for f in run] == [(8901, i) for i in range(6)]
        if all((8900, i) in sprites and (8901, i) in sprites for i in range(6)):
            spans = [foot_span(sprites[8900, i]) for i in range(6)]
            metrics['walk_shoe_spans'] = spans
            # A six-phase stride can place its passing pose before or after
            # its weight-transfer frame; both valid phase conventions exist.
            passing = min(max(spans[1], spans[4]), max(spans[2], spans[5]))
            checks['walk_has_two_narrow_passing_poses'] = passing < min(spans[0], spans[3])*.85
            checks['walk_and_run_have_distinct_art'] = all(fingerprint(sprites[8900, i]) != fingerprint(sprites[8901, i]) for i in range(6))
        else:
            checks['walk_has_two_narrow_passing_poses'] = False
            checks['walk_and_run_have_distinct_art'] = False
        if all((8902, i) in sprites for i in range(6)):
            h = [bounds(sprites[8902, i])['height'] for i in range(6)]
            checks['crouch_has_middle_transition_poses'] = h[0] > h[1] > h[2] and h[5] > h[4] > h[3]
            checks['crouch_standing_endpoints_match_scale'] = all(.95 <= h[i]/idle_h <= 1.08 for i in (0, 5))
            metrics['crouch_pose_heights'] = h
        else:
            checks['crouch_has_middle_transition_poses'] = False
        low = [bounds(sprites[8771, i])['height']/idle_h for i in (0, 5) if (8771, i) in sprites]
        checks['low_punch_never_stands_at_endpoints'] = len(low) == 2 and max(low) < .85
        airborne = [bounds(sprites[8903, i])['top'] for i in (2, 3, 4) if (8903, i) in sprites]
        checks['airborne_jump_preserves_virtual_body_origin'] = len(airborne) == 3 and all(abs(top+idle_h) <= 1 for top in airborne)

    render_review(name, sprites, actions, output)
    return dict(passed=all(checks.values()), checks=checks, metrics=metrics)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('characters', nargs='*', metavar='CHARACTER')
    parser.add_argument('--output', type=Path, default=ROOT/'scratch/teacher-motion-qa')
    args = parser.parse_args()
    unknown = set(args.characters)-set(ROSTER)
    if unknown:
        parser.error('unknown characters: '+', '.join(sorted(unknown)))
    args.output.mkdir(parents=True, exist_ok=True)
    results = {name: check_character(name, args.output) for name in args.characters or ROSTER}
    (args.output/'results.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    for name, result in results.items():
        failures = [label for label, passed in result['checks'].items() if not passed]
        print(name, 'PASS' if result['passed'] else 'FAIL', ', '.join(failures))
    raise SystemExit(0 if all(r['passed'] for r in results.values()) else 1)


if __name__ == '__main__':
    main()
