"""Validate imported controls, preserved gameplay, provenance and match logs."""
import json
import re
from import_kof_bases import ROOT, PACKS, adapt_commands

manifest = json.loads((ROOT / 'data/kof-bases.json').read_text(encoding='utf-8'))
assert len(manifest) == len(PACKS) == 6
for item in manifest:
    source = ROOT / 'downloads/kof-bases' / item['base'] / item['base']
    definition = ROOT / 'chars' / item['definition']
    target = definition.parent
    assert definition.is_file()
    assert (target / 'utc-movelist.dat').is_file()
    for cmd in source.glob('*.cmd'):
        actual = (target / cmd.name).read_bytes()
        expected, counts = adapt_commands(cmd.read_bytes())
        assert actual == expected, (item['base'], 'command import drift')
        assert counts['roll_shortcuts'] >= 1
        assert counts['max_shortcuts'] >= 1
    # Input adaptation must not change frame data, collision boxes, AI or art.
    for original in source.iterdir():
        if original.suffix.lower() in {'.cns', '.air', '.sff', '.snd'}:
            assert (target / original.name).read_bytes() == original.read_bytes()
    print('PASS controls and unchanged gameplay/art:', item['base'])
for number in range(1, 4):
    log = ROOT / f'scratch/kof-base-match-{number}.log'
    text = log.read_text()
    assert re.search(r'\["LastRound"\] => [1-9]', text), log
    assert len(re.findall(r'\["Name"\]', text)) >= 2, log
    print('PASS completed engine match:', log.name)
