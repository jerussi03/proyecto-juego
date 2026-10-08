"""Capture each new signature at normal game speed, with isolated fixtures."""
from pathlib import Path
import re
import subprocess
from build_teacher_specials import PROFILES,ctl

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'scratch/identity-preview'
SIGNATURES={'chan_kof':(1010,26),'felix':(1010,14),'alejandro':(1040,26),
 'daniela':(1010,14),'gameros':(1040,30),'armando':(1040,30),'vladimir':(1000,14),
 'jaime':(1000,23),'leonardo':(1000,22),'cesar':(1000,28)}


def main():
    original=(ROOT/'save/config.ini').read_bytes()
    for id,(target,frame) in SIGNATURES.items():
        folder=ROOT/'chars'/id
        dest=OUT/id; dest.mkdir(parents=True,exist_ok=True)
        qa=ctl(-2,'Preview clock','VarAdd','v = 58\nvalue = 1','!IsHelper && RoundState=2')
        for kind,params in [('PowerSet','value = 5000'),('VarSet','v = 44\nvalue = 0'),
          ('PosSet','x = -40-CameraPos X\ny = 0'),
          ('PosSet','x = 90-CameraPos X\ny = 0\nredirectID = EnemyNear,ID'),
          ('ChangeState',f'value = {target}\nctrl = 0')]:
            qa+=ctl(-2,'Preview fixture',kind,params,'!IsHelper && var(58)=1 && RoundState=2')
        cns=(folder/f'{id}.cns').read_text(encoding='utf-8').replace('[Statedef -2]','[Statedef -2]\n'+qa,1)
        (folder/'identity-preview.cns').write_text(cns,encoding='utf-8')
        definition=re.sub(r'(?m)^st\s*=.*','st = identity-preview.cns',(folder/f'{id}.def').read_text(encoding='utf-8'))
        (folder/'identity-preview.def').write_text(definition,encoding='utf-8')
        observer=f'''if player(1) and roundState()==2 then
 if stateNo()=={target} and time()>={frame} and not identityCaptured then
  identityCaptured=true; screenshot()
 end
 if var(58)>100 then os.exit() end
end
'''
        (dest/'observer.lua').write_text(observer,encoding='utf-8')
        config=original.decode('utf-8-sig')
        config=re.sub(r'(?m)^Lua\s*=.*',f'Lua = loop(), dofile("scratch/identity-preview/{id}/observer.lua")',config)
        config=re.sub(r'(?m)^ScreenshotFolder\s*=.*',f'ScreenshotFolder = scratch/identity-preview/{id}',config)
        config=re.sub(r'(?m)^Fullscreen\s*=.*','Fullscreen = false',config)
        (dest/'config.ini').write_text(config,encoding='utf-8')
        run=subprocess.run([str(ROOT/'TheKingOfUTc.exe'),'-config',str(dest/'config.ini'),'-p1',f'{id}/identity-preview.def','-p2','chava','-s','stages/patio.def','-rounds','1','-time','-1','-nosound','-windowed'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=20)
        assert run.returncode==0,(id,run.stdout.decode(errors='replace')[-1000:])
        assert list(dest.glob('*.png')),(id,'missing preview')
        print(id,'captured at normal speed',flush=True)
    assert (ROOT/'save/config.ini').read_bytes()==original


if __name__=='__main__': main()
