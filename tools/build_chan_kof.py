"""Create a playable Chan KOF revision without replacing the original Chan."""
from pathlib import Path
import json
import shutil
from PIL import Image, ImageOps
import build_felix as sprites

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'chars/chava'
TARGET = ROOT / 'chars/chan_kof'
ART = TARGET / 'art'


def main():
    ART.mkdir(parents=True, exist_ok=True)
    sprites.ART = ART
    sprites.SHEETS = [ART / 'chan-idle-walk-punch-uppercut.png',
                      ART / 'chan-kick-sweep-jump-guard.png']
    assert all(p.is_file() for p in sprites.SHEETS)
    for name in ('chava.cmd', 'chava.cns', 'chava.air', 'chava.snd',
                 'kof-extra.cns', 'chava-movelist.dat'):
        shutil.copy2(SOURCE / name, TARGET / name.replace('chava', 'chan_kof'))
    definition = (SOURCE / 'chava.def').read_text(encoding='utf-8')
    definition = definition.replace('Chava', 'Chan').replace('CHAVA', 'CHAN')
    definition = definition.replace('protagonista de Ingenieria en Sistemas', 'maestra de Bases de Datos')
    definition = definition.replace('chava.', 'chan_kof.').replace('chava-', 'chan_kof-')
    (TARGET / 'chan_kof.def').write_text(definition, encoding='utf-8')
    move_list = TARGET / 'chan_kof-movelist.dat'
    descriptions = move_list.read_text(encoding='utf-8')
    for old, new in {
        'CHAVA / CONTROLES KOF': 'CHAN / BASES DE DATOS KOF',
        'Codigo compilado': 'Consulta SELECT',
        'Codigo, alternativa U': 'Consulta ordenada',
        'Gancho compilacion': 'Revision estricta',
        'Mochilazo de avance': 'Correccion de entrega',
        'Barrida de semestre': 'Barrida de papeles',
        'Asistente IA': 'Examen sorpresa',
        'Entrega final': 'Documentacion perfecta',
        'Compilacion final + IA': 'Consulta definitiva',
    }.items():
        descriptions = descriptions.replace(old, new)
    move_list.write_text(descriptions, encoding='utf-8')
    frames = sprites.load_frames()
    source = Image.open(ROOT / 'data/story/portraits/chan_basededatos.jpeg').convert('RGBA')
    face = source.crop((325, 40, 650, 360))
    portraits = {0: ImageOps.fit(face, (24, 24), method=Image.Resampling.LANCZOS),
                 1: ImageOps.fit(face, (120, 140), method=Image.Resampling.LANCZOS)}
    result, count = sprites.replace_sff((SOURCE / 'chava.sff').read_bytes(), frames, portraits)
    (TARGET / 'chan_kof.sff').write_bytes(result)
    (ART / 'manifest.json').write_text(json.dumps({
        'design_reference': 'chan_basededatos.jpeg',
        'sheets': [p.name for p in sprites.SHEETS], 'poses': 48,
        'sprite_slots_replaced': count,
        'gameplay_reference': 'Chava KOF controls',
        'limitations': 'Technology projectile and voice temporarily reuse Chava assets.'
    }, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'Chan KOF: 48 poses, {count} fighter sprite slots replaced')
    from build_teacher_specials import apply_character
    apply_character('chan_kof')


if __name__ == '__main__':
    main()
