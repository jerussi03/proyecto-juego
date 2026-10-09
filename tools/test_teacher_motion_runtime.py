"""Exercise movement, guarding, knockdown/getup and KO in the real engine.

The fixture is a separate game below scratch/. Its extra controllers supply
inputs and an attacking dummy; production CNS, DEF and configuration stay intact.
CSV observations and engine screenshots provide evidence of executed actions.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import os
import re
import subprocess
import time

from package_android_assets import allowlist, package, update_ini

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'scratch/teacher-motion-runtime'
GAME = OUT / 'game'
ROSTER = ('chava', 'hector', 'chan_kof', 'felix', 'alejandro', 'daniela',
          'gameros', 'armando', 'vladimir', 'jaime', 'leonardo', 'cesar')
SPAN = 240
CASES = ('walk_forward', 'walk_backward', 'run', 'crouch', 'jump',
         'standing_guard', 'crouching_guard', 'air_guard', 'knockdown_getup', 'ko')


def controller(kind, parameters, trigger, label='Motion fixture'):
    return f'\n[State -2, {label}]\ntype = {kind}\ntrigger1 = {trigger}\n{parameters}\n'


def source_hashes():
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in allowlist()}


def fixture_controllers():
    qa = controller('VarAdd', 'v = 58\nvalue = 1\nignorehitpause = 1',
                    '!IsHelper && RoundState >= 2')
    for index, case in enumerate(CASES):
        start = index * SPAN + 10
        setup = f'!IsHelper && var(58) = {start}'
        distance = 42 if 'guard' in case or case in ('knockdown_getup', 'ko') else 210
        for kind, parameters in (
            ('LifeSet', 'value = 1000'), ('PowerSet', 'value = 0'),
            ('VelSet', 'x = 0\ny = 0'), ('PosSet', f'x = {-distance / 2} - CameraPos X\ny = 0'),
            ('LifeSet', 'value = 1000\nredirectID = EnemyNear,ID'),
            ('VelSet', 'x = 0\ny = 0\nredirectID = EnemyNear,ID'),
            ('PosSet', f'x = {distance / 2} - CameraPos X\ny = 0\nredirectID = EnemyNear,ID'),
            ('ChangeState', 'value = 0\nctrl = 1\nredirectID = EnemyNear,ID'),
        ):
            qa += controller(kind, parameters, setup)
        qa += controller('Turn', '', setup + ' && Facing != 1')
        qa += controller('Turn', 'redirectID = EnemyNear,ID', setup + ' && EnemyNear,Facing != -1')
        # ChangeState stops root execution for this tick; always reset it last.
        qa += controller('ChangeState', 'value = 0\nctrl = 1', setup)

        def inputs(flags, first, last):
            nonlocal qa
            params = '\n'.join(f'flag{n + 1 if n else ""} = {flag}' for n, flag in enumerate(flags))
            qa += controller('AssertInput', params, f'!IsHelper && var(58) = [{start + first},{start + last}]')

        if case == 'walk_forward':
            inputs(['F'], 12, 58)
        elif case == 'walk_backward':
            inputs(['B'], 12, 58)
        elif case == 'run':
            inputs(['F'], 12, 14)
            inputs(['F'], 22, 58)
        elif case == 'crouch':
            inputs(['D'], 12, 58)
        elif case == 'jump':
            inputs(['U'], 12, 14)
        elif 'guard' in case:
            # An actual incoming HitDef supplies guard distance. Back/down are
            # real asserted inputs; no replacement guard or common states.
            if case == 'air_guard':
                inputs(['U'], 12, 14)
                inputs(['B'], 15, 65)
                hit_tick = 25
            else:
                inputs(['B', 'D'] if case == 'crouching_guard' else ['B'], 12, 65)
                hit_tick = 20
            qa += controller('ChangeState', 'value = 9800\nctrl = 0\nredirectID = EnemyNear,ID',
                             f'!IsHelper && var(58) = {start + hit_tick}')
        else:
            attack = 9801 if case == 'knockdown_getup' else 9802
            qa += controller('ChangeState', f'value = {attack}\nctrl = 0\nredirectID = EnemyNear,ID',
                             f'!IsHelper && var(58) = {start + 20}')
    return qa


def dummy_states():
    output = ''
    for state, damage, falling in ((9800, 1, 0), (9801, 1, 1), (9802, 2000, 1)):
        output += f'''
[Statedef {state}]
type = S
movetype = A
physics = N
anim = 9800
ctrl = 0
velset = 0,0

[State {state}, Incoming fixture strike]
type = HitDef
trigger1 = Time = 5
attr = S, NA
damage = {damage},0
animtype = Back
guardflag = MA
hitflag = MAF
priority = 7,Hit
pausetime = 0,0
sparkno = -1
guard.sparkno = -1
ground.type = High
ground.hittime = 14
ground.slidetime = 10
guard.hittime = 14
guard.slidetime = 10
guard.ctrltime = 14
ground.velocity = 0,{(-7 if falling else 0)}
air.velocity = 0,-3
yaccel = .5
fall = {falling}
fall.yvelocity = -3
fall.xvelocity = 0
fall.recover = 0
kill = 1
getpower = 0,0
givepower = 0,0
guard.dist = 300

[State {state}, Finish fixture strike]
type = ChangeState
trigger1 = Time >= 45
value = 0
ctrl = 1
'''
    return output


def install_fixtures(names):
    qa = fixture_controllers()
    for name in names:
        folder = GAME / 'chars' / name
        text = (folder / f'{name}.cns').read_text(encoding='utf-8')
        marker = '[Statedef -2]'
        if marker in text:
            text = text.replace(marker, marker + '\n' + qa, 1)
        else:
            text += '\n' + marker + '\n' + qa
        (folder / 'motion-qa.cns').write_text(text, encoding='utf-8')
        definition = re.sub(r'(?m)^st\s*=.*', 'st = motion-qa.cns',
                            (folder / f'{name}.def').read_text(encoding='utf-8'))
        (folder / 'motion-qa.def').write_text(definition, encoding='utf-8')
    folder = GAME / 'chars/chava'
    (folder / 'motion-dummy.cns').write_text(
        (folder / 'chava.cns').read_text(encoding='utf-8') + dummy_states(), encoding='utf-8')
    definition = (folder / 'chava.def').read_text(encoding='utf-8')
    definition = re.sub(r'(?m)^st\s*=.*', 'st = motion-dummy.cns', definition)
    definition = re.sub(r'(?m)^anim\s*=.*', 'anim = motion-dummy.air', definition)
    (folder / 'motion-dummy.def').write_text(definition, encoding='utf-8')
    (folder / 'motion-dummy.air').write_text((folder / 'chava.air').read_text(encoding='utf-8') + '''
[Begin Action 9800]
Clsn2Default: 1
Clsn2[0] = -20,-110,20,0
Clsn1Default: 1
Clsn1[0] = -180,-180,180,0
200,0, 0,0, -1
''', encoding='utf-8')


def lua_observer(name, csv_path, event_path):
    # Forward slashes and JSON quoting are valid Lua string literals here.
    csv_literal = json.dumps(str(csv_path).replace('\\', '/'))
    event_literal = json.dumps(str(event_path).replace('\\', '/'))
    return f'''
motionCaptured = motionCaptured or {{}}
if player(1) and var(58)>0 then
 local t=var(58)
 if t~=motionLastTick then
  motionLastTick=t
  local case=math.floor((t-10)/{SPAN})+1
  local values={{t,stateNo(),time(),anim(),animElemNo(0),ctrl() and 1 or 0,
    posX(),posY(),life(),roundState(),spriteVar("group"),spriteVar("image"),
    facing(),velX(),velY()}}
  local file=assert(io.open({csv_literal},"a"))
  file:write(table.concat(values,",").."\\n"); file:close()
  local key=case..":"..anim()
  local wanted={{[20]=true,[21]=true,[100]=true,[10]=true,[11]=true,[12]=true,
    [40]=true,[41]=true,[42]=true,[43]=true,[44]=true,[45]=true,[46]=true,[47]=true,
    [120]=true,[121]=true,[122]=true,[130]=true,[131]=true,[132]=true,
    [150]=true,[151]=true,[152]=true,[5000]=true,[5010]=true,[5020]=true,
    [5050]=true,[5060]=true,[5100]=true,[5110]=true,[5120]=true,[5150]=true}}
  if wanted[anim()] and not motionCaptured[key] then
   motionCaptured[key]=true
   screenshot()
   local events=assert(io.open({event_literal},"a"))
   events:write(table.concat({{t,case,stateNo(),anim(),spriteVar("group"),spriteVar("image")}},",").."\\n")
   events:close()
  end
  if t>={len(CASES)*SPAN-15} or (case=={len(CASES)} and stateNo()==5150 and time()>=15) then os.exit() end
 end
end
'''


def assess(rows):
    results = []
    for index, case in enumerate(CASES):
        first = index * SPAN + 10
        window = [row for row in rows if first + 11 <= row[0] < first + SPAN]
        states = {int(row[1]) for row in window}
        animations = {int(row[3]) for row in window}
        recovered = any(row[0] > first + 85 and row[1] == 0 and row[5] == 1
                        and abs(row[7]) < 0.05 for row in window)
        checks = {'observed_frames': bool(window)}
        x_travel = (window[-1][6] - window[0][6]) if len(window) > 1 else 0
        if case == 'walk_forward':
            checks.update(walking_state=20 in states, forward_animation=20 in animations,
                          advances=x_travel > .25, restores_standing_control=recovered)
        elif case == 'walk_backward':
            checks.update(walking_state=20 in states, backward_animation=21 in animations,
                          retreats=x_travel < -.25, restores_standing_control=recovered)
        elif case == 'run':
            checks.update(run_state=100 in states, run_animation=100 in animations,
                          advances=x_travel > .25,
                          restores_standing_control=recovered)
        elif case == 'crouch':
            checks.update(lower_hold_rise={10, 11, 12}.issubset(animations),
                          restores_standing_control=recovered)
        elif case == 'jump':
            checks.update(takeoff_air_landing={40, 50, 52}.issubset(states),
                          ascent_descent_landing={40, 41, 44, 47}.issubset(animations),
                          actually_airborne=any(row[7] < -10 for row in window),
                          restores_standing_control=recovered)
        elif 'guard' in case:
            guard = {'standing_guard': (130, 150), 'crouching_guard': (131, 151),
                     'air_guard': (132, 152)}[case]
            checks.update(guard_pose=guard[0] in animations, real_guard_reaction=guard[1] in animations,
                          no_damage=all(row[8] == 1000 for row in window),
                          restores_standing_control=recovered)
        elif case == 'knockdown_getup':
            checks.update(natural_fall_ground_down_getup={5050, 5100, 5110, 5120}.issubset(states),
                          getup_animation=5120 in animations,
                          restores_standing_control=recovered,
                          survives=all(row[8] > 0 for row in window))
        else:
            checks.update(defeated_state=5150 in states, life_is_zero=any(row[8] == 0 for row in window),
                          resting_on_floor=any(row[1] == 5150 and abs(row[7]) < .05 for row in window))
        results.append(dict(case=case, checks=checks, states=sorted(states),
                            animations=sorted(animations), frames=len(window), passed=all(checks.values())))
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('characters', nargs='*')
    parser.add_argument('--run', action='store_true', help='Run actual sequential engine matches')
    parser.add_argument('--engine', type=Path, default=ROOT / 'TheKingOfUTc.exe')
    parser.add_argument('--timeout', type=int, default=65)
    parser.add_argument('--realtime', action='store_true',
                        help='Disable speedtest to capture more individually rendered animation frames')
    args = parser.parse_args()
    names = args.characters or ROSTER
    if set(names) - set(ROSTER):
        parser.error('Unknown characters: ' + ', '.join(sorted(set(names) - set(ROSTER))))
    OUT.mkdir(parents=True, exist_ok=True)
    before = source_hashes()
    manifest = package(GAME, {'Video': {'RenderMode': 'OpenGL 3.3', 'Fullscreen': 0,
                                      'WindowWidth': 960, 'WindowHeight': 540}}, False)
    install_fixtures(names)
    if not args.run:
        print('Prepared isolated runtime fixture:', GAME)
        assert source_hashes() == before, 'Production game files changed'
        return
    engine = args.engine.resolve()
    env = dict(os.environ)
    env['PATH'] = str(engine.parent / 'lib') + os.pathsep + env.get('PATH', '')
    base_config = (GAME / 'save/config.ini').read_text(encoding='utf-8')
    (GAME / 'qa').mkdir(exist_ok=True)
    report = {'scope': 'Windows engine execution of production AIR/SFF and common states in an isolated fixture',
              'engine': str(engine), 'asset_count': manifest['file_count'],
              'playback': 'realtime' if args.realtime else 'speedtest', 'characters': {}}
    for name in names:
        folder = OUT / name
        folder.mkdir(exist_ok=True)
        csv_path, event_path = folder / 'frames.csv', folder / 'captures.csv'
        for path in (csv_path, event_path, *folder.glob('*.png')):
            if path.exists():
                path.unlink()
        (GAME / 'qa/observer.lua').write_text(lua_observer(name, csv_path, event_path), encoding='utf-8')
        config = update_ini(base_config, 'Common', {'Lua': 'loop(), dofile("qa/observer.lua")'})
        config = update_ini(config, 'Config', {'ScreenshotFolder': str(folder).replace('\\', '/')})
        config_path = folder / 'config.ini'
        config_path.write_text(config, encoding='utf-8')
        started = time.monotonic()
        arguments = [str(engine), '-config', str(config_path),
                '-p1', f'{name}/motion-qa.def', '-p2', 'chava/motion-dummy.def',
                '-s', 'stages/patio.def', '-rounds', '1', '-time', '-1',
                '-nosound', '-nojoy', '-windowed']
        if not args.realtime:
            arguments.append('-speedtest')
        attempts = []
        for attempt in range(3):
            try:
                process = subprocess.run(arguments, cwd=GAME, env=env,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=args.timeout)
                code, output = process.returncode, process.stdout.decode(errors='replace')
            except subprocess.TimeoutExpired as error:
                code, output = 'TIMEOUT', (error.stdout or b'').decode(errors='replace')
            attempts.append({'returncode': code, 'output_tail': output[-1800:]})
            # Some NVIDIA/Windows runs fail before graphics initialization.
            # Retry only this startup failure, never an executed gameplay case.
            if code not in (3221225480, -1073741816) or csv_path.exists():
                break
            print(name, 'renderer startup failed; retry', attempt + 1, flush=True)
            (folder / f'startup-attempt-{attempt + 1}.log').write_text(output, encoding='utf-8')
            time.sleep(1)
        (folder / 'stdout.log').write_text(output, encoding='utf-8')
        rows = [[float(value) for value in row] for row in csv.reader(csv_path.open())] if csv_path.exists() else []
        checks = assess(rows)
        failures = [case['case'] for case in checks if not case['passed']]
        report['characters'][name] = dict(returncode=code, seconds=round(time.monotonic() - started, 2),
            attempts=attempts,
            cases=checks, screenshot_count=len(list(folder.glob('*.png'))),
            passed=code == 0 and not failures, source_sha256=before[f'chars/{name}/{name}.sff'])
        print(name, 'PASS' if report['characters'][name]['passed'] else 'FAIL',
              'exit=', code, 'seconds=', report['characters'][name]['seconds'], 'failed=', failures, flush=True)
        report['production_assets_unchanged'] = source_hashes() == before
        report['passed'] = all(result['passed'] for result in report['characters'].values())
        (OUT / 'results.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        assert report['production_assets_unchanged'], 'Production game files changed'
    raise SystemExit(0 if report['passed'] else 1)


if __name__ == '__main__':
    main()
