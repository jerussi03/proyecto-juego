"""Build the KOF-inspired controls from the preserved pre-change files.

Sprite extraction is asset packing: the poses are ImageGen artwork, not drawn
or synthesized by this script. Existing SFF data and palettes remain byte-exact.
"""
from pathlib import Path
from io import BytesIO
import re, struct, shutil, json
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
BACK = ROOT / 'backups/kof-controls-20260913'
ART = ROOT / 'chars/hector/art/kof'
ART.mkdir(parents=True, exist_ok=True)

def read(path):
    return path.read_text(encoding='utf-8-sig')

def write(path, text):
    path.write_text(text.rstrip() + '\n', encoding='utf-8')

def state(text, n):
    return re.search(r'(?ims)^\[Statedef '+str(n)+r'\].*?(?=^\[Statedef |\Z)', text).group()

def action(text, n):
    return re.search(r'(?ims)^\[Begin Action '+str(n)+r'\].*?(?=^\[Begin Action |\Z)', text).group()

def command(name, sequence, time=22):
    return f'\n[Command]\nname = "{name}"\ncommand = {sequence}\ntime = {time}\nbuffer.time = {1 if sequence.startswith("/") else 4}\n'

def change(label, target, alltr, alternatives):
    out=f'\n[State -1, {label}]\ntype = ChangeState\nvalue = {target}\n'
    for t in ['!IsHelper','RoundState = 2']+alltr: out+=f'triggerall = {t}\n'
    for i, ts in enumerate(alternatives,1):
        for t in ts: out+=f'trigger{i} = {t}\n'
    return out

def pack_sff(original, extras):
    data=bytearray(original)
    offset,count=struct.unpack_from('<II',data,36)
    ldata=struct.unpack_from('<I',data,52)[0]
    table=bytearray(data[offset:offset+28*count])
    known={struct.unpack_from('<HH',table,i*28) for i in range(count)}
    payload=bytearray()
    newoffset=len(data)
    start=newoffset+28*(count+len(extras))
    for group,item,im,ax,ay in extras:
        assert (group,item) not in known
        stream=BytesIO(); im.save(stream,format='PNG')
        raw=struct.pack('<I',im.width*im.height*4)+stream.getvalue()
        table.extend(struct.pack('<HHHHhhHBBIIHH',group,item,im.width,im.height,ax,ay,0,11,32,start+len(payload)-ldata,len(raw),0,0))
        payload.extend(raw)
    struct.pack_into('<II',data,36,newoffset,count+len(extras))
    # Include the appended PNG payloads in the addressable local data region.
    struct.pack_into('<I',data,56,start+len(payload)-ldata)
    return data+table+payload

def sprites():
    src=ART/'hector-attacks-source.png'
    if not src.exists():
        shutil.copy2(Path.home()/'.codex/generated_images/01a099dc-14f1-76e3-ae60-382b043756e4/exec-22ccc9d5-d26b-4b76-aec8-495cdcf02fa5.png',src)
    sheet=Image.open(src).convert('RGBA')
    # Chroma-key the solid background as part of importing the animation sheet.
    pixels=list(sheet.getdata())
    sheet.putdata([(r,g,b,0 if r>140 and b>140 and g<100 and min(r,b)-g>75 else 255) for r,g,b,a in pixels])
    output=[]; manifest=[]
    for row,group in enumerate([400,410,240,640]):
        for col in range(6):
            # The extended boot crosses its nominal grid cell by six pixels.
            left=col*256 + (10 if row==2 and col==4 else 0)
            right=(col+1)*256 + (10 if row==2 and col==3 else 0)
            cell=sheet.crop((left,row*256,right,(row+1)*256))
            box=cell.getbbox(); assert box
            # Constant scale avoids size changes between animation frames.
            scale=0.46
            im=cell.crop(box).resize((round((box[2]-box[0])*scale),round((box[3]-box[1])*scale)),Image.Resampling.NEAREST)
            ax=round((col*256+110-left-box[0])*scale)
            ay=im.height if row<3 else round((246-box[1])*scale)
            im.save(ART/f'{group}-{col}.png')
            output.append((group,col,im,ax,ay))
            manifest.append(dict(group=group,item=col,file=f'{group}-{col}.png',w=im.width,h=im.height,ax=ax,ay=ay))
    (ART/'manifest.json').write_text(json.dumps(manifest,indent=2))
    return output

