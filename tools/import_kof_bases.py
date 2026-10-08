"""Import downloaded Ikaruga bases; preserve global input configuration.

The imported fighters retain original names and artwork until full UTC sprite
sets are ready. Source archives are never modified. Run from any directory.
"""
from pathlib import Path
import hashlib
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
PACKS = ['Kyo-KOF02UM', 'TerryEX-KOF02UM', 'RyoEX-KOF02UM',
         'Iori-KOF02UM', "K'-KOF02UM", 'Nameless-KOF02UM']


def adapt_commands(raw):
    # Latin-1 is a byte-preserving transport for Japanese command identifiers.
    text = raw.decode('latin1')
    boundary = re.search(r'(?im)^\[Statedef\s+-1\]', text).start()
    commands, states = text[:boundary], text[boundary:]
    blocks = re.split(r'(?im)(?=^\[Command\])', commands)
    roll_added = max_changed = cd_changed = 0
    result = []
    for block in blocks:
        sequence = re.search(r'(?im)^command\s*=\s*([^;\r\n]+)', block)
        if not sequence:
            result.append(block)
            continue
        value = sequence[1].strip().replace(' ', '')
        # Only shortcut definitions identified by their shared command name;
        # leave generic c/z input detectors intact for the author's AI.
        name = re.search(r'(?im)^name\s*=\s*"([^"]+)"', block)[1]
        siblings = [b for b in blocks if re.search(
            r'(?im)^name\s*=\s*"' + re.escape(name) + '"', b)]
        combined = '\n'.join(siblings)
        if value == 'c' and re.search(r'(?im)^command\s*=\s*a\+y\s*$', combined):
            block = block[:sequence.start(1)] + 'z' + block[sequence.end(1):]
            max_changed += 1
        elif value == 'z' and re.search(r'(?im)^command\s*=\s*y\+b\s*$', combined):
            block = block[:sequence.start(1)] + 'y+b' + block[sequence.end(1):]
            cd_changed += 1
        result.append(block)
        if value == 'x+a':
            shortcut = block[:sequence.start(1)] + 'c' + block[sequence.end(1):]
            result.append(shortcut)
            roll_added += 1
    assert roll_added and max_changed and cd_changed, 'Unknown base input layout'
    return (''.join(result) + states).encode('latin1'), dict(
        roll_shortcuts=roll_added, max_shortcuts=max_changed, cd_shortcuts_removed=cd_changed)


def add_movelist(target):
    manual = (target / 'txt/ReadMe(ENG).txt').read_text(encoding='cp932')
    moves = manual.split('=====<Movelist>=====')[1].split('=====<Credits>=====')[0]
    moves = moves.replace('z - Knockdown Attack', 'z - Maximum Mode (RB / teclado D)')
    moves = moves.replace('c - Maximum Mode', 'c - Roll (RT / teclado C)')
    moves = moves.replace('y+b or z', 'y+b').replace('Roll - x+a', 'Roll - x+a or c')
    moves = moves.replace('Maximum Mode - a+y', 'Maximum Mode - a+y or z')
    header = ('<#abf2eb>:BASE KOF 2002 UM / IKARUGA:</>\n'
              'KOF A / B / C / D = ^X / ^A / ^Y / ^B\n'
              'Atajos UTC: ^C evasión / ^Z MAX\n'
              'Graficos originales; conversion UTC pendiente.\n')
    (target / 'utc-movelist.dat').write_text(header + moves, encoding='utf-8')
    for definition in target.glob('*.def'):
        raw = definition.read_bytes()
        if b'movelist = utc-movelist.dat' not in raw:
            raw = raw.replace(b'[Files]', b'[Files]\r\nmovelist = utc-movelist.dat')
            definition.write_bytes(raw)


def main():
    config = ROOT / 'save/config.ini'
    before = hashlib.sha256(config.read_bytes()).hexdigest()
    manifest = []
    for pack in PACKS:
        source = ROOT / 'downloads/kof-bases' / pack / pack
        target = ROOT / 'chars' / ('base-' + pack.replace("'", 'prime'))
        if target.exists():
            raise SystemExit(f'Refusing to overwrite existing import: {target}')
        shutil.copytree(source, target, ignore=shutil.ignore_patterns('Thumbs.db', 'desktop.ini', '*.ico'))
        changes = {}
        for cmd in target.glob('*.cmd'):
            updated, counts = adapt_commands(cmd.read_bytes())
            cmd.write_bytes(updated)
            changes[cmd.name] = counts
        add_movelist(target)
        archive = ROOT / 'downloads/kof-bases' / (pack + '.zip')
        manifest.append(dict(base=pack, author='Ikaruga',
            definition=f'{target.name}/{pack}.def',
            source='http://ikrgmugen.web.fc2.com/kof02um.html',
            sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
            adaptation=changes, artwork='Original KOF; UTC animation replacement pending'))
    output = ROOT / 'data/kof-bases.json'
    output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    select = ROOT / 'data/select.def'
    selection = select.read_text(encoding='utf-8-sig')
    assert '; BEGIN KOF BASES' not in selection
    block = '; BEGIN KOF BASES - original artwork / UTC controls\n'
    block += '\n'.join(f"{item['definition']}, stages/patio.def, order=0" for item in manifest)
    block += '\n; END KOF BASES\n\n'
    selection = selection.replace('[ExtraStages]', block + '[ExtraStages]')
    select.write_text(selection, encoding='utf-8')
    assert hashlib.sha256(config.read_bytes()).hexdigest() == before
    print(json.dumps({'imported': len(manifest), 'config_sha256': before}, indent=2))


if __name__ == '__main__':
    main()
