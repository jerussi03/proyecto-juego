"""Check all twelve fighters' normals and draw their real sprites at native scale.

Default: static AIR/SFF checks plus pivot/contact sheets in ignored scratch/.
--run: isolated real-button playback, including hit, whiff, low and air guard.
The fixtures never change production files, keyboard maps or global config.
"""
from pathlib import Path
from io import BytesIO
import argparse
import csv
import hashlib
import json
import re
import struct
import subprocess

from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'scratch/teacher-normals-qa'
ROSTER = ['hector', 'chava', 'chan_kof', 'felix', 'alejandro', 'daniela',
          'gameros', 'armando', 'vladimir', 'jaime', 'leonardo', 'cesar']
NORMALS = [(200, 'x', 'S'), (210, 'y', 'S'), (230, 'a', 'S'), (240, 'b', 'S'),
           (400, 'x', 'C'), (410, 'y', 'C'), (430, 'a', 'C'), (440, 'b', 'C'),
           (600, 'x', 'A'), (610, 'y', 'A'), (630, 'a', 'A'), (640, 'b', 'A')]
SPAN = 150
# Independent acceptance examples: each fighter has a confirmed route and a
# deliberately unavailable route. They are exercised with real button presses.
CHAIN_EXAMPLES = {
    'chava': ((200, 210), (200, 230)), 'hector': ((200, 201), (230, 240)),
    'chan_kof': ((200, 210), (200, 240)), 'felix': ((400, 210), (200, 210)),
    'alejandro': ((200, 210), (230, 240)), 'daniela': ((200, 230), (200, 240)),
    'gameros': ((200, 230), (200, 240)), 'armando': ((200, 240), (200, 210)),
    'vladimir': ((200, 210), (230, 240)), 'jaime': ((230, 240), (200, 210)),
    'leonardo': ((230, 240), (200, 210)), 'cesar': ((400, 210), (200, 210)),
}


def parse_air(text):
    """AIR collision boxes are world offsets, independent of sprite trim/axes."""
    actions = {}
    for match in re.finditer(r'(?ims)^\[Begin Action (\d+)\]\s*\n(.*?)(?=^\[Begin Action |\Z)', text):
        frames, defaults, current = [], {1: [], 2: []}, {1: None, 2: None}
        destination = {}
        for raw in match[2].splitlines():
            line = raw.split(';', 1)[0].strip()
            header = re.match(r'Clsn([12])(Default)?:\s*(\d+)', line, re.I)
            box = re.match(r'Clsn([12])\[\d+\]\s*=\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)', line, re.I)
            frame = re.match(r'(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)(.*)', line)
            if header:
                kind = int(header[1])
                destination[kind] = defaults if header[2] else current
                destination[kind][kind] = []
            elif box:
                kind = int(box[1])
                destination[kind][kind].append(tuple(map(int, box.groups()[1:])))
            elif frame:
                frames.append(dict(group=int(frame[1]), index=int(frame[2]), x=int(frame[3]),
                                   y=int(frame[4]), duration=int(frame[5]), flip='H' in frame[6].upper(),
                                   hit=list(defaults[1] if current[1] is None else current[1]),
                                   hurt=list(defaults[2] if current[2] is None else current[2])))
                current = {1: None, 2: None}
        actions[int(match[1])] = frames
    return actions


def read_sff(path):
    blob = path.read_bytes()
    offset, count = struct.unpack_from('<II', blob, 36)
    ldata = struct.unpack_from('<I', blob, 52)[0]
    tdata = struct.unpack_from('<I', blob, 60)[0]
    entries = [struct.unpack_from('<HHHHhhHBBIIHH', blob, offset + i * 28) for i in range(count)]
    sprites = {}
    for i, entry in enumerate(entries):
        group, index, width, height, ax, ay, link, fmt, depth, ofs, size, pal, flags = entry
        if size == 0:
            previous = entries[link]
            image = sprites[previous[0], previous[1]]['image']
        else:
            assert fmt in {10, 11, 12}, (path, group, index, 'expected PNG sprites', fmt)
            start = (tdata if flags & 1 else ldata) + ofs
            image = Image.open(BytesIO(blob[start + 4:start + size])).convert('RGBA')
            assert image.size == (width, height), (path, group, index, image.size)
        assert (group, index) not in sprites, (path, 'duplicate sprite', group, index)
        sprites[group, index] = dict(image=image, ax=ax, ay=ay)
    return sprites