def ui_sprites():
    bar=Image.new('RGBA',(80,3),(255,202,60,255))
    label=Image.new('RGBA',(82,13),(12,18,26,225))
    d=ImageDraw.Draw(label); d.text((2,0),'MAX',fill=(255,220,100,255)); d.line((1,12,80,12),fill=(120,103,57,255))
    return [(9900,0,bar,0,0),(9901,0,label,0,0)]

NORMAL='(StateNo = [200,240]) || (StateNo = [400,440])'
SPECIAL='(StateNo = [1000,1030])'
MOTION={'qcf':'~D, DF, F','qcb':'~D, DB, B','dp':'~F, D, DF','hcf':'~B, DB, D, DF, F','hcb':'~F, DF, D, DB, B','dqcf':'~D, DF, F, D, DF, F','dqcb':'~D, DB, B, D, DB, B','qcfhcb':'~D, DF, F, DF, D, DB, B'}

def build_commands(name):
    old=read(BACK/f'chars/{name}/{name}.cmd')
    s='; KOF notation: A=x, B=a, C=y, D=b. Xbox X/A/Y/B.\n[Remap]\nx=x\ny=y\nz=z\na=a\nb=b\nc=c\ns=s\n\n[Defaults]\ncommand.time=22\ncommand.buffer.time=4\n'
    for key in ['x','y','a','b','c','z','s']: s+=command(key,key,1)
    for key,v in [('holdfwd','F'),('holdback','B'),('holddown','D'),('holdup','U')]: s+=command(key,'/$'+v,1)
    for key,v in [('FF','F,F'),('BB','B,B')]: s+=command(key,v,12)
    for key,v in [('roll','x+a'),('roll','c'),('max','a+y'),('max','z'),('blowback','y+b'),('recovery','x+a')]: s+=command(key,v,1)
    for motion in MOTION:
        for key in ['x','y','a','b']:
            s+=command(motion+'_'+key,MOTION[motion]+', '+key,36 if motion in ['dqcf','dqcb','qcfhcb'] else 24)
    s+=command('max2',MOTION['dqcb']+', x+y',40)
    s+='\n[Statedef -1]\n'
    human=['AILevel = 0','StateType != A']
    s+=change('Guard cancel roll', 'ifelse(command = "holdback",923,922)',human+['Power >= 1000'],[['command = "roll"','StateNo = [150,153]']])
    s+=change('Emergency evasion AB or RT','ifelse(command = "holdback",921,920)',human+['Ctrl'],[['command = "roll"']])
    s+=change('MAX BC or RB',900,human+['var(40) = 0','command = "max"'],[['Ctrl','Power >= 1000'],[NORMAL,'MoveContact','Power >= 2000']])
    # Complex motions precede shorter motions and normal attacks.
    s+=change('MAX2',4000,human+['Power >= 2000','var(40) > 0','command = "max2"']+(['NumHelper(4010) = 0'] if name=='hector' else ['NumHelper(3010) = 0']),[['Ctrl'],[NORMAL,'MoveContact'],[SPECIAL,'MoveContact']])
    super1=3200 if name=='hector' else 3000
    s+=change('Double quarter circle super',super1,human+['Power >= 1000','NumHelper(3010) = 0','command = "dqcf_x" || command = "dqcf_y"'],[['Ctrl'],[NORMAL,'MoveContact'],[SPECIAL,'MoveContact','var(40) > 0']])
    s+=change('Rush super',3500,human+['Power >= 1000','command = "qcfhcb_x" || command = "qcfhcb_y"'],[['Ctrl'],[NORMAL,'MoveContact'],[SPECIAL,'MoveContact','var(40) > 0']])
    if name=='hector':
        s+=change('DDoS super',3000,human+['Power >= 1000','NumHelper(3015) = 0','command = "dqcf_a" || command = "dqcf_b"'],[['Ctrl'],[NORMAL,'MoveContact']])
        s+=change('FPV super',3300,human+['Power >= 1000','NumHelper(3030) = 0','command = "dqcb_a" || command = "dqcb_b"'],[['Ctrl'],[NORMAL,'MoveContact']])
        s+=change('Shutdown finisher',4100,human+['Ctrl','Power >= 1000','(EnemyNear, Life) <= 120'],[['command = "hcb_y"']])
        s+=change('Firewall parry',700,human+['Ctrl'],[['command = "qcb_a" || command = "qcb_b"']])
        s+=change('Sin conexion',3100,human+['Ctrl','Power >= 1000','NumHelper(7015) = 0'],[['command = "hcf_x" || command = "hcf_y"']])
        s+=change('Handshake throw',800,human+['Ctrl','P2BodyDist X < 35','P2BodyDist X >= 0','P2StateType != A','P2MoveType != H'],[['command = "hcb_x"']])
    for target,motion,buttons in [(1010,'dp',['x','y']),(1030,'hcf',['a','b']),(1020,'qcb',['x','y']),(1000,'qcf',['x','y'])]:
        trs=human+[f'command = "{motion}_{buttons[0]}" || command = "{motion}_{buttons[1]}"']
        if target==1000 and name=='chava': trs[-1]+=' || command = "hcf_x" || command = "hcf_y"'
        if target==1000: trs+=['NumHelper(1005) = 0']
        s+=change('Motion special '+str(target),target,trs,[['Ctrl'],[NORMAL,'MoveContact'],[SPECIAL,'StateNo != '+str(target),'MoveContact || (StateNo = 1000 && var(43) > 0)','var(40) >= 90']])
    s+=change('CD blowback',750,human+['Ctrl'],[['command = "blowback"']])
    if name=='chava':
        # Preserve the manual variants, normal chains, and existing CPU behavior.
        tail=old[old.index('[State -1, Run]'):]
        s+=tail
        s+=change('CPU IA',3000,['AILevel > 0','StateType != A','Ctrl','Power >= 1000','NumHelper(3010) = 0'],[['P2BodyDist X > 70','Random < 7 * AILevel']])
    else:
        for posture,targets in [('A',[600,630,610,640]),('C',[400,430,410,440]),('S',[200,230,210,240])]:
            for key,target in zip(['x','a','y','b'],targets):
                tr=['AILevel = 0',f'command = "{key}"']
                if posture=='A': tr+=['StateType = A']
                elif posture=='C': tr+=['StateType != A','command = "holddown"']
                else: tr+=['StateType = S','command != "holddown"']
                alts=[['Ctrl']]
                if key in ['y','b']: alts+=[[f'StateNo = {targets[0]} || StateNo = {targets[1]}','MoveHit','AnimElemTime(5) >= 0']]
                s+=change('Normal '+str(target),target,tr,alts)
        for label,target,cmd in [('Run',100,'FF'),('Backstep',105,'BB'),('Taunt',195,'s')]:
            s+=change(label,target,human+['Ctrl'],[[f'command = "{cmd}"']])
        tail=old[old.index('[State -1, CPU]'):]
        tail=tail.replace('Power >= 500','Power >= 1000')
        s+=tail
    s+=change('CPU roll',920,['AILevel > 0','Ctrl','StateType != A'],[['P2MoveType = A','P2BodyDist X < 100','Random < 8 * AILevel']])
    return s

