"""Register original normal sprites and synchronize special contacts to artwork.

The generated atlas is an input asset. Cropping and registration never stretch
individual poses: every frame in an atlas uses one standing calibration.
"""
from io import BytesIO
from pathlib import Path
import json
import re
import struct

import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
STATES = [1000, 1010, 1020, 1030, 1040, 1070, 3000, 3500, 4000, 3015]
HEADER = '<HHHHhhHBBIIHH'


def read_sprites(path):
    blob = path.read_bytes()
    table, count = struct.unpack_from('<II', blob, 36)
    data = struct.unpack_from('<I', blob, 52)[0]
    result = {}
    for index in range(count):
        g, n, w, h, ax, ay, link, fmt, depth, offset, size, pal, flags = struct.unpack_from(HEADER, blob, table + index * 28)
        if fmt in (11, 12) and size:
            image = Image.open(BytesIO(blob[data + offset + 4:data + offset + size])).convert('RGBA')
            result[g, n] = (image, ax, ay)
    return result


def legacy_combat_sprites(root,id):
    """Recover complete old kicks and crouches from the original source atlas.

    The first import mistook detached ground shadows for bodies in several
    cells. Never preserve those tiny fragments just because the SFF is valid.
    """
    art=root/'chars'/id/'art'
    path=art/'combat.png'
    if not path.exists():
        prefix='chan' if id=='chan_kof' else id
        path=art/f'{prefix}-kick-sweep-jump-guard.png'
    if not path.exists(): return {}
    rgba=np.array(Image.open(path).convert('RGBA'))
    h,w=rgba.shape[:2]
    _,labels,stats,centers=cv2.connectedComponentsWithStats((rgba[:,:,3]>100).astype(np.uint8),8)
    figures=[i for i in range(1,len(stats)) if stats[i,4]>1000]
    assert len(figures)==24,(id,'legacy combat body count',len(figures))
    figures.sort(key=lambda i:centers[i,1])
    members=[sorted(figures[r*6:r*6+6],key=lambda i:centers[i,0]) for r in range(4)]
    idle=read_sprites(root/'chars'/id/f'{id}.sff')[0,0]
    bbox=idle[0].getchannel('A').getbbox()
    scale=(bbox[3]-bbox[1])/stats[members[0][0],3]
    rows=[]
    for r,line in enumerate(members):
        poses=[]
        floor=max(stats[i,1]+stats[i,3] for i in line)
        for c,i in enumerate(line):
            x,y,fw,fh,_=stats[i]
            mask=cv2.dilate((labels==i).astype(np.uint8),np.ones((3,3),np.uint8),iterations=2)
            pixels=rgba.copy(); pixels[:,:,3]*=mask
            box=(max(0,x-2),max(0,y-2),min(w,x+fw+2),min(h,y+fh+2))
            sprite=Image.fromarray(pixels).crop(box)
            sprite=sprite.resize((round(sprite.width*scale),round(sprite.height*scale)),Image.Resampling.NEAREST)
            ax=round(((c+.5)*w/6-box[0])*scale)
            ay=round(((floor if r==2 else y+fh)-box[1])*scale)
            poses.append((sprite,ax,ay))
        rows.append(poses)
    frames={}
    for group,row in [(230,0),(240,0),(430,1),(440,1),(40,2)]:
        for i,pose in enumerate(rows[row]): frames[group,i]=pose
    # Crouch hold uses two truly crouched pictures. The old slot 10,3 used
    # the sweep's recovered standing frame and made the character pop taller.
    for i in range(6): frames[10,i]=idle if i in (0,5) else rows[1][0]
    return frames