def state_sections(text):
    return {int(m[1]): m[2] for m in re.finditer(r'(?ims)^\[Statedef\s+(-?\d+)\](.*?)(?=^\[Statedef |\Z)', text)}


def value(text, key):
    match = re.search(r'(?im)^\s*' + re.escape(key) + r'\s*=\s*([^;\r\n]+)', text)
    return match[1].strip() if match else None


def referenced_actions(state):
    expression = value(state.split('[State ', 1)[0], 'anim') or ''
    return {int(n) for n in re.findall(r'(?<![\w.])\d+', expression) if int(n) >= 100}


def frame_mask(sprite, frame, box):
    """Use actual sprite axes; total weapon width is never treated as body scale."""
    image = sprite['image']
    ax = sprite['ax']
    if frame['flip']:
        image = ImageOps.mirror(image)
        ax = image.width - ax
    x1, y1, x2, y2 = box
    rect = (x1 - frame['x'] + ax, y1 - frame['y'] + sprite['ay'],
            x2 - frame['x'] + ax + 1, y2 - frame['y'] + sprite['ay'] + 1)
    # Ignore antialiased wisps; a box touching one translucent fringe pixel
    # cannot establish that the fist, foot or weapon is actually there.
    return image.getchannel('A').crop(rect).point(lambda alpha: 255 if alpha >= 96 else 0)