def hit(n,damage=65,attr='S, SA',fall=0,velocity='-4'):
    return f'''\n[State {n}, Contact]
type = HitDef
trigger1 = AnimElem = 4
attr = {attr}
damage = {damage},5
animtype = Heavy
guardflag = {'L' if attr.startswith('C') else 'MA'}
hitflag = MAF
priority = 4,Hit
pausetime = 7,10
sparkno = 2
sparkxy = -8,-60
hitsound = 5,0
guardsound = 6,0
ground.type = {'Low' if attr.startswith('C') else 'High'}
ground.slidetime = 16
ground.hittime = 20
ground.velocity = {velocity}
air.velocity = -3,-5
air.hittime = 22
fall = {fall}
fall.recover = 0
getpower = 40,20
givepower = 24,12
'''

def attack(n,anim,damage=65,posture='S',fall=0,vel='-4',kind='SA'):
    return f'''\n[Statedef {n}]
type = {posture}
movetype = A
physics = {posture}
anim = {anim}
ctrl = 0
{'velset = 0,0' if posture != 'A' else ''}
poweradd = 12
''' + hit(n,damage,f'{posture}, {kind}',fall,vel)+f'''
[State {n}, End]
type = ChangeState
trigger1 = AnimTime = 0
value = {11 if posture=='C' else 50 if posture=='A' else 0}
ctrl = 1
'''