def normal_sprites(root, id):
    sheet_path = root / 'chars' / id / 'art/normal-v3/sheet.png'
    if not sheet_path.exists():
        return {}
    sheet = Image.open(sheet_path).convert('RGBA')
    width, height = sheet.size
    rgba=np.array(sheet)
    _,labels,stats,centers=cv2.connectedComponentsWithStats((rgba[:,:,3]>100).astype(np.uint8),8)
    figures=[i for i in range(1,len(stats)) if stats[i,4]>1000]
    assert len(figures)==24,(id,'expected 24 complete silhouettes',len(figures))
    figures.sort(key=lambda i:centers[i,1])
    cells = []
    for row in range(4):
        line = []
        members=sorted(figures[row*6:row*6+6],key=lambda i:centers[i,0])
        for column,component in enumerate(members):
            x,y,w,h,_=stats[component]
            assert x>1 and x+w<width-1 and y>1 and y+h<height-1,(id,row,column,'clipped atlas edge')
            # Generated feet/arms can cross an imaginary grid line. Extract
            # complete silhouettes first instead of clipping them to a cell.
            keep=cv2.dilate((labels==component).astype(np.uint8),np.ones((3,3),np.uint8),iterations=2)
            pixels=rgba.copy();pixels[:,:,3]*=keep
            crop=(max(0,x-3),max(0,y-3),min(width,x+w+3),min(height,y+h+3))
            sprite=Image.fromarray(pixels).crop(crop)
            local_box=(crop[0]-column*width/6,crop[1]-row*height/4,crop[2]-column*width/6,crop[3]-row*height/4)
            line.append((sprite,local_box))
        cells.append(line)
    existing = read_sprites(root / 'chars' / id / f'{id}.sff')
    idle, idle_x, idle_y = existing[0, 0]
    idle_box = idle.getchannel('A').getbbox()
    standing_height = idle_box[3] - idle_box[1]
    first_box = cells[0][0][1]
    scale = standing_height / (first_box[3] - first_box[1])
    output = sheet_path.parent
    frames = {}
    preview = Image.new('RGB', (1080, 600), (25, 34, 43))
    metrics = dict(scale=scale, standing_height=standing_height, groups={})
    for row, line in enumerate(cells):
        # The atlas puts airborne rows at different heights. Register their
        # first anticipation pose to the standing head height, preserving the
        # relative motion of later frames and tucked legs without scaling.
        floor_row = line[0][1][1] + standing_height / scale
        for col, (sprite, box) in enumerate(line):
            sprite = sprite.resize((max(1, round(sprite.width * scale)), max(1, round(sprite.height * scale))), Image.Resampling.NEAREST)
            ax = round((width / 12 - box[0]) * scale)
            # Feet of a ground attack sit on the ground. Airborne tucked feet
            # retain one virtual floor throughout their own animation row.
            ay = sprite.height if row < 2 else round((floor_row - box[1]) * scale)
            key = (8770 + row, col)
            frames[key] = (sprite, ax, ay)
            sprite.save(output / f'{key[0]}-{col}.png')
            metrics['groups'][f'{key[0]},{col}'] = dict(size=list(sprite.size), axis=[ax, ay])
            preview.paste(sprite, (col * 180 + 85 - ax, row * 150 + 135 - ay), sprite)
        ImageDraw.Draw(preview).text((4, row * 150 + 2), ['Firma de pie', 'Puño agachado', 'Mano aérea', 'Patada aérea'][row], fill='white')
    preview.save(output / 'preview.png')
    (output / 'registration.json').write_text(json.dumps(metrics, indent=2), encoding='utf-8')
    return frames


def _parts(text):
    return list(re.finditer(r'(?ims)^\[Statedef (\d+)\].*?(?=^\[Statedef |\Z)', text))


def _hit_times(block):
    times = []
    for controller in re.split(r'(?im)(?=^\[State )', block):
        if not re.search(r'(?im)^type\s*=\s*HitDef\s*$', controller):
            continue
        match = re.search(r'(?im)^trigger1\s*=\s*Time\s*=\s*(\d+)', controller)
        if match:
            times.append(int(match[1]))
    return times


def _duration(block):
    times = re.findall(r'(?im)^trigger1\s*=\s*Time\s*>=\s*(\d+)', block)
    return int(times[-1]) if times else 42


def _style(id, state):
    # Every entry describes the actual limb/prop used to strike. Support and
    # counter stances get their own windup rather than an endless attack loop.
    plans = {
        'chan_kof': [8770, 8760, 8773, 440, 8760, 8770, 8760, 240, 8760, 240],
        'felix': [8770, 8760, 8771, 440, 8760, 8771, 8770, 8770, 8770, 8770],
        'alejandro': [8760, 410, 8770, 8760, 8760, 8770, 8770, 8770, 8770, 8770],
        'daniela': [8770, 8760, 8770, 8770, 8760, 8770, 8760, 8770, 8770, 8770],
        'gameros': [8770, 8773, 8701, 440, 8760, 8770, 8770, 8701, 240, 240],
        'armando': [8770, 8772, 8760, 240, 8760, 8770, 8772, 8770, 8772, 8770],
        'vladimir': [8770, 8770, 8760, 440, 8760, 8770, 8770, 8770, 8770, 8770],
        'jaime': [8773, 410, 8701, 440, 8760, 8770, 8701, 8773, 8773, 8773],
        'leonardo': [240, 8773, 8770, 120, 20, 240, 120, 240, 240, 240],
        'cesar': [8770, 8760, 8701, 8770, 8760, 8770, 8701, 8770, 8701, 8770],
    }
    return plans[id][STATES.index(state)]


