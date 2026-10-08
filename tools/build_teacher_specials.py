"""Install original subject/hobby specials without changing any input definitions.

The source sheets and exact ImageGen prompts live in each character's art/specials.
Re-running this builder replaces its own sprite slots, actions and controllers.
"""
from pathlib import Path
from io import BytesIO
import argparse
import hashlib
import json
import re
import shutil
import struct
import time
import numpy as np
import cv2
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
HEADER = '<HHHHhhHBBIIHH'
START = '; BEGIN TEACHER SPECIALS'
END = '; END TEACHER SPECIALS'

# Gameplay differences are intentional, not just different move names.
PROFILES = {
    'chan_kof': dict(name='Chan', moves=['Examen SQL','Peso de Crossfit','Ruta de Senderismo','Indice Cluster','Documentacion Perfecta','Circuito de Crossfit','Crossfit Total','DROP TABLE MAX2'], speed=5.8, damage=54, stun=27, advance=3.8, rush=78, utility='charge', gain=200, cost=0, cooldown=200, shots=5, interval=13, arc=0),
    'felix': dict(name='Felix', moves=['Llave de Soporte','Reinicio Forzado','Reparacion en Marcha','Cable a Tierra','Mantenimiento Preventivo','Reinicio en Cadena','Reparacion General','Restaurar Sistema MAX2'], speed=4.6, damage=68, stun=20, advance=3.0, rush=84, utility='heal', heal=40, cost=150, cooldown=360, shots=4, interval=18, arc=0),
    'alejandro': dict(name='Alejandro', moves=['Componente Angular','Inyeccion de Dependencias','ng serve','Error de Compilacion','Importar Modulo','Refactorizacion','Build de Produccion','Deploy MAX2'], speed=7.6, damage=47, stun=17, advance=0, rush=65, utility='buff', cost=0, cooldown=300, shots=6, interval=10, arc=0),
    'daniela': dict(name='Daniela', moves=['Diagrama UML','Revision de Negocio','Bolsazo de Requisitos','Cambio de Alcance','Documento Aprobado','Victor, Echame la Mano','Entrega Documentada','Auditoria MAX2'], speed=5.3, damage=59, stun=24, advance=4.0, rush=76, utility='charge', gain=180, cost=0, cooldown=210, shots=5, interval=14, arc=0),
    'gameros': dict(name='Gameros', moves=['Gamepad Arcade','Rep de Gimnasio','Rodada en Moto','Pedal a Fondo','Modo Gym','Combo de Gimnasio','Full Throttle','Final Boss MAX2'], speed=6.6, damage=55, stun=18, advance=7.4, rush=74, utility='charge', gain=220, cost=0, cooldown=240, shots=5, interval=12, arc=0),
    'armando': dict(name='Armando', moves=['Saque de Pingpong','Clavada de Basquet','Impresion en Movimiento','Rebote Conectado','Calibrar IoT','Clavada Final','Torneo de Basquet','Internet de los Golpes MAX2'], speed=5.2, damage=52, stun=19, advance=4.2, rush=80, utility='buff', cost=0, cooldown=300, shots=6, interval=13, arc=1),
    'vladimir': dict(name='Vladimir', moves=['Invitacion Obligatoria','Pase al Frente','Nadie se Va','Honores al Sol','Pase de Lista','Conferencia Obligatoria','Recorrido de Salones','Asistencia Total MAX2'], speed=5.0, damage=50, stun=25, advance=0, rush=82, utility='charge', gain=180, cost=0, cooldown=240, shots=5, interval=16, arc=0),
    'jaime': dict(name='Jaime', moves=['Salto del Caballo','Potencia al Cuadrado','Sprint en Bicicleta','Derivada al Piso','Calculo Mental','Gambito Ciclista','Tour de Integrales','Teorema Final MAX2'], speed=4.4, damage=61, stun=21, advance=6.4, rush=78, utility='charge', gain=200, cost=0, cooldown=230, shots=5, interval=15, arc=2),
    'leonardo': dict(name='Leonardo', moves=['Notificacion Push','Actualizar App','Swipe Elegante','Scroll Infinito','Modo Avion','Contraataque Movil','Release Movil','Actualizacion MAX2'], speed=8.8, damage=43, stun=17, advance=0, rush=63, utility='evade', cost=100, cooldown=180, shots=7, interval=9, arc=0),
    'cesar': dict(name='Cesar', moves=['Consulta PHP','Baston del Backend','Silla de Apoyo','DELETE Sin WHERE','Pausa de Recuperacion','Empuje de Backend','Revision Estricta','Examen Final MAX2'], speed=3.8, damage=74, stun=24, advance=2.6, rush=92, utility='heal', heal=65, cost=200, cooldown=420, shots=4, interval=20, arc=0),
}