def build_extra(name):
    old=read(BACK/f'chars/{name}/{name}.cns')
    s='; Character-specific KOF-inspired specials and missing normals.\n'
    if name=='hector':
        for n,anim,dmg,post,fall in [(400,400,26,'C',0),(410,410,62,'C',0),(240,240,66,'S',0),(440,430,58,'C',1),(610,600,57,'A',0),(640,640,65,'A',0)]:
            s+=attack(n,anim,dmg,post,fall,kind='NA').replace(f'damage = {dmg},5',f'damage = {dmg},0')
    # Packet / compiled code: one limited, blockable projectile, no power cost.
    s+='''
[Statedef 1000]
type = S
movetype = A
physics = S
anim = 1000
ctrl = 0
velset = 0,0
poweradd = 20

[State 1000, Clear projectile contact]
type = VarSet
trigger1 = Time = 0
v = 43
value = 0

[State 1000, Projectile]
type = Helper
trigger1 = AnimElem = 4
trigger1 = NumHelper(1005) = 0
name = "Codigo / paquete"
ID = 1005
stateno = 1005
postype = p1
pos = 35,-58
keyctrl = 0
ownpal = 1

[State 1000, End]
type = ChangeState
trigger1 = AnimTime = 0
value = 0
ctrl = 1
'''
    proj=state(old,3020)
    proj=proj.replace('[Statedef 3020]','[Statedef 1005]').replace('[State 3020,','[State 1005,')
    proj=re.sub(r'damage = [^\n]+','damage = 58,6',proj)
    proj=re.sub(r'ground.hittime = [^\n]+','ground.hittime = 18',proj)
    proj=proj.replace('attr = A,HP','attr = A,SP')
    impact='[State 1005, Packet impact]' if name=='hector' else '[State 1005, Impact]'
    proj=proj.replace(impact,'''[State 1005, Report contact for MAX cancel]
type = ParentVarSet
trigger1 = MoveContact
v = 43
value = 1

'''+impact)
    s+=proj
    for n,anim,dmg in [(1010,410 if name=='hector' else 410,78),(1020,210,72),(1030,430 if name=='hector' else 440,64),(750,240,85)]:
        block=attack(n,anim,dmg,'C' if n==1030 else 'S',1 if n in [1010,1030,750] else 0,'-3,-7' if n==1010 else '-5')
        extra=''
        if n in [1020,1030]:
            extra=f'\n[State {n}, Advance]\ntype = VelSet\ntrigger1 = Time < 12\nx = {4.5 if n==1020 else 5}\n'
        if n==1010:
            extra=f'\n[State {n}, Anti air startup]\ntype = NotHitBy\ntrigger1 = Time < 5\nvalue = SCA, NA, SA, HA\ntime = 1\n'
        if n==750: block=block.replace('damage = 85,5','damage = 85,0')
        s+=block.replace(f'[State {n}, End]',extra+f'\n[State {n}, End]')
    if name=='chava':
        for n,cost in [(3500,1000),(4000,2000)]:
            s+=f'''\n[Statedef {n}]
type = S
movetype = A
physics = S
anim = 3500
ctrl = 0
velset = 0,0
poweradd = -{cost}

[State {n}, Flash]
type = SuperPause
trigger1 = Time = 0
time = 18
movetime = 18
anim = -1
darken = 1
p2defmul = 1

[State {n}, Rush]
type = VelSet
trigger1 = AnimElemTime(9) < 0
x = 4.5
'''
            for i in [3,6,9]:
                s+=hit(n,50 if i!=9 else 85,'S, HA',1 if i==9 else 0,'-2,-7' if i==9 else '-1').replace('AnimElem = 4',f'AnimElem = {i}').replace('getpower = 40,20','getpower = 0,0')
            if n==4000:
                s+='''
[State 4000, Compilacion final]
type = Helper
trigger1 = AnimElem = 9
trigger1 = NumHelper(3010) = 0
name = "Asistente IA MAX2"
ID = 3010
stateno = 3010
postype = p1
pos = -25,-85
keyctrl = 0
ownpal = 1
'''
            s+=f'\n[State {n}, End]\ntype = ChangeState\ntrigger1 = AnimTime = 0\nvalue = 0\nctrl = 1\n'
    return s

