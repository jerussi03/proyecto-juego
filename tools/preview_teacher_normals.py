"""Capture four authored attacks per teacher at normal engine speed.

Uses isolated, ignored fixtures; preserves the real character files and config.
"""
from pathlib import Path
import re
import subprocess

from build_teacher_specials import PROFILES, ctl
from teacher_normals import KITS

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'scratch/identity-preview/normals'


def main():
    original = (ROOT / 'save/config.ini').read_bytes()
    for id in PROFILES:
        folder = ROOT / 'chars' / id
        dest = OUT / id
        dest.mkdir(parents=True, exist_ok=True)
        qa = ctl(-2, 'Preview clock', 'VarAdd', 'v = 58\nvalue = 1', '!IsHelper && RoundState=2')
        steps = []
        for index, target in enumerate((210, 410, 610, 640)):
            start = 1 + index * 85
            test = f'!IsHelper && var(58)={start} && RoundState=2'
            for kind, params in [
                ('PosSet', f'x = -55-CameraPos X\ny = {-65 if target >= 600 else 0}'),
                ('VelSet', 'x = 0\ny = 0'),
                ('PosSet', 'x = 45-CameraPos X\ny = 0\nredirectID = EnemyNear,ID'),
                ('ChangeState', f'value = {target}\nctrl = 0'),
            ]:
                qa += ctl(-2, 'Preview action', kind, params, test)
            # Lua observes state time before that frame is presented. Capture
            # two ticks into the active element so the saved image is extended.
            steps.append((target, start, KITS[id][target].startup + 2))
        source = (folder / f'{id}.cns').read_text(encoding='utf-8')
        (folder / 'identity-preview.cns').write_text(source.replace('[Statedef -2]', '[Statedef -2]\n' + qa, 1), encoding='utf-8')
        definition = re.sub(r'(?m)^st\s*=.*', 'st = identity-preview.cns', (folder / f'{id}.def').read_text(encoding='utf-8'))
        (folder / 'identity-preview.def').write_text(definition, encoding='utf-8')
        observer = 'if player(1) and roundState()==2 then\n'
        for index, (target, start, startup) in enumerate(steps):
            observer += f' if var(58)>={start} and var(58)<{start+85} and stateNo()=={target} and time()>={startup} and not captured{index} then captured{index}=true; screenshot() end\n'
        observer += ' if var(58)>340 then os.exit() end\nend\n'
        (dest / 'observer.lua').write_text(observer, encoding='utf-8')
        config = original.decode('utf-8-sig')
        relative = dest.relative_to(ROOT).as_posix()
        config = re.sub(r'(?m)^Lua\s*=.*', f'Lua = loop(), dofile("{relative}/observer.lua")', config)
        config = re.sub(r'(?m)^ScreenshotFolder\s*=.*', f'ScreenshotFolder = {relative}', config)
        config = re.sub(r'(?m)^Fullscreen\s*=.*', 'Fullscreen = false', config)
        (dest / 'config.ini').write_text(config, encoding='utf-8')
        before = set(dest.glob('*.png'))
        run = subprocess.run([str(ROOT / 'TheKingOfUTc.exe'), '-config', str(dest / 'config.ini'), '-p1', f'{id}/identity-preview.def', '-p2', 'chava', '-s', 'stages/patio.def', '-rounds', '1', '-time', '-1', '-nosound', '-windowed'], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=25)
        assert run.returncode == 0, (id, run.stdout.decode(errors='replace')[-1500:])
        count = len(set(dest.glob('*.png')) - before)
        assert count == 4, (id, 'expected four fresh contact captures', count)
        print(id, 'four contacts captured at normal speed', flush=True)
    assert (ROOT / 'save/config.ini').read_bytes() == original


if __name__ == '__main__':
    main()
