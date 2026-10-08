"""Validate the new roster and finish one real engine fight per teacher."""
from pathlib import Path
import json
import re
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
ROSTER = json.loads((ROOT / 'data/utc-roster.json').read_text(encoding='utf-8'))


def main():
    original_config = (ROOT / 'save/config.ini').read_bytes()
    original_controls = (ROOT / 'chars/chava/chava.cmd').read_bytes()
    results = []
    for spec in ROSTER:
        name = spec['id']
        commands = (ROOT / f'chars/{name}/{name}.cmd').read_bytes().split(b'[Statedef -1]')[0].replace(b'\r\n', b'\n')
        assert commands == original_controls.split(b'[Statedef -1]')[0].replace(b'\r\n', b'\n')
        assert (ROOT / f'chars/{name}/art/specials/gameplay.json').is_file()
        log = ROOT / f'scratch/{name}-match.log'
        started = time.time()
        process = subprocess.run([
            str(ROOT / 'TheKingOfUTc.exe'), '-p1', f'{name}/{name}.def',
            '-p2', 'chava', '-p1.ai', '8', '-p2.ai', '8', '-rounds', '1',
            '-time', '8', '-speedtest', '-nosound', '-windowed', '-log', str(log)
        ], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
        output = process.stdout.decode(errors='replace')
        assert process.returncode == 0, (name, process.returncode, output[-2000:])
        assert log.exists() and log.stat().st_mtime >= started - 2, (name, 'no fresh match log', output[-2000:])
        data = log.read_text(encoding='utf-8')
        last_round = re.search(r'\["LastRound"\] => (\d+)', data)
        assert last_round and int(last_round[1]) >= 1 and '["Win"] => true' in data, (name, 'match did not complete')
        assert f'["Name"] => "{spec["name"]}"' in data, (name, 'wrong fighter loaded')
        assert '["Name"] => "Chava"' in data
        assert 'error' not in output.lower(), (name, output[-2000:])
        results.append({'character': name, 'passed': True, 'controls_unchanged': True,
                        'log': str(log.relative_to(ROOT))})
        print(name, 'PASS: real match completed; original commands retained', flush=True)
    assert (ROOT / 'save/config.ini').read_bytes() == original_config, 'Global input settings changed'
    (ROOT / 'scratch/utc-roster-validation.json').write_text(json.dumps(results, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