def build_air(name):
    a=read(BACK/f'chars/{name}/{name}.air')
    if name=='hector':
        # Source sheet contact boxes measured against the imported fist/boot.
        for n,post,box,times in [(400,'C',(14,-57,69,-36),[2,2,2,3,3,5]),(410,'C',(12,-106,42,-51),[3,3,3,4,5,7]),(240,'S',(24,-96,100,-65),[3,4,3,4,5,7]),(640,'A',(17,-39,90,-7),[3,3,3,4,5,7])]:
            a+=f'\n[Begin Action {n}]\nClsn2Default: 2\nClsn2[0] = -25,{-78 if post=="C" else -108},25,-34\nClsn2[1] = -28,-34,30,0\n'
            for i,t in enumerate(times):
                if i==3: a+='Clsn1: 1\nClsn1[0] = '+','.join(map(str,box))+'\n'
                a+=f'{n},{i},0,0,{t}\n'
        # Running uses existing actual running sprites, not missing action 100.
        a+='\n[Begin Action 100]\nClsn2Default: 1\nClsn2[0] = -24,-105,27,0\n'+''.join(f'100,{i},0,0,3\n' for i in range(6))
    a+='\n[Begin Action 920]\nClsn2Default: 1\nClsn2[0] = -24,-100,24,0\n100,1,0,0,5\n100,2,0,0,5\n100,3,0,0,5\n0,0,0,0,9\n'
    # Short casting action independent from the long five-shot IA super pose.
    a+='\n[Begin Action 1000]\nClsn2Default: 1\nClsn2[0] = -24,-106,24,0\n'+''.join(f'3000,{i},0,0,{[3,3,3,4,6,9][i]}\n' for i in range(6))
    if name=='chava':
        a+='\n[Begin Action 3500]\nClsn2Default: 1\nClsn2[0] = -22,-106,24,0\n'
        for j,(group,item) in enumerate([(210,0),(210,2),(210,3),(210,4),(211,2),(211,3),(211,4),(210,2),(210,3),(210,4),(210,5),(0,0)],1):
            if j in [3,6,9]: a+='Clsn1: 1\nClsn1[0] = 0,-125,73,-45\n'
            a+=f'{group},{item},0,0,{4 if j<10 else 6}\n'
    a+='\n[Begin Action 9900]\n9900,0,0,0,-1\n\n[Begin Action 9901]\n9901,0,0,0,-1\n'
    return a