from teacher_identity import IDENTITIES
for identity,profile in PROFILES.items():
    profile.update(IDENTITIES[identity])
    if identity in {'chan_kof','jaime'}: profile['utility']='prepare'
    if identity=='gameros': profile['utility']='buff'
PROFILES['alejandro']['moves'][2]='Paso de Refactorizacion'
PROFILES['gameros']['moves'][0]='Combo Arcade'
PROFILES['gameros']['moves'][1]='Patada de Gimnasio'
PROFILES['armando']['moves'][2]='Sensor Impreso'
PROFILES['leonardo']['moves'][0]='Push de Patadas'
PROFILES['cesar']['moves'][0]='Baston PHP'
PROFILES['alejandro']['cooldown']=90
PROFILES['armando']['cooldown']=120


def state(n, anim, move='A', kind='S', cost=0):
    return f'\n[Statedef {n}]\ntype = {kind}\nmovetype = {move}\nphysics = N\nanim = {anim}\nctrl = 0\nvelset = 0,0\npoweradd = {-cost}\n'


def ctl(n, label, kind, params, trigger='Time = 0'):
    return f'\n[State {n}, {label}]\ntype = {kind}\ntrigger1 = {trigger}\n{params}\n'


def end(n, ticks=None):
    return ctl(n, 'Recovery', 'ChangeState', 'value = 0\nctrl = 1', f'Time >= {ticks}' if ticks else 'AnimTime = 0')


def fx(n, anim=8703, x=24, y=-60, duration=24):
    return ctl(n, 'Subject effect', 'Explod', f'anim = {anim}\nID = 8790\npostype = p1\npos = {x},{y}\nbindtime = -1\nremovetime = {duration}\nsprpriority = 5\nremoveongethit = 1\nownpal = 1')


def helper(n, child, x=35, y=-58, trigger='Time = 12', identity=None):
    return ctl(n, 'Subject helper', 'Helper', f'name = "Teacher special"\nhelpertype = normal\nID = {identity or child}\nstateno = {child}\npostype = p1\npos = {x},{y}\nfacing = 1\nkeyctrl = 0\nownpal = 1\nsupermovetime = 30', trigger)


