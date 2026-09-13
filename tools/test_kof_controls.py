"""Static checks and real Ikemen input playback (no keyboard injection).

Run with --prepare to build isolated QA definitions/configs, or --check-logs
after the engine run. Production definitions never load these QA states.
"""
from pathlib import Path
import re, struct, json, sys
from io import BytesIO
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'scratch/kof-qa'
OUT.mkdir(parents=True,exist_ok=True)

def validate():
    report={}
    for name in ['hector','chava']:
        folder=ROOT/f'chars/{name}'
        blob=(folder/f'{name}.sff').read_bytes()
        off,count=struct.unpack_from('<II',blob,36)
        ldata=struct.unpack_from('<I',blob,52)[0]
        sprites={}
        for i in range(count):
            entry=struct.unpack_from('<HHHHhhHBBIIHH',blob,off+i*28)
            g,n,w,h,ax,ay,link,fmt,depth,ofs,size,pal,flags=entry
            assert (g,n) not in sprites,(name,'duplicate sprite',g,n)
            sprites[g,n]=entry
            if fmt==11 and size:
                image=Image.open(BytesIO(blob[ldata+ofs+4:ldata+ofs+size]))
                assert image.size==(w,h),(name,g,n,image.size,(w,h))
        air=(folder/f'{name}.air').read_text()
        refs={(int(g),int(i)) for g,i in re.findall(r'(?m)^\s*(\d+)\s*,\s*(\d+)\s*,',air)}
        assert not refs-sprites.keys(),(name,'missing sprites',refs-sprites.keys())
        anims=re.findall(r'(?im)^\[Begin Action (\d+)\]',air)
        assert len(anims)==len(set(anims)),(name,'duplicate animation')
        cns='\n'.join((folder/f).read_text() for f in [f'{name}.cns','kof-extra.cns'])+'\n'+(ROOT/'chars/kof-system.cns').read_text()
        states=re.findall(r'(?im)^\[Statedef (-?\d+)\]',cns)
        assert len(states)==len(set(states)),(name,'duplicate state')
        cmd=(folder/f'{name}.cmd').read_text()
        declared=set(re.findall(r'(?m)^name\s*=\s*"([^"]+)"',cmd.split('[Statedef -1]')[0]))
        used=set(re.findall(r'command\s*[!=]=?\s*"([^"]+)"',cmd+cns))
        assert not used-declared,(name,'undeclared commands',used-declared)
        required={200,210,230,240,400,410,430,440,600,610,630,640,750,900,920,921,922,923,1000,1005,1010,1020,1030,3000,3500,4000}
        assert required <= {int(n) for n in states},(name,'missing moves')
        # Each new contact box must intersect visible pixels of its active frame.
        if name=='hector':
            contacts={400:(14,-57,69,-36),410:(12,-106,42,-51),240:(24,-96,100,-65),640:(17,-39,90,-7)}
            for group,box in contacts.items():
                e=sprites[group,3]; ax,ay=e[4:6]
                image=Image.open(BytesIO(blob[ldata+e[9]+4:ldata+e[9]+e[10]])).convert('RGBA')
                rect=(box[0]+ax,box[1]+ay,box[2]+ax,box[3]+ay)
                assert image.getchannel('A').crop(rect).getbbox(),(group,'hitbox misses art')
        report[name]=dict(sprites=count,animations=len(anims),states=len(states),commands=len(declared),passed=True)
    (OUT/'static-validation.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))

def prepare():
    # Input flags are relative F/B, so the same motions are tested from both sides.
    cases=[
        ('AB roll',[('x','a')],920),
        ('back AB roll',[('B',),('B','x','a')],921),
        ('RT roll',[('c',)],920),
        ('BC MAX',[('a','y')],900),
        ('RB MAX',[('z',)],900),
        ('crouch A',[('D',),('D','x')],400),
        ('crouch C',[('D',),('D','y')],410),
        ('stand D',[('b',)],240),
        ('crouch D',[('D',),('D','b')],440),
        ('QCF A',[('D',),('D','F'),('F','x')],1000),
        ('QCF C',[('D',),('D','F'),('F','y')],1000),
        ('DP A',[('F',),('D',),('D','F','x')],1010),
        ('QCB A',[('D',),('D','B'),('B','x')],1020),
        ('HCF B',[('B',),('D','B'),('D',),('D','F'),('F','a')],1030),
        ('double QCF super',[('D',),('D','F'),('F',),('D',),('D','F'),('F','x')],-1),
        ('rush super',[('D',),('D','F'),('F',),('D','F'),('D',),('D','B'),('B','x')],3500),
        ('MAX2',[('D',),('D','B'),('B',),('D',),('D','B'),('B','x','y')],4000),
        ('CD blowback',[('y','b')],750),
        ('BC insufficient energy',[('a','y')],-2),
        ('guard cancel AB',[('x','a')],922),
    ]
    specs=[]
    for facing in [1,-1]:
        for label,sequence,target in cases:
            specs.append(dict(label=label,facing=facing,sequence=sequence,target=target))
    (OUT/'cases.json').write_text(json.dumps(specs,indent=2))
    common='''[Statedef -2]
[State QA, Clock]
type = VarAdd
trigger1 = RoundState = 2
v = 58
value = 1
ignorehitpause = 1

[State QA, Preserve life]
type = LifeSet
trigger1 = 1
value = 10000
ignorehitpause = 1
'''
    for name in ['hector','chava']:
        qa=common
        for idx,spec in enumerate(specs):
            start=idx*140+10
            cond=f'var(58) = {start}'
            def ctrl(kind,params,t=cond):
                return f'\n[State QA, {kind} {idx}]\ntype = {kind}\ntrigger1 = {t}\n{params}\n'
            qa+=ctrl('PowerSet','value = '+('0' if spec['target']==-2 else '5000'))
            qa+=ctrl('VarSet','v = 40\nvalue = '+('500' if spec['target']==4000 else '0'))
            qa+=ctrl('PosSet',f'x = {-65*spec["facing"]}\ny = 0')
            qa+=ctrl('Turn','',t=cond+f' && Facing != {spec["facing"]}')
            # Put the dummy on the other side without making the player move.
            qa+=ctrl('PosSet',f'x = {65*spec["facing"]}\ny = 0\nredirectID = EnemyNear, ID')
            qa+=ctrl('ChangeState','value = 0\nctrl = 1')
            if spec['target']==922:
                qa+=ctrl('ChangeState','value = 150\nctrl = 0',t=f'var(58) = {start+7}')
            for j,flags in enumerate(spec['sequence']):
                tick=start+8+j*3
                params='\n'.join(f'flag{str(k+1) if k else ""} = {flag}' for k,flag in enumerate(flags))
                qa+=ctrl('AssertInput',params,t=f'var(58) = [{tick},{tick+2}]')
        # Ikemen keeps the first definition of a negative state. Put the QA
        # clock in the main state file, not a second competing Statedef -2.
        base=(ROOT/f'chars/{name}/{name}.cns').read_text()
        base=re.sub(r'(?ims)^\[Statedef -2\].*?(?=^\[Statedef |\Z)','',base)
        path=ROOT/f'chars/{name}/kof-input-qa.cns'; path.write_text(base+'\n'+qa)
        definition=(ROOT/f'chars/{name}/{name}.def').read_text()
        definition=re.sub(r'(?m)^st\s*=.*','st = kof-input-qa.cns',definition)
        (ROOT/f'chars/{name}/kof-input-qa.def').write_text(definition)
    cfg=(ROOT/'save/config.ini').read_text(encoding='utf-8-sig')
    cfg=re.sub(r'(?m)^Lua\s*=.*','Lua = loop(), dofile("scratch/kof-qa/observer.lua")',cfg)
    cfg=re.sub(r'(?m)^ScreenshotFolder\s*=.*','ScreenshotFolder = scratch/kof-qa',cfg)
    (OUT/'config.ini').write_text(cfg)
    (OUT/'observer.lua').write_text('''
if player(1) then
  local t = var(58)
  if t > 0 and t ~= kofLastTick then
    kofLastTick = t
    local f = assert(io.open("scratch/kof-qa/" .. name() .. "-input.csv", "a"))
    f:write(string.format("%d,%d,%d,%d,%d,%d,%d,%f,%f\\n",t,stateNo(),anim(),time(),power(),var(40),numExplod(9900),posX(),velX()))
    f:close()
    if (stateNo() == 900 and time() == 5) or (stateNo() == 400 and animElemNo(0) == 4 and animElemTime(4) == 0) then screenshot() end
    if t >= '''+str(len(specs)*140)+''' then os.exit() end
  end
end
''')
    print('Prepared',len(specs),'real-input scenarios per character')

def check_logs():
    import csv
    specs=json.loads((OUT/'cases.json').read_text())
    results={}
    for name in ['Hector','Chava']:
        rows=[[float(x) for x in r] for r in csv.reader((OUT/f'{name}-input.csv').open())]
        result=[]
        for idx,spec in enumerate(specs):
            start=idx*140+18
            window=[r for r in rows if start <= r[0] < start+60]
            target=spec['target']
            if target==-1: target=3200 if name=='Hector' else 3000
            found={int(r[1]) for r in window}
            ok=(900 not in found if target==-2 else target in found)
            checks={}
            if target==900:
                checks['cost']=any(r[4]==4000 for r in window)
                checks['max_bar']=any(r[5]>0 and r[6]>0 for r in window)
            if target in [920,921,922]:
                checks['returns_to_idle']=any(r[1]==0 for r in window if r[0]>start+35)
                if target==922: checks['cost']=any(r[4]==4000 for r in window)
            if target==4000: checks['consumes_max']=any(r[1]==4000 and r[5]==0 for r in window)
            ok=ok and all(checks.values())
            result.append(dict(label=spec['label'],facing=spec['facing'],expected=target,seen=sorted(found),checks=checks,passed=ok))
        results[name]=result
    (OUT/'input-validation.json').write_text(json.dumps(results,indent=2))
    failed=[(name,r) for name,rs in results.items() for r in rs if not r['passed']]
    print('Input scenarios:',sum(len(r) for r in results.values()),'Failed:',len(failed))
    for name,r in failed: print(name,r)
    return not failed

if __name__=='__main__':
    validate()
    if '--prepare' in sys.argv: prepare()
    if '--check-logs' in sys.argv: sys.exit(0 if check_logs() else 1)