def shared():
    s='; Shared KOF-inspired system. var(40)=MAX frames, var(41)=entry cost.\n'
    for n in [920,921,922,923]:
        s+=f'''
[Statedef {n}]
type = S
movetype = I
physics = N
anim = 920
ctrl = 0
velset = 0,0
poweradd = {-1000 if n>=922 else 0}

[State {n}, Invulnerable to strikes and projectiles, throwable]
type = NotHitBy
trigger1 = Time >= {0 if n>=922 else 2} && Time < 16
value = SCA, AA, AP
time = 1

[State {n}, Travel]
type = VelSet
trigger1 = Time < 16
x = {-5.5 if n%2 else 5.5}

[State {n}, Vulnerable recovery]
type = VelSet
trigger1 = Time >= 16
x = 0

[State {n}, Pass opponent]
type = PlayerPush
trigger1 = Time < 16
value = 0

[State {n}, Trail]
type = AfterImage
trigger1 = Time = 0
time = 16
length = 5
timegap = 2
framegap = 1
trans = add
palcolor = 0
paladd = 0,35,65

[State {n}, Finish]
type = ChangeState
trigger1 = Time >= 24
value = 0
ctrl = 1
'''
    s+='''
[Statedef 900]
type = S
movetype = I
physics = S
anim = 0
velset = 0,0
ctrl = 0

[State 900, Quick MAX costs two stocks]
type = VarSet
trigger1 = Time = 0
v = 41
value = ifelse((PrevStateNo = [200,240]) || (PrevStateNo = [400,440]),2000,1000)

[State 900, Pay]
type = PowerAdd
trigger1 = Time = 0
value = -var(41)

[State 900, Start MAX]
type = VarSet
trigger1 = Time = 0
v = 40
value = 600

[State 900, Activation flash]
type = PalFX
trigger1 = Time = 0
time = 12
add = 100,70,0

[State 900, Finish]
type = ChangeState
trigger1 = Time >= ifelse(var(41) = 2000,3,12)
value = 0
ctrl = 1

[Statedef -3]

[State -3, End MAX outside combat]
type = VarSet
triggerall = !IsHelper
trigger1 = RoundState != 2
trigger2 = !Alive
v = 40
value = 0

[State -3, MAX clock]
type = VarAdd
triggerall = !IsHelper
trigger1 = var(40) > 0
v = 40
value = -1

[State -3, Special cancel drains MAX]
type = VarAdd
triggerall = !IsHelper
triggerall = var(40) > 0
triggerall = Time = 0
trigger1 = StateNo = [1000,1030]
trigger1 = PrevStateNo = [1000,1030]
v = 40
value = -min(90,var(40))

[State -3, MAX2 consumes the mode after entry payment]
type = VarSet
triggerall = !IsHelper
trigger1 = StateNo = 4000 && Time = 1
v = 40
value = 0

[State -3, Golden MAX pulse]
type = PalFX
triggerall = !IsHelper
trigger1 = var(40) > 0 && GameTime % 24 = 0
time = 8
add = 48,32,0

[State -3, MAX label]
type = Explod
triggerall = !IsHelper
trigger1 = var(40) > 0 && NumExplod(9901) = 0
anim = 9901
ID = 9901
postype = left
pos = ifelse(TeamSide = 1,12,226),207
facing = 1
bindtime = -1
removetime = -1
sprpriority = 10
ontop = 1
ownpal = 1
supermovetime = 999999
pausemovetime = 999999

[State -3, MAX bar]
type = Explod
triggerall = !IsHelper
trigger1 = var(40) > 0 && NumExplod(9900) = 0
anim = 9900
ID = 9900
postype = left
pos = ifelse(TeamSide = 1,13,227),217
facing = 1
bindtime = -1
removetime = -1
sprpriority = 11
ontop = 1
ownpal = 1
supermovetime = 999999
pausemovetime = 999999

[State -3, Update MAX bar]
type = ModifyExplod
triggerall = !IsHelper
trigger1 = NumExplod(9900) > 0
ID = 9900
scale = max(0.001,var(40)/600.0),1

[State -3, Remove expired MAX bar]
type = RemoveExplod
triggerall = !IsHelper
trigger1 = var(40) <= 0
ID = 9900

[State -3, Remove expired MAX label]
type = RemoveExplod
triggerall = !IsHelper
trigger1 = var(40) <= 0
ID = 9901
'''
    return s

def main():
    additions=sprites()
    write(ROOT/'chars/kof-system.cns',shared())
    for name in ['hector','chava']:
        folder=ROOT/f'chars/{name}'
        write(folder/f'{name}.cmd',build_commands(name))
        write(folder/'kof-extra.cns',build_extra(name))
        write(folder/f'{name}.air',build_air(name))
        cns=read(BACK/f'chars/{name}/{name}.cns')
        cns=cns.replace('[Data]','[Data]\npower = 5000',1)
        if name=='hector':
            for n in [3000,3100,3300,3500]:
                old=state(cns,n); new=re.sub(r'poweradd = -\d+','poweradd = -1000',old); cns=cns.replace(old,new)
            old=state(cns,4000); new=old.replace('poweradd = -3000','poweradd = ifelse(var(40) > 0,-2000,-3000)'); cns=cns.replace(old,new)
        write(folder/f'{name}.cns',cns)
        for suffix in ['', '-qa']:
            p=folder/f'{name}{suffix}.def'
            d=read(BACK/f'chars/{name}/{name}{suffix}.def')
            d=d.replace('[Files]','[Files]\nst2 = kof-extra.cns\nst3 = ../kof-system.cns',1)
            write(p,d)
        blob=(BACK/f'chars/{name}/{name}.sff').read_bytes()
        (folder/f'{name}.sff').write_bytes(pack_sff(blob,(additions if name=='hector' else [])+ui_sprites()))
    print('Built commands, MAX, evasion, specials, normals and packed SFF sprites for Hector and Chava.')

if __name__=='__main__': main()