def hit(n, damage, trigger='AnimElem = 4', projectile=False, supermove=False,
        low=False, fall=False, velocity='-4', stun=20, lift=False):
    attr = ('A,' + ('HP' if supermove else 'SP')) if projectile else ('C,' if low else 'S,') + ('HA' if supermove else 'SA')
    chip=max(3,damage//12) if isinstance(damage,int) else 8
    return ctl(n, 'Contact', 'HitDef', f'''attr = {attr}
damage = {damage},{chip}
animtype = Heavy
guardflag = {'L' if low else 'MA'}
hitflag = MAF
priority = 4,Hit
pausetime = {0 if projectile else 6},9
sparkno = {'-1' if projectile else '2'}
guard.sparkno = 40
sparkxy = -8,-60
hitsound = F5,2
guardsound = F6,0
ground.type = {'Low' if low else 'High'}
ground.slidetime = 14
ground.hittime = {stun}
ground.velocity = {velocity}{',-7' if lift else ''}
air.velocity = -3,-5
air.hittime = 24
fall = {int(fall)}
fall.recover = 0
getpower = {0 if projectile or supermove else 30},0
givepower = 18,9''', trigger)


def projectile(n, p, supermove=False, utility=False):
    anim = 8703 if utility else 8700
    speed = p['speed']
    falling = p['arc'] or utility
    out = state(n, anim, kind='A')
    out += ctl(n, 'Travel', 'VelSet', f'x = {speed}\ny = '+('-3.5' if p['arc']==2 else '-1.0' if p['arc']==1 else '4.8' if utility else '0'))
    if falling and not utility:
        out += ctl(n,'Gravity','VelAdd','y = '+('0.20' if p['arc']==2 else '0.28'),'1')
        if p['arc']==1:
            out += ctl(n,'Calibrated serve snapshot','VarSet','v = 3\nvalue = Root,var(44)')
            out += ctl(n,'Calibrated lateral rebound','VelMul','x = -1','var(3)>0 && ((FrontEdgeDist<12 && Vel X>0) || (BackEdgeDist<12 && Vel X<0))')
            out += ctl(n,'Bounce count','VarAdd','v = 1\nvalue = 1','Pos Y >= -12 && Vel Y > 0')
            out += ctl(n,'Pingpong bounce','VelSet','y = -4.0','Pos Y >= -12 && Vel Y > 0')
            out += ctl(n,'Bounce position','PosSet','y = -12','Pos Y > -12')
            out += ctl(n,'Bounce limit','DestroySelf','', 'var(1) >= 3+var(3)')
        else:
            out += ctl(n,'Ground end','ChangeState','value = 3021','Pos Y >= -8 && Vel Y > 0')
    if utility:
        out += ctl(n,'Sun path','VelSet','x = 0\ny = 4.8','1')
        out += ctl(n,'Floor','ChangeState','value = 3021','Pos Y >= -12')
    out += ctl(n,'No push','PlayerPush','value = 0','1')
    out += ctl(n,'Projectile trade','HitOverride','attr = SCA,AA,AP,AT\nslot = 0\nstateno = 3021\ntime = 1','1')
    velocity = '2.6' if p['name']=='Vladimir' else '-4'
    out += hit(n, 31 if supermove else 62 if utility else p['damage'], trigger='Time = 0', projectile=True, supermove=supermove, velocity=velocity, stun=p['stun'])
    if n==1005:
        out += ctl(n,'MAX projectile confirm','ParentVarSet','v = 43\nvalue = 1','MoveContact')
    out += ctl(n,'Impact','ChangeState','value = 3021','MoveContact')
    out += ctl(n,'Cleanup','DestroySelf','',f'Time > {180 if p["arc"]==1 else 100}\ntrigger2 = FrontEdgeDist < -90\ntrigger3 = RoundState != 2\ntrigger4 = Root,Life <= 0')
    return out


def special_cns(id, p):
    from teacher_identity import build, maximum
    from teacher_super_variants import build as super_variant, extra, second
    out = build(id,p,state,ctl,hit,end,helper,projectile)
    out += super_variant(id,p,3000,state,ctl,hit,end)
    out += second(id,p,state,ctl,hit,end)
    out += maximum(id,state,ctl,hit,end,helper)
    out += extra(id,state,ctl,hit,end)
    return out


def extract_sheet(path, id):
    sheet=Image.open(path).convert('RGBA')
    # AI sheets may put feet below a nominal grid boundary. Locate complete
    # silhouettes on the entire sheet instead of slicing off those feet or
    # accidentally adding them to the device in the next row.
    rgba=np.asarray(sheet)
    mask=cv2.dilate((rgba[:,:,3]>100).astype(np.uint8),np.ones((3,3),np.uint8),iterations=2)
    _,labels,stats,centers=cv2.connectedComponentsWithStats(mask,8)
    frames={}
    out=path.parent
    preview=Image.new('RGB',(768,512),(24,30,39))
    for row in range(4):
        # Every body frame uses the same scale. Arms, a handbag swing, a bike
        # or a tucked jump must not cause the teacher to grow/shrink per frame.
        # Fixed calibrations reviewed against each teacher's packed normal
        # head/body size. A whole signature keeps one scale across all frames.
        body_scale={'chan_kof':.40,'felix':.38,'alejandro':.37,'daniela':.42,
                    'gameros':.40,'armando':.40,'vladimir':.42,'jaime':.40,
                    'leonardo':.34,'cesar':.40}[id]
        for col in range(6):
            cx=(col+.5)*sheet.width/6; cy=(row+.5)*sheet.height/4
            choices=[i for i in range(1,len(stats)) if stats[i,4]>300 and abs(centers[i,0]-cx)<110 and abs(centers[i,1]-cy)<135]
            assert choices,(id,row,col,'empty cell')
            component=max(choices,key=lambda i:stats[i,4])
            x,y,w,h,_=stats[component]
            box=(max(0,x-6),max(0,y-6),min(sheet.width,x+w+6),min(sheet.height,y+h+6))
            keep=cv2.dilate((labels==component).astype(np.uint8),np.ones((3,3),np.uint8),iterations=1)
            selected=rgba.copy()
            selected[:,:,3]=selected[:,:,3]*keep
            sprite=Image.fromarray(selected).crop(box)
            sprite.putalpha(sprite.getchannel('A').point(lambda a:a if a>=40 else 0))
            tight=sprite.getchannel('A').getbbox()
            assert tight,(id,row,col)
            sprite=sprite.crop(tight)
            box=(box[0]+tight[0],box[1]+tight[1],box[0]+tight[2],box[1]+tight[3])
            # Body matches the existing ~110px-tall UTC cast. Motor/bike body
            # keeps this same scale; wide props have a separate size cap.
            cap={0:(42,32),1:(146,112),2:(78,84),3:(52,46)}[row]
            scale=min(cap[0]/sprite.width,cap[1]/sprite.height)
            if row==1: scale=body_scale
            sprite=sprite.resize((max(1,round(sprite.width*scale)),max(1,round(sprite.height*scale))),Image.Resampling.NEAREST)
            axis=(round((cx-box[0])*scale),sprite.height) if row==1 else (sprite.width//2,sprite.height) if row==2 else (sprite.width//2,sprite.height//2)
            frames[8700+row,col]=(sprite,*axis)
            sprite.save(out/f'{row}-{col}.png')
            preview.paste(sprite,(col*128+(128-sprite.width)//2,row*128+112-sprite.height),sprite)
        ImageDraw.Draw(preview).text((3,row*128+3),['Projectile','Signature','Device','Support'][row],fill='white')
    preview.save(out/'preview.png')
    return frames


def write_binary(path,packed):
    # OneDrive may briefly lock a synchronized binary between reads/writes.
    for attempt in range(12):
        try:
            path.write_bytes(packed)
            return
        except OSError:
            if attempt==11: raise
            time.sleep(.25)


def upsert_sff(path, frames):
    blob=bytearray(path.read_bytes())
    tableoff,count=struct.unpack_from('<II',blob,36)
    ldata=struct.unpack_from('<I',blob,52)[0]
    entries=[bytearray(blob[tableoff+i*28:tableoff+(i+1)*28]) for i in range(count)]
    present={struct.unpack_from('<HH',e):i for i,e in enumerate(entries)}
    for key in frames:
        if key not in present:
            present[key]=len(entries)
            entries.append(bytearray(struct.pack(HEADER,*key,0,0,0,0,0,0,0,0,0,0,0)))
    tableoff=len(blob)
    start=tableoff+len(entries)*28
    payload=bytearray()
    for key,(im,ax,ay) in frames.items():
        stream=BytesIO(); im.save(stream,format='PNG')
        raw=struct.pack('<I',im.width*im.height*4)+stream.getvalue()
        entries[present[key]]=struct.pack(HEADER,*key,im.width,im.height,ax,ay,0,11,32,start+len(payload)-ldata,len(raw),0,0)
        payload.extend(raw)
    struct.pack_into('<II',blob,36,tableoff,len(entries))
    struct.pack_into('<I',blob,56,start+len(payload)-ldata)
    packed=blob+b''.join(entries)+payload
    write_binary(path,packed)


def actions(id):
    out='\n'+START+'\n'
    for action,group,ticks,loop,collision in [(8700,8700,3,True,'shot'),(8702,8702,5,True,None),(8703,8703,4,True,'shot'),(8704,8701,8,True,'gate'),(8705,8700,2,False,None),(8720,8701,6,False,'body'),(8721,8701,9,False,'body'),(8734,8701,9,False,'cycling')]:
        out+=f'\n[Begin Action {action}]\n'
        if collision=='shot':
            out+='Clsn1Default: 1\nClsn1[0] = -18,-14,18,14\nClsn2Default: 1\nClsn2[0] = -18,-14,18,14\n'
        elif collision=='gate':
            out+='Clsn1Default: 1\nClsn1[0] = -35,-96,35,-5\n'
        elif collision in ['body','cycling']:
            out+='Clsn2Default: 1\nClsn2[0] = -22,-98,22,0\n'
        for i in range(6):
            if collision=='cycling' or collision=='body' and i in [2,3,4]:
                out+='Clsn1: 1\nClsn1[0] = 12,-88,72,-22\n'
            out+=f'{group},{i}, 0,0, {ticks}\n'
    for action in [8730,8732,8733,8735]:
        out+=f'\n[Begin Action {action}]\nClsn2Default: 1\nClsn2[0] = -22,-98,22,0\n'
        if action==8730:
            for group in [200,240,410]:
                for i in [1,2,3,4]:
                    out+='Clsn1: 1\nClsn1[0] = 10,-104,78,-14\n'
                    out+=f'{group},{i}, 0,0, 4\n'
        elif action==8735:
            out+='Clsn1Default: 1\nClsn1[0] = 8,-110,58,-25\n'
            out+=''.join(f'410,{i}, 0,0, 4\n' for i in range(6))
        elif action==8732:
            out+='Clsn1Default: 1\nClsn1[0] = -84,-32,84,0\n8701,5, 0,0, 22\n'
        else:
            out+='Clsn1Default: 1\nClsn1[0] = 8,-85,58,-8\n'
            out+=''.join(f'200,{i%5}, 0,0, 8\n' for i in range(6))
    out+='\n[Begin Action 8736]\nClsn2Default: 1\nClsn2[0] = -22,-98,22,0\n'
    for i in range(15):
        out+='Clsn1: 1\nClsn1[0] = 10,-92,82,-14\n'
        out+=f'240,{[1,2,3,4,3][i%5]}, 0,0, 4\n'
    from teacher_identity import actions as identity_actions
    return out+identity_actions(id)+END+'\n'


def clean_generated(text):
    return re.sub(r'\s*'+re.escape(START)+r'.*?'+re.escape(END)+r'\s*','\n\n',text,flags=re.S).rstrip()+'\n'


def commands(p,id):
    cond='!IsHelper\ntriggerall = RoundState = 2\ntriggerall = StateType != A\ntriggerall = Ctrl\ntriggerall = var(48) = 0\ntriggerall = Power >= '+str(p['cost'])
    extra = '\n'+START+'\n'
    extra += ctl(-1,'Teacher support QCB kick','ChangeState','value = 1040','command = "qcb_a" || command = "qcb_b"\ntriggerall = '+cond+'\ntriggerall = AILevel = 0')
    extra += ctl(-1,'CPU support','ChangeState','value = 1040','Random < AILevel * 2\ntriggerall = '+cond+'\ntriggerall = AILevel > 0\ntriggerall = P2BodyDist X > 110'+('\ntriggerall = Life < 850' if p['utility']=='heal' else ''))
    # Existing CPU only used the common AI tutor. Use all four real specials.
    from teacher_identity import COUNTERS, PROJECTILE_USERS
    choice='ifelse(P2BodyDist X>100,1000,ifelse(Random<500,1010,1030))' if id in PROJECTILE_USERS else 'ifelse(P2BodyDist X>90,1020,ifelse(Random<350,1000,ifelse(Random<500,1010,1030)))'
    if id in COUNTERS: choice=f'ifelse(P2MoveType=A && P2BodyDist X<80,{COUNTERS[id]},{choice})'
    bounds='\ntriggerall = P2BodyDist X < 90' if id in {'vladimir','cesar','felix'} else ''
    extra += ctl(-1,'CPU themed special','ChangeState','value = '+choice,'Random < AILevel * 6\ntriggerall = !IsHelper\ntriggerall = AILevel > 0\ntriggerall = RoundState = 2\ntriggerall = StateType != A\ntriggerall = Ctrl\ntriggerall = NumHelper(1005) = 0'+bounds)
    return extra+END+'\n'


def timers(id):
    out='\n'+START+'\n'
    for var in [46,48]:
        out+=ctl(-2,'Teacher timer','VarAdd',f'v = {var}\nvalue = -1\nignorehitpause = 1',f'!IsHelper && var({var}) > 0')
    from teacher_identity import passive
    return out+passive(id,ctl)+END+'\n'


def apply_character(id):
    p=PROFILES[id]; folder=ROOT/'chars'/id
    art=folder/'art/specials'; sheet=art/'sheet.png'
    if not sheet.exists(): return False
    # One recoverable snapshot before the first installation. Later edits and
    # rebuilds use the current files and only replace our named sections.
    backup=art/'before-specials'; backup.mkdir(parents=True,exist_ok=True)
    for file in [f'{id}.sff',f'{id}.air',f'{id}.cns',f'{id}.cmd','kof-extra.cns',f'{id}-movelist.dat']:
        if not (backup/file).exists(): shutil.copy2(folder/file,backup/file)
    # Reuse the previous pre-install archive only when the full current SFF
    # still matches our last output. This keeps repeat builds stable while
    # preserving any later manual changes to normal poses or Victor's sprites.
    sff=folder/f'{id}.sff'
    current=sff.read_bytes()
    record=art/'sff-install.json'
    if record.exists():
        previous=json.loads(record.read_text(encoding='utf-8'))
        if hashlib.sha256(current).hexdigest()==previous['installed_hash']:
            current=bytes.fromhex(previous['input_header'])+current[64:previous['input_size']]
            write_binary(sff,current)
    installation=dict(input_size=len(current),input_header=current[:64].hex())
    from teacher_identity import sprites as identity_sprites
    from teacher_animation import normal_sprites, legacy_combat_sprites
    frames=extract_sheet(sheet,id)
    frames.update(identity_sprites(ROOT,id))
    frames.update(legacy_combat_sprites(ROOT,id))
    frames.update(normal_sprites(ROOT,id))
    upsert_sff(sff,frames)
    if id=='daniela':
        from victor_assist import sprites as victor_sprites
        upsert_sff(sff,victor_sprites())
    installation['installed_hash']=hashlib.sha256(sff.read_bytes()).hexdigest()
    record.write_text(json.dumps(installation,indent=2),encoding='utf-8')
    air=folder/f'{id}.air'
    air_text=clean_generated(air.read_text(encoding='utf-8'))
    # Recover old installs where removing Victor's previous AIR block also
    # swallowed the following BEGIN marker, leaving orphan special actions.
    air_text=re.sub(r'(?ims)^\[Begin Action 87\d\d\].*?(?=^\[Begin Action |\Z)','',air_text)
    air_text=air_text.replace(START,'').replace(END,'').rstrip()+'\n'
    # Low attacks used standing uppercut artwork, making the body appear to
    # grow out of its crouch. Use the existing low sequence at its native scale;
    # retain group 410 for the dedicated standing antiair action 8735.
    def low_attack(match):
        block=re.sub(r'(?m)^(?:400|410),(\d+),',r'440,\1,',match.group(0))
        return re.sub(r'(?m)^Clsn1\[0\] = .*$', 'Clsn1[0] = 8,-48,65,-8',block)
    air_text=re.sub(r'(?ims)^\[Begin Action (?:400|410)\].*?(?=^\[Begin Action |\Z)',low_attack,air_text)
    from teacher_identity import normal_air, tune_basics
    air.write_text(normal_air(air_text,id)+actions(id),encoding='utf-8')
    if id=='daniela':
        from victor_assist import install_air
        install_air(air)
    cns=folder/f'{id}.cns'
    text=clean_generated(cns.read_text(encoding='utf-8'))
    text=re.sub(r'(?ims)^\[Statedef (3000|3010|3020|3021)\].*?(?=^\[Statedef |\Z)','',text)
    if id=='daniela':
        text=re.sub(r'(?ims)^\[Statedef 82\d\d\].*?(?=^\[Statedef |\Z)','',text)
        text=re.sub(r'(?ims)^\[State -2, Victor[^\]]*\].*?(?=^\[State|\Z)','',text)
        companion=(ROOT/'tools/victor-companion.cns').read_text(encoding='utf-8')
        controllers,states=companion.split('[Statedef 8200]',1)
        controllers=controllers.replace('[Statedef -2]','')
        text=text.replace('[Statedef -2]','[Statedef -2]\n'+controllers,1)
        text+='\n[Statedef 8200]'+states
    if '[Statedef -2]' in text:
        text=text.replace('[Statedef -2]','[Statedef -2]\n'+timers(id),1)
    else: text+='\n[Statedef -2]\n'+timers(id)
    cns.write_text(tune_basics(text,id),encoding='utf-8')
    (folder/'kof-extra.cns').write_text(special_cns(id,p),encoding='utf-8')
    cmd=folder/f'{id}.cmd'; text=clean_generated(cmd.read_text(encoding='utf-8'))
    if id=='daniela':
        # A partner assist cannot be called again while Victor is still away.
        text=re.sub(r'(?m)^triggerall = NumHelper\(3010\) = 0\n(?:triggerall = Helper\(8200\),StateNo = 8200\n)?','triggerall = NumHelper(3010) = 0\ntriggerall = Helper(8200),StateNo = 8200\n',text)
    text=text.replace('[State -1, Motion special 1010]',commands(p,id)+'\n[State -1, Motion special 1010]',1)
    text=re.sub(r'(?m)^x = ifelse\(P2BodyDist X > 50,.*','x = ifelse(P2BodyDist X > 50,Const(velocity.walk.fwd),0)',text)
    cmd.write_text(text,encoding='utf-8')
    # Normal contacts, chains and airborne attacks belong to the individual
    # teacher. Special timelines use the real HitDef schedule for visible hits.
    from teacher_normals import apply_cns, apply_air, apply_cmd, describe, update_movelist
    from teacher_animation import synchronize
    for state_path in (cns, folder/'kof-extra.cns'):
        state_path.write_text(apply_cns(state_path.read_text(encoding='utf-8'),id),encoding='utf-8')
    air_text=apply_air(air.read_text(encoding='utf-8'),id)
    air_text,extra_text=synchronize(air_text,(folder/'kof-extra.cns').read_text(encoding='utf-8'),id,sff)
    air.write_text(air_text,encoding='utf-8')
    (folder/'kof-extra.cns').write_text(extra_text,encoding='utf-8')
    cmd.write_text(apply_cmd(cmd.read_text(encoding='utf-8'),id),encoding='utf-8')
    moves=folder/f'{id}-movelist.dat'
    base=(ROOT/'chars/chava/chava-movelist.dat').read_text(encoding='utf-8')
    old=['Codigo compilado','Gancho compilacion','Mochilazo de avance','Barrida de semestre','unused','Asistente IA','Entrega final','Compilacion final + IA']
    base=base.replace('CHAVA / CONTROLES KOF',p['name'].upper()+' / CONTROLES KOF')
    for a,b in zip(old,p['moves']): base=base.replace(a,b)
    base=base.replace('Codigo, alternativa U',p['moves'][0]+' (alternativa)')
    base=base.replace('<#63ded7>:Supers',f'{p["moves"][4]:38} _D_DB_B + ^A / ^B\nApoyo: costo {p["cost"]}; espera {p["cooldown"]//60} s.\n\n<#63ded7>:Supers')
    base+='\n\n<#63ded7>:Identidad - '+p['role']+':</>\n'
    base+=p['resource']+': hasta tres iconos debajo de VIDA.\n'+'\n'.join(p['notes'])+'\n'
    normals=describe(id)
    # Remove the template character's normals and show the actual repertoire
    # and confirmed chains maintained by the same module as the state files.
    base=update_movelist(base,id)
    normal_art=folder/'art/normal-v3'
    normal_art.mkdir(parents=True,exist_ok=True)
    (normal_art/'moves.json').write_text(json.dumps(normals,ensure_ascii=False,indent=2),encoding='utf-8')
    moves.write_text(base,encoding='utf-8')
    (art/'gameplay.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8')
    manifest=folder/'art/manifest.json'
    if manifest.exists():
        data=json.loads(manifest.read_text(encoding='utf-8'))
        data.update(special_frames=24,specials='art/specials/gameplay.json',limitations='Voices and some impact sounds share prototype resources; some normal actions reuse poses.')
        data.update(identity_frames=6,identity_art='art/identity-v2/preview.png',identity_role=p['role'])
        data.update(normal_frames=24,normal_art='art/normal-v3/sheet.png',normal_moves='art/normal-v3/moves.json',limitations='Original keyframe animations; prototype voices and some impact sounds are shared.')
        if id=='daniela':data.update(victor_assist_frames=24,victor_assist='art/victor-assist/PROMPT.json')
        manifest.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    print(id, '54 themed frames; own normals, specials, resource and MAX2;',p['role'],flush=True)
    return True


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('characters',nargs='*'); args=parser.parse_args()
    for id in args.characters or PROFILES: assert apply_character(id),(id,'missing sheet')
    from teacher_normals import write_catalog
    write_catalog()
    path=ROOT/'data/utc-roster.json'
    roster=json.loads(path.read_text(encoding='utf-8'))
    for entry in roster:
        if entry['id'] not in PROFILES: continue
        profile=PROFILES[entry['id']]
        moves=profile['moves']
        entry.update(moves=[moves[0],moves[0]+' (alternativa)',*moves[1:4],*moves[5:]],
                     support_move=moves[4],identity_role=profile['role'],identity_resource=profile['resource'])
    path.write_text(json.dumps(roster,ensure_ascii=False,indent=2),encoding='utf-8')


if __name__=='__main__': main()