def contact_sheet(name, sprites, actions, selected):
    # Every panel uses the same pixels per game unit, origin and floor. Cropping
    # or fitting each silhouette would hide the very size changes under review.
    width, height = 220, 205
    sheet = Image.new('RGB', (width * 7, height * 2), '#17212c')
    draw = ImageDraw.Draw(sheet)
    for i, (label, action, frame_index) in enumerate(selected):
        x, y = (i % 7) * width, (i // 7) * height
        origin = (x + 76, y + 170)
        frame = actions[action][frame_index]
        sprite = sprites.get((frame['group'], frame['index']))
        if sprite is None:
            draw.text((x+8,y+36),f'MISSING {frame["group"]},{frame["index"]}',fill='#ff6868')
            continue
        image, ax = sprite['image'], sprite['ax']
        if frame['flip']:
            image = ImageOps.mirror(image)
            ax = image.width - ax
        draw.text((x + 8, y + 6), f'{label} / {action}:{frame_index + 1}', fill='white')
        draw.line((x, origin[1], x + width, origin[1]), fill='#607482')
        draw.line((origin[0], y + 20, origin[0], y + height), fill='#334654')
        sheet.paste(image, (origin[0] - ax + frame['x'], origin[1] - sprite['ay'] + frame['y']), image)
        for key, color in [('hurt', '#5cbeed'), ('hit', '#ff6868')]:
            for box in frame[key]:
                draw.rectangle(tuple(v + origin[j % 2] for j, v in enumerate(box)), outline=color, width=1)
        draw.ellipse((origin[0]-2, origin[1]-2, origin[0]+2, origin[1]+2), fill='white')
    sheet.save(OUT / f'{name}-contacts.png')


def pose_sheet(name, sprites, actions):
    """All authored attack phases, with a standing body as a scale reference.

    No automatic full-silhouette height assertion is used: a raised cane, a
    tucked leg and a crouch intentionally change that measurement. This sheet
    exposes head/torso/limb proportions for a meaningful visual inspection.
    """
    targets = [0, 11] + [normal[0] for normal in NORMALS]
    columns = max(len(actions[target]) for target in targets if target in actions)
    width, height = 190, 160
    sheet = Image.new('RGB', (columns*width, len(targets)*height), '#17212c')
    draw = ImageDraw.Draw(sheet)
    reference = sprites[actions[0][0]['group'], actions[0][0]['index']]
    ghost = reference['image'].copy()
    ghost.putalpha(ghost.getchannel('A').point(lambda alpha: alpha//5))
    for row, target in enumerate(targets):
        for column, frame in enumerate(actions.get(target, [])):
            x, y = column*width, row*height
            origin = (x+60, y+140)
            draw.line((x, origin[1], x+width, origin[1]), fill='#657685')
            for offset in [-100, -50]:
                draw.line((x, origin[1]+offset, x+width, origin[1]+offset), fill='#263b48')
            draw.line((origin[0], y+20, origin[0], y+height), fill='#354954')
            sheet.paste(ghost, (origin[0]-reference['ax'], origin[1]-reference['ay']), ghost)
            sprite = sprites.get((frame['group'], frame['index']))
            if sprite is None:
                draw.text((x+5,y+28),f'MISSING {frame["group"]},{frame["index"]}',fill='#ff6868')
                continue
            image, ax = sprite['image'], sprite['ax']
            if frame['flip']:
                image, ax = ImageOps.mirror(image), image.width-ax
            sheet.paste(image, (origin[0]-ax+frame['x'], origin[1]-sprite['ay']+frame['y']), image)
            draw.text((x+5,y+4), f'{target}:{column+1} / {frame["duration"]}t', fill='white')
    sheet.save(OUT / f'{name}-poses.png')


def static_check(names=ROSTER):
    OUT.mkdir(parents=True, exist_ok=True)
    report, signatures = {}, {}
    for name in names:
        folder = ROOT / 'chars' / name
        sprites = read_sff(folder / f'{name}.sff')
        actions = parse_air((folder / f'{name}.air').read_text(encoding='utf-8'))
        state_text = '\n'.join((folder / file).read_text(encoding='utf-8') for file in [f'{name}.cns', 'kof-extra.cns'])
        states = state_sections(state_text)
        checks, details, selected = {}, {}, [('idle', 0, 0), ('crouch', 11, 0)]
        idle = actions[0][0]
        idle_alpha = sprites[idle['group'],idle['index']]['image'].getchannel('A')
        idle_area = sum(idle_alpha.histogram()[96:])
        body_metrics = {}
        for animation, frames in actions.items():
            if animation >= 800:
                continue
            ratios = []
            for frame in frames:
                sprite = sprites.get((frame['group'],frame['index']))
                ratios.append(round(sum(sprite['image'].getchannel('A').histogram()[96:])/idle_area, 3)
                              if sprite else 0)
            checks[f'{animation}_body_present_every_phase'] = bool(ratios) and min(ratios) >= .18
            body_metrics[animation] = ratios
            if animation in {0,11}:
                floor_offsets = []
                for frame in frames:
                    sprite = sprites.get((frame['group'],frame['index']))
                    bounds = sprite['image'].getchannel('A').point(lambda alpha: 255 if alpha >= 96 else 0).getbbox() if sprite else None
                    floor_offsets.append(frame['y']+bounds[3]-sprite['ay'] if bounds else -1000)
                checks[f'{animation}_settled_feet_on_floor'] = all(-5 <= offset <= 5 for offset in floor_offsets)
        fingerprint = []
        contact_images = {}
        for state, button, stance in NORMALS:
            section = states.get(state, '')
            checks[f'{state}_defined'] = bool(section)
            if not section:
                continue
            checks[f'{state}_stance'] = value(section.split('[State ', 1)[0], 'type') == stance
            checks[f'{state}_physical_hit'] = bool(re.search(r'(?im)^type\s*=\s*HitDef\s*$', section))
            animations = referenced_actions(section)
            # Ifelse selectors contain flag literals; keep only actual AIR IDs.
            animations &= actions.keys()
            checks[f'{state}_animation'] = bool(animations)
            details[state] = []
            for animation in sorted(animations):
                frames = actions[animation]
                active = [(index, frame) for index, frame in enumerate(frames) if frame['hit']]
                checks[f'{animation}_active_box'] = bool(active)
                checks[f'{animation}_finite'] = bool(frames) and all(frame['duration'] > 0 for frame in frames)
                # A crouch changes height, but cannot turn a person into a tiny
                # detached shadow. Area catches extraction failures without
                # mistaking raised weapons or bent knees for a size change.
                areas = []
                for frame in frames:
                    sprite = sprites.get((frame['group'],frame['index']))
                    areas.append(sum(sprite['image'].getchannel('A').histogram()[96:]) if sprite else 0)
                checks[f'{animation}_body_present_every_phase'] = bool(areas) and min(areas) >= idle_area*.18
                for index, frame in active:
                    sprite = sprites.get((frame['group'], frame['index']))
                    checks[f'{animation}_{index}_sprite'] = sprite is not None
                    if sprite is None:
                        continue
                    contact_images.setdefault(state, hashlib.sha256(sprite['image'].tobytes()).hexdigest())
                    intersections = [frame_mask(sprite, frame, box).histogram()[255] >= 4 for box in frame['hit']]
                    checks[f'{animation}_{index}_visible_contact'] = any(intersections)
                    details[state].append(dict(action=animation, element=index+1,
                        sprite=[frame['group'], frame['index']], hitboxes=frame['hit'],
                        visible_contact=any(intersections)))
                if active and not any(label == str(state) for label, _, _ in selected):
                    selected.append((str(state), animation, active[0][0]))
            # Compare gameplay values only. Different sprite IDs, names and
            # effect colors cannot make two mechanically identical kits pass.
            keys = ['damage', 'pausetime', 'ground.hittime', 'ground.velocity', 'air.velocity',
                    'fall', 'guardflag', 'hitflag', 'juggle', 'poweradd']
            fingerprint.append(tuple((key, value(section, key)) for key in keys))
        for punch, kick in [(200,230),(210,240),(400,430),(410,440),(600,630),(610,640)]:
            checks[f'{punch}_{kick}_different_visible_strike'] = (punch in contact_images and kick in contact_images
                and contact_images[punch] != contact_images[kick])
        signatures[name] = hashlib.sha256(repr(fingerprint).encode()).hexdigest()
        contact_sheet(name, sprites, actions, selected)
        pose_sheet(name, sprites, actions)
        report[name] = dict(checks=checks, normals=details, body_area_relative_to_idle=body_metrics,
                            passed=all(checks.values()))
    groups = {}
    for name, signature in signatures.items():
        groups.setdefault(signature, []).append(name)
    duplicates = [group for group in groups.values() if len(group) > 1]
    result = dict(characters=report, identical_gameplay_kits=duplicates,
                  passed=all(row['passed'] for row in report.values()) and not duplicates)
    (OUT / 'static-validation.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    failed = [(name, key) for name, row in report.items() for key, ok in row['checks'].items() if not ok]
    print('Normal static checks:', len(names), 'fighters;', len(failed), 'failures;',
          len(duplicates), 'duplicate gameplay kits', flush=True)
    for failure in failed:
        print('FAIL', *failure, flush=True)
    if duplicates:
        print('IDENTICAL GAMEPLAY', duplicates, flush=True)
    return result


def controller(kind, params, trigger, label='Normal QA'):
    return f'\n[State -2, {label}]\ntype = {kind}\ntrigger1 = {trigger}\n{params}\n'


def scenarios(name):
    cases = []
    for facing in [1, -1]:
        for state, button, stance in NORMALS:
            for mode in ['hit', 'whiff', 'guard']:
                case=dict(state=state, button=button, stance=stance, facing=facing, mode=mode)
                if name=='chava' and state==200 and mode=='whiff': case['alternate_repeat']=True
                cases.append(case)
        allowed, forbidden = CHAIN_EXAMPLES[name]
        for mode in ['hit', 'guard', 'whiff']:
            source, target = allowed
            _, button, stance = next(normal for normal in NORMALS if normal[0] == source)
            chain_button = 'x' if target == 201 else next(normal[1] for normal in NORMALS if normal[0] == target)
            cases.append(dict(state=source, button=button, stance=stance, facing=facing, mode=mode,
                              chain_target=target, chain_button=chain_button, chain_allowed=mode=='hit'))
        source, target = forbidden
        _, button, stance = next(normal for normal in NORMALS if normal[0] == source)
        chain_button = next(normal[1] for normal in NORMALS if normal[0] == target)
        cases.append(dict(state=source, button=button, stance=stance, facing=facing, mode='hit',
                          chain_target=target, chain_button=chain_button, chain_allowed=False))
    return cases


def prepare(name, cases):
    folder = ROOT / 'chars' / name
    qa = controller('VarAdd', 'v = 58\nvalue = 1\nignorehitpause = 1', '!IsHelper && RoundState = 2')
    qa += controller('VarSet', 'fv = 20\nvalue = MoveHit\nignorehitpause = 1', '!IsHelper')
    qa += controller('VarSet', 'fv = 21\nvalue = MoveGuarded\nignorehitpause = 1', '!IsHelper')
    for i, case in enumerate(cases):
        start, facing = i * SPAN + 10, case['facing']
        distance = 280 if case['mode'] == 'whiff' else 40
        setup = f'!IsHelper && var(58) = {start}'
        for kind, params in [
            ('LifeSet', 'value = 1000'), ('PowerSet', 'value = 0'),
            ('VarSet', 'v = 20\nvalue = 0'), ('VarSet', 'v = 24\nvalue = 0'),
            ('VarSet', 'v = 28\nvalue = 0'),
            ('VarSet', 'v = 44\nvalue = 0'), ('VarSet', 'v = 46\nvalue = 0'),
            ('VarSet', 'v = 48\nvalue = 0'),
            ('VelSet', 'x = 0\ny = 0'),
            ('PosSet', f'x = {-distance*facing/2} - CameraPos X\ny = 0'),
            ('LifeSet', 'value = 1000\nredirectID = EnemyNear,ID'),
            ('PowerSet', 'value = 0\nredirectID = EnemyNear,ID'),
            ('ChangeState', 'value = 0\nctrl = 1\nredirectID = EnemyNear,ID'),
            ('VelSet', 'x = 0\ny = 0\nredirectID = EnemyNear,ID'),
            ('PosSet', f'x = {distance*facing/2} - CameraPos X\ny = 0\nredirectID = EnemyNear,ID'),
        ]:
            qa += controller(kind, params, setup)
        qa += controller('Turn', '', setup + f' && Facing != {facing}')
        qa += controller('Turn', 'redirectID = EnemyNear,ID', setup + f' && EnemyNear,Facing != {-facing}')
        # A root ChangeState stops the rest of its controllers that tick.
        # Finish resetting positions/facing before changing the root state.
        qa += controller('ChangeState', 'value = 0\nctrl = 1', setup)
        if case['stance'] == 'A':
            # Keep a short hop at a fixed test height until the move recovers;
            # release it afterwards to verify landing and restored control.
            window = f'!IsHelper && var(58) = [{start+4},{start+65}]'
            qa += controller('PosSet', 'y = -28', window)
            qa += controller('VelSet', 'y = 0', window)
            qa += controller('ChangeState', 'value = 50\nctrl = 1', f'var(58) = {start+5}')
        elif case['stance'] == 'C':
            qa += controller('AssertInput', 'flag = D', f'var(58) = [{start+4},{start+70}]')
        if case['mode'] == 'guard':
            guard = 131 if case['stance'] == 'C' else 130
            # 130/131 are guard poses; 150/152 are guard-hit reactions and
            # immediately exit without a real hit. Enter the guard pose only
            # during the attack so the dummy cannot walk/backhop out of range.
            qa += controller('ChangeState', f'value = {guard}\nctrl = 0\nredirectID = EnemyNear,ID',
                f'StateNo={case["state"]} && MoveGuarded=0 && var(58)=[{start+8},{start+60}]')
            flags = 'flag = B' + ('\nflag2 = D' if guard == 131 else '')
            qa += controller('AssertInput', flags+'\nredirectID = EnemyNear,ID', f'var(58) = [{start+8},{start+70}]')
        qa += controller('AssertInput', f'flag = {case["button"]}', f'var(58) = [{start+8},{start+9}]')
        if 'chain_target' in case:
            qa += controller('AssertInput', f'flag = {case["chain_button"]}\nignorehitpause = 1',
                f'!IsHelper && StateNo={case["state"]} && Time=[6,9] && var(58)=[{start+12},{start+55}]')
            if name=='hector' and case['chain_target']==201 and case['chain_allowed']:
                qa += controller('AssertInput', 'flag = x\nignorehitpause = 1',
                    f'!IsHelper && StateNo=201 && Time=[6,9] && var(58)=[{start+12},{start+65}]')
        if case.get('alternate_repeat'):
            qa += controller('AssertInput', 'flag = x\nignorehitpause = 1', f'var(58)=[{start+17},{start+18}]')
    text = (folder / f'{name}.cns').read_text(encoding='utf-8')
    if '[Statedef -2]' in text:
        text = text.replace('[Statedef -2]', '[Statedef -2]\n'+qa, 1)
    else:
        text += '\n[Statedef -2]\n'+qa
    (folder / 'normal-qa.cns').write_text(text, encoding='utf-8')
    definition = re.sub(r'(?m)^st\s*=.*', 'st = normal-qa.cns', (folder / f'{name}.def').read_text(encoding='utf-8'))
    (folder / 'normal-qa.def').write_text(definition, encoding='utf-8')


def check_run(name, cases):
    with (OUT / f'{name}.csv').open() as source:
        rows = [[float(value) for value in row] for row in csv.reader(source)]
    results = []
    for i, case in enumerate(cases):
        start = i * SPAN + 18
        window = [row for row in rows if start <= row[0] < start+120]
        state = case['state']
        # Hector's repeated Ping and Chava's alternate standing punch keep the
        # same button identity while being allowed their dedicated follow-ups.
        allowed = {state, 201, 202} if state == 200 and name == 'hector' else {state}
        entered = [row for row in window if int(row[1]) in allowed]
        checks = dict(button_enters_normal=bool(entered),
                      recovers_control=any(row[7] == 1 and row[0] > start+70 for row in window),
                      preserves_identity_resource=all(0 <= row[10] <= 3 for row in window))
        if case['mode'] == 'hit':
            checks['physical_contact_hurts'] = any(row[4] < 1000 for row in window)
            checks['hit_confirmed'] = any(row[5] > 0 for row in entered)
        elif case['mode'] == 'whiff':
            checks['no_distant_damage'] = all(row[4] == 1000 for row in window)
            checks['no_false_confirm'] = all(row[5] == 0 for row in entered)
        else:
            checks['guard_registered'] = any(row[6] > 0 for row in entered)
            # Normal strikes have no chip damage; an overhead may deliberately
            # fail low guard, so crouched attacks here use the correct stance.
            checks['guard_prevents_damage'] = all(row[4] == 1000 for row in window)
        if 'chain_target' in case:
            target_seen = any(row[1] == case['chain_target'] for row in window)
            checks['own_confirmed_chain'] = target_seen == case['chain_allowed']
            if name=='hector' and case['chain_target']==201 and case['chain_allowed']:
                checks['triple_ping_finisher']=any(row[1]==202 for row in window)
        if case.get('alternate_repeat'):
            checks['buffered_alternate_repeat']={200,201}<={int(row[9]) for row in entered}
        results.append(dict(**case, checks=checks, passed=all(checks.values())))
    failed = [row for row in results if not row['passed']]
    print(name, len(results), 'normal cases,', len(failed), 'failed', flush=True)
    for row in failed[:8]:
        print(row, flush=True)
    if len(failed)>8:
        print('Additional failures:',len(failed)-8,'(full details in input-validation.json)',flush=True)
    return results


def run(names):
    original = (ROOT / 'save/config.ini').read_bytes()
    config = original.decode('utf-8-sig')
    config = re.sub(r'(?m)^Lua\s*=.*', 'Lua = loop(), dofile("scratch/teacher-normals-qa/observer.lua")', config)
    config = re.sub(r'(?m)^ScreenshotFolder\s*=.*', 'ScreenshotFolder = scratch/teacher-normals-qa', config)
    config = re.sub(r'(?m)^Fullscreen\s*=.*', 'Fullscreen = false', config)
    (OUT / 'config.ini').write_text(config, encoding='utf-8')
    observer = '''if player(1) and roundState()==2 then
 local t=var(58)
 if t>0 and t~=normalLastTick then
  normalLastTick=t
  local values={t,stateNo(),time(),life(),0,fvar(20),fvar(21),ctrl() and 1 or 0,posY(),anim(),var(44),posX(),0,facing(),0,0}
  if enemyNear() then values[5]=life(); values[13]=posX(); values[15]=facing(); values[16]=stateNo() end
  player(1)
  local file=assert(io.open("scratch/teacher-normals-qa/"..normalQAID..".csv","a"))
  file:write(table.concat(values,",").."\\n"); file:close()
  if t>=CASETICKS then os.exit() end
 end
end
'''
    result_path = OUT / 'input-validation.json'
    report = json.loads(result_path.read_text(encoding='utf-8')) if result_path.exists() else {}
    for name in names:
        cases = scenarios(name)
        prepare(name, cases)
        output = OUT / f'{name}.csv'
        if output.exists():
            output.unlink()
        (OUT / 'observer.lua').write_text(f'normalQAID="{name}"\n'+observer.replace('CASETICKS',str(len(cases)*SPAN)), encoding='utf-8')
        proc = subprocess.run([str(ROOT / 'TheKingOfUTc.exe'), '-config', str(OUT / 'config.ini'),
            '-p1', f'{name}/normal-qa.def', '-p2', 'chava', '-s', 'stages/patio.def',
            '-rounds', '1', '-time', '-1', '-speedtest', '-nosound', '-windowed'],
            cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=55)
        assert proc.returncode == 0, (name, proc.stdout.decode(errors='replace')[-2000:])
        report[name] = check_run(name, cases)
        result_path.write_text(json.dumps(report, indent=2), encoding='utf-8')
        assert (ROOT / 'save/config.ini').read_bytes() == original, 'Global config changed'
    assert all(case['passed'] for name in names for case in report[name]), 'Normal gameplay failures'
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('characters', nargs='*', metavar='CHARACTER')
    parser.add_argument('--run', action='store_true', help='Launch sequential isolated engine matches')
    options = parser.parse_args()
    names = options.characters or ROSTER
    if set(names) - set(ROSTER):
        parser.error('Unknown characters: '+', '.join(sorted(set(names)-set(ROSTER))))
    result = static_check(names)
    if options.run:
        run(names)
    raise SystemExit(0 if result['passed'] else 1)