def _box(sprite, low=False, kick=False):
    image, ax, ay = sprite
    alpha = np.array(image.getchannel('A')) > 80
    yy, xx = np.nonzero(alpha)
    if not len(xx):
        return (8, -80, 55, -20)
    right = int(xx.max()) - ax
    top = int(yy.min()) - ay
    bottom = int(yy.max()) - ay
    # Restrict the vertical contact to pixels in the leading limb. This avoids
    # invisible forehead-to-foot columns and giant whole-screen props.
    tip = xx >= max(ax + 12, xx.max() - max(15, image.width // 5))
    if tip.any():
        high = int(yy[tip].min()) - ay - 3
        low_y = int(yy[tip].max()) - ay + 3
    else:
        high, low_y = max(top, -80), min(bottom, -20)
    high, low_y = max(top - 2, high), min(bottom + 2, low_y)
    if low:
        high, low_y = max(high, -58), min(low_y, -3)
    if high >= low_y:
        high, low_y = max(top, -60), min(bottom, -5)
    assert right > 2, ('contact faces away from the opponent', right)
    return (max(2, min(16, right - 24)), high, right + 2, low_y)


def _hold_windows(block):
    windows = []
    for controller in re.split(r'(?im)(?=^\[State )', block):
        if not re.search(r'(?im)^type\s*=\s*TargetBind\s*$', controller):
            continue
        match = re.search(r'(?im)^trigger1\s*=\s*Time\s*=\s*\[(\d+),(\d+)\]', controller)
        if match:
            windows.append((int(match[1]), int(match[2])))
    return windows


def _bike_windows(id, state):
    return {
        ('gameros', 1020): [(3, 20)],
        ('gameros', 3500): [(4, 16), (19, 30)],
        ('jaime', 1020): [(3, 20)],
        ('jaime', 3000): [(4, 16), (18, 24)],
    }.get((id, state), [])


def _frame_group(id, state, tick, default):
    # Airborne sprite axes retain a virtual floor, so they must not be reused
    # after landing or for a grounded rush. In particular, Armando's old
    # landing ChangeAnim is now represented by this complete timeline.
    air_windows = {
        ('chan_kof', 1020): ([(3, 24)], 240),
        ('gameros', 1010): ([(3, 26)], 240),
        ('armando', 1010): ([(3, 26)], 8770),
        ('armando', 3000): ([(3, 23)], 8770),
        ('armando', 4000): ([(3, 26)], 8770),
        ('jaime', 1000): ([(3, 26)], 240),
        ('jaime', 4000): ([(3, 26), (31, 52)], 240),
        ('leonardo', 1010): ([(3, 23)], 240),
    }
    flight = air_windows.get((id, state))
    if flight and not any(start <= tick <= stop for start, stop in flight[0]):
        return flight[1]
    if id == 'jaime' and state == 3000 and tick >= 25:
        return 240  # Finish the cycling pass with a planted kick.
    return default


def _timeline(animation, id, state, duration, contacts, group, sprites, low_attack, holds):
    out = f'\n[Begin Action {animation}]\n'
    hurt_top = -62 if low_attack else -96
    out += f'Clsn2Default: 1\nClsn2[0] = -20,{hurt_top},20,-1\n'
    timeline = []
    bikes = _bike_windows(id, state)
    for tick in range(duration + 1):
        frame_group = _frame_group(id, state, tick, group)
        if (frame_group, 0) not in sprites:
            frame_group = group
        active = next((t for t in contacts if t <= tick < t + 4), None)
        if contacts:
            future = next((t for t in contacts if t > tick), None)
            past = next((t for t in reversed(contacts) if t + 4 <= tick), None)
            if active is not None:
                # All 240 new poses were reviewed: index 3 is full extension;
                # index 2 is still winding up for several teachers.
                pose = 3 if frame_group in range(8770, 8774) else (3 if tick-active < 2 else 4)
            elif future is not None and future - tick <= 4:
                pose = 1
            elif past is not None and tick - past < 8:
                pose = 4
            else:
                pose = 0 if past is None else 5
        else:
            pose = min(5, tick * 6 // max(1, duration + 1))
        if id == 'jaime' and frame_group in (8772, 8773):
            # The authored aerial row contacts on 2, retracts on 3 and rests
            # on 4; its final atlas cell is another kick rather than recovery.
            pose = 2 if active is not None else {2: 1, 3: 3, 4: 3, 5: 4}.get(pose, pose)
        held = next((window for window in holds if window[0] <= tick <= window[1]), None)
        released = next((window for window in holds if window[1] < tick <= window[1] + 5), None)
        if held:
            pose = 3
        elif released:
            pose = 4
        if frame_group == 8701:
            riding = next((window for window in bikes if window[0] <= tick <= window[1]), None)
            if riding:
                pose = ((tick - riding[0]) // 2) % 6
        if frame_group == 8760:
            if id == 'chan_kof' and state in (1010, 3000, 4000):
                pose = 5 if active is not None else [0, 1, 2, 3, 4, 0][pose]
            if id == 'daniela' and state in (1010, 1040, 3000):
                pose = [0, 1, 2, 1, 4, 5][pose]
        sprite = sprites.get((frame_group, pose), sprites[frame_group, 0])
        box = _box(sprite, low_attack) if active is not None else None
        item = (frame_group, pose, box)
        if timeline and timeline[-1][0] == item:
            timeline[-1] = (item, timeline[-1][1] + 1)
        else:
            timeline.append((item, 1))
    for (g, pose, box), ticks in timeline:
        if box:
            out += 'Clsn1: 1\nClsn1[0] = ' + ','.join(str(x) for x in box) + '\n'
        out += f'{g},{pose}, 0,0, {ticks}\n'
    return out


def synchronize(air_text, cns_text, id, sff_path):
    """Allocate independent action timelines, with visible startup and recovery.

    HitDef time is the source of truth, so multihit attacks visibly retract and
    strike again at each contact. Active collision never exists in anticipation.
    """
    sprites = read_sprites(sff_path)
    actions = []
    blocks = {}
    catalog = {}
    for match in _parts(cns_text):
        n = int(match[1])
        if n not in STATES:
            continue
        block = match[0]
        duration = _duration(block)
        contacts = _hit_times(block)
        group = _style(id, n)
        if (group, 0) not in sprites:
            group = 200
        animation = 8800 + STATES.index(n)
        # ChangeAnim in old supers reused generic sequences and could discard
        # the landing/contact frames. The complete timeline handles them here.
        block = re.sub(r'(?ims)^\[State [^\]]*\]\s*\ntype\s*=\s*ChangeAnim\b.*?(?=^\[State |\Z)', '', block)
        block = re.sub(r'(?m)^anim\s*=.*', f'anim = {animation}', block, count=1)
        low_attack = bool(re.search(r'(?m)^type\s*=\s*C\s*$', block)) or group in (440, 8771)
        holds = _hold_windows(block)
        actions.append(_timeline(animation, id, n, duration, contacts, group, sprites, low_attack, holds))
        entry = dict(animation=animation, group=group, contacts=contacts, duration=duration,
                     hold_windows=holds, bike_windows=_bike_windows(id, n))
        if id == 'leonardo' and n == 1000:
            # var(45) snapshots the battery before it is spent. With no battery
            # the animation must also omit the last active window, otherwise a
            # surviving HitDef from kick two could connect during a fake third.
            dry_animation = 8810
            dry_contacts = [time for time in contacts if time != 25]
            actions.append(_timeline(dry_animation, id, n, duration, dry_contacts, group, sprites, low_attack, holds))
            block += f'\n[State {n}, Battery selects kick count]\ntype = ChangeAnim\ntrigger1 = Time = 0 && var(45)=0\nvalue = {dry_animation}\n'
            entry['variants'] = dict(no_battery=dict(animation=dry_animation, contacts=dry_contacts))
        blocks[n] = block
        catalog[str(n)] = entry
    cns_text = re.sub(r'(?ims)^\[Statedef (\d+)\].*?(?=^\[Statedef |\Z)', lambda m: blocks.get(int(m[1]), m[0]), cns_text)
    air_text = re.sub(r'(?ims)^\[Begin Action (?:880\d|8810)\].*?(?=^\[Begin Action |\Z)', '', air_text)
    air_text = air_text.rstrip() + '\n' + '\n'.join(actions)
    path = sff_path.parent / 'art/normal-v3/special-timelines.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(catalog, indent=2), encoding='utf-8')
    return air_text.rstrip() + '\n', cns_text
