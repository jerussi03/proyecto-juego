"""Build the game's illustrated dialogue cards and native SFF archive.

Source portraits are preserved as supplied; the layout frames them as cards.
Run with --source DIR on the first build, then sources are local to the game.
"""
from pathlib import Path
from io import BytesIO
import argparse
import json
import shutil
import struct
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/story'
FONT = Path('C:/Windows/Fonts')


def hero():
    raw = (ROOT / 'chars/chava/chava.sff').read_bytes()
    table, count = struct.unpack_from('<II', raw, 36)
    data = struct.unpack_from('<I', raw, 52)[0]
    for i in range(count):
        e = struct.unpack_from('<HHHHhhHBBIIHH', raw, table + 28*i)
        if e[0] == 0 and e[10] and e[7] in (10, 11, 12):
            return Image.open(BytesIO(raw[data+e[9]+4:data+e[9]+e[10]])).convert('RGBA')
    raise ValueError('No PNG standing sprite found for Chava')


def wrap(draw, text, font, width):
    lines = []
    for paragraph in text.split('\n'):
        line = ''
        for word in paragraph.split():
            candidate = (line + ' ' + word).strip()
            if draw.textlength(candidate, font=font) > width:
                lines.append(line)
                line = word
            else:
                line = candidate
        lines.append(line)
    return lines


def card(portrait, chapter, title, speaker, body, number, total):
    im = Image.new('RGB', (1280, 720), '#101920')
    d = ImageDraw.Draw(im)
    for y in range(0, 720, 32):
        d.line((0,y,1280,y), fill='#18232b')
    for x in range(0,1280,32):
        d.line((x,0,x,720), fill='#18232b')
    d.rectangle((0,0,1280,9), fill='#d5fa57')
    f = lambda size, bold=False: ImageFont.truetype(str(FONT / ('consolab.ttf' if bold else 'consola.ttf')), size)
    d.text((42,29), 'THE KING OF UTC / EXPEDIENTE DE CHAVA', font=f(20,True), fill='#d5fa57')
    d.text((42,64), chapter.upper(), font=f(20), fill='#bccbd4')
    title_font = f(35,True)
    while d.textlength(title, font=title_font) > 1180:
        title_font = f(title_font.size-1,True)
    d.text((42,98), title, font=title_font, fill='white')
    d.rectangle((40,162,420,639), fill='#e3e6df')
    thumb = ImageOps.contain(portrait, (366,459), method=Image.Resampling.NEAREST)
    xy = (230-thumb.width//2, 400-thumb.height//2)
    im.paste(thumb, xy, thumb if thumb.mode == 'RGBA' else None)
    d.rectangle((40,162,420,639), outline='#9aa995', width=2)
    d.rectangle((450,162,1240,639), fill='#17232e', outline='#3c5261', width=2)
    d.rectangle((450,162,457,639), fill='#d5fa57')
    d.text((488,191), speaker, font=f(25,True), fill='#d5fa57')
    body_font = f(30)
    lines = wrap(d, body, body_font, 706)
    assert len(lines) <= 9, (title, len(lines), body)
    for i, line in enumerate(lines):
        d.text((488,246+i*38), line, font=body_font, fill='#f0f3f4')
    d.text((488,600), f'DIÁLOGO {number:02d} / {total:02d}', font=f(17), fill='#a1b4c2')
    d.text((42,673), 'CONFIRMAR / ENTER: SIGUIENTE    IZQUIERDA: ANTERIOR    ESC: SALIR', font=f(20), fill='#bccbd4')
    return im


def sff(images):
    records, payloads = [], bytearray()
    for n, im in enumerate(images):
        buf = BytesIO()
        im.convert('RGBA').save(buf, format='PNG')
        payload = b'\0'*4 + buf.getvalue()
        records.append(struct.pack('<HHHHhhHBBIIHH', 0,n,1280,720,0,0,0,12,32,len(payloads),len(payload),0,0))
        payloads.extend(payload)
    offset = 512 + 28*len(records)
    header = bytearray(512)
    header[:12] = b'ElecbyteSpr\0'
    header[12:16] = bytes((0,1,0,2))
    struct.pack_into('<II',header,36,512,len(records))
    struct.pack_into('<II',header,52,offset,len(payloads))
    (OUT/'story.sff').write_bytes(header+b''.join(records)+payloads)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source', type=Path)
    args = p.parse_args()
    src = OUT/'portraits'
    src.mkdir(parents=True, exist_ok=True)
    data = json.loads((OUT/'chapters.json').read_text(encoding='utf-8'))
    chava = hero()
    images, groups = [], {}
    def add(key, part, portrait, label, pages):
        indexes = []
        for i, (speaker, body) in enumerate(pages):
            indexes.append(len(images))
            images.append(card(portrait, label, part['title'], speaker, body, i+1,len(pages)))
        groups[key] = indexes
    add('intro',data['intro'],chava,'Prólogo',data['intro']['pages'])
    for i, ch in enumerate(data['chapters']):
        target = src/ch['source']
        if args.source:
            shutil.copy2(args.source/ch['source'], target)
        portrait = Image.open(target).convert('RGB')
        add(ch['id'],ch,portrait,f"Capítulo {i+1:02d} / {ch['subject']}",ch['pages'])
        add(ch['id']+'_after',ch,portrait,'Materia aprobada' if ch.get('fighter') else 'Continuación de la historia',ch['after'])
    add('ending',data['ending'],chava,'Epílogo',data['ending']['pages'])
    sff(images)
    manifest = ['-- Generated by tools/build_story.py; edit chapters.json instead.', 'return {']
    for key, indexes in groups.items():
        manifest.append('  '+key+' = {'+','.join(map(str,indexes))+'},')
    manifest.append('}')
    (OUT/'pages.lua').write_text('\n'.join(manifest)+'\n',encoding='utf-8')
    preview = ROOT/'scratch/story-preview'
    preview.mkdir(parents=True,exist_ok=True)
    for key in ('intro','chan','alejandro','cesar','ending'):
        images[groups[key][0]].save(preview/(key+'.png'))
    # Real startup storyboard, same cards as the in-game reader.
    intro = ['[Info]','localcoord = 1280,720','[SceneDef]','spr = ../story/story.sff','startscene = 0']
    for i, n in enumerate(groups['intro']):
        intro += [f'[Scene {i}]','fadein.time = 15','fadeout.time = 15','clearcolor = 16,25,32',f'layer0.anim = {i}','end.time = 900',f'[Begin Action {i}]',f'0,{n},0,0,-1']
    (ROOT/'data/ikemen1/intro.def').write_text('\n'.join(intro)+'\n',encoding='utf-8')
    print(f'Built {len(images)} dialogue cards, 12 chapters, introduction and ending.')


if __name__ == '__main__':
    main()
