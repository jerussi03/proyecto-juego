"""Exercise production motion commands, damage and support mechanics in Ikemen.

The isolated QA definitions add AssertInput controllers, never key bindings or
global config changes. Both facing directions and all eight moves are covered.
"""
from pathlib import Path
import csv
import json
import re
import subprocess
import sys
from build_teacher_specials import PROFILES, ctl
from teacher_identity import PROJECTILE_USERS, COUNTERS

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'scratch/teacher-specials-qa'
OUT.mkdir(parents=True,exist_ok=True)
CASES=[
    ('QCF punch',[('D',),('D','F'),('F','x')],1000),
    ('DP punch',[('F',),('D',),('D','F','x')],1010),
    ('QCB punch',[('D',),('D','B'),('B','x')],1020),
    ('HCF kick',[('B',),('D','B'),('D',),('D','F'),('F','a')],1030),
    ('QCB kick support',[('D',),('D','B'),('B','a')],1040),
    ('Double QCF super',[('D',),('D','F'),('F',),('D',),('D','F'),('F','x')],3000),
    ('QCF HCB super',[('D',),('D','F'),('F',),('D','F'),('D',),('D','B'),('B','x')],3500),
    ('MAX2',[('D',),('D','B'),('B',),('D',),('D','B'),('B','x','y')],4000),
]
SPECS=[dict(label=l,sequence=s,target=t,facing=f) for f in [1,-1] for l,s,t in CASES]
SPECS += [dict(label='Support cooldown blocked',sequence=CASES[4][1],target=-1,facing=1,cooldown=240),
          dict(label='Support zero power',sequence=CASES[4][1],target=-2,facing=1,power=0),
          dict(label='Prepared projectile',sequence=CASES[0][1],target=1000,facing=1,buff=240),
          dict(label='Projectile trajectory',sequence=CASES[0][1],target=1000,facing=1,distance=320),
          dict(label='Ranged signature',sequence=CASES[2][1],target=1020,facing=1,distance=160),
          dict(label='Desk camera left',sequence=[],target=0,facing=1,center=-220),
          dict(label='Desk camera right',sequence=[],target=0,facing=-1,center=220),
          dict(label='Prepared alternate super',sequence=CASES[6][1],target=3500,facing=1,buff=240),
          dict(label='Full identity resource',sequence=CASES[3][1],target=1030,facing=1,resource=3),
          dict(label='Prepared support',sequence=CASES[4][1],target=1040,facing=1,resource=3),
          dict(label='Prepared MAX2',sequence=CASES[7][1],target=4000,facing=1,resource=3),
          dict(label='Counter whiff',sequence=[],target=0,facing=1),
          dict(label='Identity receiving hit',sequence=[],target=0,facing=1),
          dict(label='Preparation expires',sequence=[],target=0,facing=1,resource=3,buff=40),
          dict(label='Repeated preparation',sequence=CASES[4][1],target=1040,facing=1),
          dict(label='Calibrated serve',sequence=CASES[0][1],target=1000,facing=1,distance=320,resource=3,buff=240)]
SPAN=300


def specs_for(id):
    specs=[dict(spec) for spec in SPECS]
    if id=='alejandro':
        next(spec for spec in specs if spec['label']=='Prepared projectile')['resource']=1
        specs.append(dict(label='Expired module cannot duplicate',sequence=CASES[0][1],target=1000,
                          facing=1,distance=320,buff=240,resource=0))
    if id=='leonardo':
        next(spec for spec in specs if spec['label']=='Prepared projectile')['resource']=1
    if id not in PROJECTILE_USERS:
        specs.append(dict(label='Physical signature whiff',sequence=CASES[0][1],target=1000,
                          facing=1,distance=320))
    specs.append(dict(label='Rising strike whiff',sequence=CASES[1][1],target=1010,
                      facing=-1,distance=320))
    if id in {'chan_kof','gameros'}:
        specs.append(dict(label='Confirmed identity branch',sequence=CASES[0][1],target=1000,
                          facing=1,resource=2,buff=240))
        specs.append(dict(label='Unconfirmed identity branch blocked',sequence=CASES[0][1],target=1000,
                          facing=-1,resource=2,buff=240,distance=320))
        if id=='gameros':
            specs.append(dict(label='Gym branch needs gym',sequence=CASES[0][1],target=1000,
                              facing=1,resource=2,buff=0))
    if id=='armando':
        specs.append(dict(label='Remote IoT sensor activation',sequence=CASES[2][1],target=1020,
                          facing=1,distance=300))
    if id=='jaime':
        for direction in ['F','B']:
            specs.append(dict(label='Calculated knight route '+direction,sequence=CASES[0][1],
                              target=1000,facing=1,distance=220,resource=1,direction=direction))
    if id=='leonardo':
        specs.append(dict(label='Continuous swipe crossing',sequence=CASES[2][1],target=1020,
                          facing=1,distance=110))
    return specs


def static_art_check(ids=None):
    """Verify conditional contacts and holding poses from actual AIR timelines.

    Resource-less Push must not expose the paid third contact. A grapple must
    keep its arm/prop extended while TargetBind owns the other fighter.
    """
    from test_teacher_normals import parse_air, read_sff, state_sections, frame_mask
    results={}
    def at_tick(frames,tick):
        clock=0
        for frame in frames:
            if frame['duration']<0 or clock<=tick<clock+frame['duration']: return frame
            clock+=frame['duration']
        return frames[-1]
    for id in ids or PROFILES:
        folder=ROOT/'chars'/id
        actions=parse_air((folder/f'{id}.air').read_text(encoding='utf-8'))
        sprites=read_sff(folder/f'{id}.sff')
        states=state_sections((folder/'kof-extra.cns').read_text(encoding='utf-8'))
        checks={}
        for number in [1000,1010,1020,1030,1040,1070,3000,3500,4000,3015]:
            block=states.get(number)
            if not block: continue
            expression=re.search(r'(?im)^anim\s*=\s*([^;\r\n]+)',block)
            if not expression: continue
            animations={int(n) for n in re.findall(r'\b\d+\b',expression[1]) if int(n)>=8000 and int(n) in actions}
            for change in re.finditer(r'(?ims)^type\s*=\s*ChangeAnim\s*\n(.*?)(?=^\[State |\Z)',block):
                alternate=re.search(r'(?im)^value\s*=\s*(\d+)\s*$',change[1])
                if alternate and int(alternate[1]) in actions: animations.add(int(alternate[1]))
            for animation in animations:
                for index,frame in enumerate(actions[animation]):
                    if frame['hit']:
                        sprite=sprites.get((frame['group'],frame['index']))
                        checks[f'{animation}_{index}_visible_contact']=sprite is not None and any(frame_mask(sprite,frame,box).histogram()[255]>=4 for box in frame['hit'])
            bind=re.search(r'(?ims)^type\s*=\s*TargetBind\s*\n(.*?)(?=^\[State |\Z)',block)
            if bind:
                interval=re.search(r'Time\s*=\s*\[(\d+),(\d+)\]',bind[1],re.I)
                if interval:
                    first,last=map(int,interval.groups())
                    checks[f'{number}_holds_grapple_pose']=bool(animations) and all(
                        at_tick(actions[animation],tick)['index'] in {3,4}
                        for animation in animations for tick in range(first,last+1))
        if id=='leonardo':
            block=states[1000]
            # The first ifelse branch is the stocked animation by contract;
            # evaluate both real timelines rather than trusting a catalog.
            selection=re.search(r'(?im)^anim\s*=\s*ifelse\(\s*var\((?:44|45)\)\s*>\s*0\s*,\s*(\d+)\s*,\s*(\d+)\s*\)',block)
            zero_branch=re.search(r'(?ims)^type\s*=\s*ChangeAnim\s*\ntrigger1\s*=\s*Time\s*=\s*0\s*&&\s*var\(45\)\s*=\s*0\s*\nvalue\s*=\s*(\d+)',block)
            checks['push_conditional_timeline']=selection is not None or zero_branch is not None
            if selection:
                paid,free=map(int,selection.groups())
            elif zero_branch:
                paid=int(re.search(r'(?im)^anim\s*=\s*(\d+)',block)[1])
                free=int(zero_branch[1])
            if selection or zero_branch:
                checks['push_no_third_contact_without_battery']=not at_tick(actions[free],25)['hit']
                checks['push_third_contact_with_battery']=bool(at_tick(actions[paid],25)['hit'])
        results[id]=dict(checks=checks,passed=all(checks.values()))
    (OUT/'art-validation.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    failed=[(id,key) for id,row in results.items() for key,passed in row['checks'].items() if not passed]
    print('Special art checks:',len(results),'fighters;',len(failed),'failures',flush=True)
    for failure in failed: print('FAIL',*failure,flush=True)
    return not failed


def prepare(id):
    folder=ROOT/'chars'/id
    p=PROFILES[id]
    qa='\n; Isolated real-input QA. Never loaded by production definitions.\n'
    qa+=ctl(-2,'Clock','VarAdd','v = 58\nvalue = 1\nignorehitpause = 1','RoundState = 2')
    for idx,spec in enumerate(specs_for(id)):
        if spec['label']=='Counter whiff' and id in COUNTERS:
            target=COUNTERS[id]
            spec=dict(spec,target=target,sequence=CASES[1 if target==1010 else 3][1])
        if spec['label']=='Identity receiving hit' and id=='gameros': spec=dict(spec,resource=3)
        start=idx*SPAN+10
        c=f'var(58) = {start}'
        f=spec['facing']
        distance=spec.get('distance',50)/2
        center=spec.get('center',0)
        if 'whiff' in spec['label'].lower():
            # A distant actor must not be clipped against a stale camera edge
            # before its world-space setup. Otherwise 320px becomes ~140px.
            for redirect in ['', 'redirectID = EnemyNear,ID\n']:
                qa+=ctl(-2,'Preserve whiff world distance','ScreenBound',
                        redirect+'value = 0\nmovecamera = 0,0',f'var(58)=[{start},{start+270}]')
        for kind,params in [('PowerSet',f'value = {spec.get("power",3000)}'),
                            ('LifeSet','value = 500'),
                            ('VarSet',f'v = 40\nvalue = {500 if spec["target"]==4000 else 0}'),
                            ('VarSet',f'v = 46\nvalue = {spec.get("buff",0)}'),
                            ('VarSet',f'v = 48\nvalue = {spec.get("cooldown",0)}'),
                            ('VarSet',f'v = 44\nvalue = {spec.get("resource",0)}'),
                            ('VarSet','v = 45\nvalue = 0'),
                            ('PosSet',f'x = {center-distance*f} - CameraPos X\ny = 0'),
                            ('LifeSet','value = 1000\nredirectID = EnemyNear,ID'),
                            ('PowerSet','value = 1000\nredirectID = EnemyNear,ID'),
                            ('ChangeState','value = 0\nctrl = 1\nredirectID = EnemyNear,ID'),
                            ('VelSet','x = 0\ny = 0\nredirectID = EnemyNear,ID'),
                            ('PosSet',f'x = {center+distance*f} - CameraPos X\ny = 0\nredirectID = EnemyNear,ID'),
                            ('ChangeState','value = 0\nctrl = 1')]:
            qa+=ctl(-2,'Case setup',kind,params,c)
        qa+=ctl(-2,'Facing','Turn','',c+f' && Facing != {f}')
        if 'center' in spec:
            # A one-tick teleport can be clamped against the old screen edge
            # before the camera follows. Move both players in stage coordinates
            # for a short window, allowing the real camera to settle.
            for redirect,position in [('',center-distance*f),('redirectID = EnemyNear,ID\n',center+distance*f)]:
                qa+=ctl(-2,'Camera setup bounds','ScreenBound',redirect+'value = 0\nmovecamera = 1,1',f'var(58) = [{start},{start+SPAN-2}]')
                qa+=ctl(-2,'Camera setup location','PosSet',redirect+f'x = {position} - CameraPos X\ny = 0',f'var(58) = [{start},{start+SPAN-2}]')
        for j,flags in enumerate(spec['sequence']):
            tick=start+8+j*3
            params='\n'.join(f'flag{k+1 if k else ""} = {flag}' for k,flag in enumerate(flags))
            qa+=ctl(-2,'Motion','AssertInput',params,f'var(58) = [{tick},{tick+2}]')
        if 'identity branch' in spec['label'] or spec['label']=='Gym branch needs gym':
            first=9 if id=='chan_kof' else 19
            qa+=ctl(-2,'Identity decision button','AssertInput','flag = a\nignorehitpause = 1',
                    f'StateNo=1000 && Time=[{first},{first+5}] && var(58)=[{start},{start+100}]')
        if spec['label']=='Remote IoT sensor activation':
            for j,flags in enumerate(CASES[4][1]):
                tick=start+70+j*3
                params='\n'.join(f'flag{k+1 if k else ""} = {flag}' for k,flag in enumerate(flags))
                qa+=ctl(-2,'Remote calibration motion','AssertInput',params,f'var(58)=[{tick},{tick+2}]')
        if 'direction' in spec:
            qa+=ctl(-2,'Choose calculated square','AssertInput',f'flag = {spec["direction"]}',
                    f'StateNo=1000 && Time=[10,17] && var(58)=[{start},{start+100}]')
        if spec['label']=='Repeated preparation' and id in {'alejandro','armando'}:
            for j,flags in enumerate(CASES[4][1]):
                tick=start+140+j*3
                params='\n'.join(f'flag{k+1 if k else ""} = {flag}' for k,flag in enumerate(flags))
                qa+=ctl(-2,'Repeat preparation motion','AssertInput',params,f'var(58) = [{tick},{tick+2}]')
        if (id=='leonardo' and spec['target']==3000) or (id in COUNTERS and spec['target']==COUNTERS[id] and 'whiff' not in spec['label'].lower()):
            incoming=25 if spec['target']==1010 else 35
            qa+=ctl(-2,'Incoming strike to test counter','ChangeState','value = 200\nctrl = 0\nredirectID = EnemyNear,ID',f'var(58) = {start+incoming}')
        if spec['label']=='Identity receiving hit' and id in {'cesar','gameros'}:
            qa+=ctl(-2,'Incoming identity test','ChangeState','value = 200\nctrl = 0\nredirectID = EnemyNear,ID',f'var(58) = {start+12}')
        if id=='armando' and spec['label'] in {'Projectile trajectory','Calibrated serve'}:
            # Keep the opponent above the flight path: a hit legitimately
            # removes the ball, so it cannot demonstrate a ground bounce.
            for kind,params in [('PosSet','y = -160'),('VelSet','x = 0\ny = 0'),('ScreenBound','value = 0\nmovecamera = 0,0')]:
                qa+=ctl(-2,'Opponent above bounce test',kind,params+'\nredirectID = EnemyNear,ID',f'var(58) = [{start},{start+260}]')
    for v,expression in [(29,'Vel X'),(30,'Pos Y'),(31,'var(1)')]:
        qa+=ctl(-2,'Projectile observation','VarSet',f'fv = {v}\nvalue = 0','1')
        qa+=ctl(-2,'Projectile observation','VarSet',f'fv = {v}\nvalue = Helper(1005), {expression}','NumHelper(1005) > 0')
    qa+=ctl(-2,'Camera observation','VarSet','fv = 35\nvalue = CameraPos X','1')
    qa+=ctl(-2,'Identity decision observation','VarSet','fv = 37\nvalue = 0','1')
    qa+=ctl(-2,'Identity decision observation','VarSet','fv = 37\nvalue = Helper(1050),StateNo','NumHelper(1050)>0')
    if id=='daniela':
        for v,expression in [(32,'Pos X + CameraPos X'),(33,'StateNo'),(34,'Pos X'),(36,'AnimElemNo(0)')]:
            qa+=ctl(-2,'Victor observation','VarSet',f'fv = {v}\nvalue = Helper(8200), {expression}','NumHelper(8200) > 0')
    cns=(folder/f'{id}.cns').read_text(encoding='utf-8')
    assert '[Statedef -2]' in cns
    cns=cns.replace('[Statedef -2]','[Statedef -2]\n'+qa,1)
    (folder/'teacher-qa.cns').write_text(cns,encoding='utf-8')
    definition=(folder/f'{id}.def').read_text(encoding='utf-8')
    definition=re.sub(r'(?m)^st\s*=.*','st = teacher-qa.cns',definition)
    (folder/'teacher-qa.def').write_text(definition,encoding='utf-8')


def check(id):
    p=PROFILES[id]
    with (OUT/f'{id}.csv').open() as source:
        rows=[[float(v) for v in row] for row in csv.reader(source)]
    results=[]
    for idx,spec in enumerate(specs_for(id)):
        if spec['label']=='Counter whiff' and id in COUNTERS:
            spec=dict(spec,target=COUNTERS[id])
        start=idx*SPAN+18
        window=[r for r in rows if start<=r[0]<start+260]
        target=spec['target']
        states={int(r[1]) for r in window}
        conditions={}
        if target==-1: conditions['cooldown_blocks']=1040 not in states
        elif target==-2: conditions['energy_requirement']=(1040 not in states if p['cost'] else 1040 in states)
        else: conditions['motion']=target in states
        if target>=1000:
            conditions['recovers']=any(r[1]==0 for r in window if r[0]>start+100)
            if target not in [1040] and 'distance' not in spec and spec['label']!='Counter whiff':
                # The move must actually hurt a standing opponent, not just enter
                # a renamed state or display an unconnected visual effect.
                conditions['deals_damage']=any(r[5]<1000 for r in window)
            if target in [3000,3500,4000]:
                conditions['stock_cost']=any(r[1]==target and r[3]==(1000 if target==4000 else 2000) for r in window)
            if target==4000: conditions['consumes_max']=any(r[1]==4000 and r[6]==0 for r in window)
            if target==1040:
                conditions['support_cost']=any(r[1]==1040 and r[3]==3000-p['cost'] for r in window)
                if p['utility']=='heal': conditions['heals']=any(r[4]==500+p['heal']+(30 if id=='felix' and spec.get('resource')==3 else 0) for r in window)
                if p['utility']=='charge': conditions['charges']=any(r[3]==3000+p['gain'] for r in window)
                if p['utility']=='buff': conditions['buff_active']=any(r[7]>0 for r in window)
                if p['utility']=='prepare': conditions['resource_prepared']=any(r[24]>=1 for r in window)
                if id in {'chan_kof','alejandro','armando','jaime','daniela','vladimir','leonardo'}:
                    conditions['support_resource']=any(r[24]>0 for r in window)
                conditions['cooldown_started']=any(r[8]>0 for r in window)
        # These identities must stay visible in the real engine, not be replaced
        # by a Chava tutor or missing sprite.
        if target==1000:
            conditions['projectile_identity']=any(r[9]>0 for r in window) if id in PROJECTILE_USERS else all(r[9]==0 for r in window)
            if id in {'chan_kof','felix','daniela','gameros','vladimir'}:
                conditions['confirmed_resource']=all(r[24]<=spec.get('resource',0) for r in window) if 'distance' in spec else any(r[24]>0 for r in window)
            if id=='leonardo' and 'distance' not in spec:
                if spec.get('resource',0)>0:
                    conditions['paid_third_push_kick']=any(r[5]<=912 for r in window)
                    conditions['push_spends_battery']=any(r[24]==0 and r[25]>0 for r in window)
                else:
                    conditions['two_push_kicks']=any(r[5]<=948 for r in window)
                    conditions['third_push_kick_needs_battery']=all(r[5]>=948 for r in window)
        if target in [3000,4000]:
            conditions['no_device_emitter']=all(r[10]==0 for r in window)
            if id=='leonardo' and target==3000:conditions['counter_triggers']=3015 in states
        if spec['label']=='Prepared projectile' and id=='alejandro': conditions['component_copy']=any(r[11]>0 for r in window)
        if spec['label']=='Expired module cannot duplicate':
            conditions['no_unpaid_component_copy']=all(r[11]==0 for r in window)
        if spec['label'] in {'Physical signature whiff','Rising strike whiff','Unconfirmed identity branch blocked'}:
            conditions['physical_range_respected']=all(r[5]==1000 for r in window)
        if 'whiff' in spec['label'].lower() and spec.get('distance',0)>=320 and window and len(window[0])>34:
            conditions['distant_world_setup']=max(abs(r[16]+r[21]-r[34]) for r in window[:5])>=300
        if spec['label']=='Confirmed identity branch':
            conditions['confirmed_followup']=1030 in states
            if id=='chan_kof': conditions['corrections_spent']=any(r[24]==0 and r[25]>0 for r in window)
        if spec['label'] in {'Unconfirmed identity branch blocked','Gym branch needs gym'}:
            conditions['branch_requirement']=1030 not in states
        if spec['label']=='Remote IoT sensor activation':
            conditions['calibration_command']=1040 in states
            conditions['remote_burst']=any(r[29]==1051 for r in window)
            conditions['sensor_awaits_signal']=any(r[29]==1050 for r in window)
        if 'direction' in spec:
            active=[r for r in window if r[1]==1000]
            conditions['calculation_spent']=any(r[24]==0 for r in active)
            conditions['chosen_knight_route']=any(r[30]==(-2 if spec['direction']=='B' else 2) for r in active)
            conditions['air_route_changes_velocity']=any(r[31]<-3 if spec['direction']=='B' else r[31]>5 for r in active)
        if spec['label']=='Continuous swipe crossing':
            active=[r for r in window if r[1]==1020]
            steps=[abs(b[16]-a[16]) for a,b in zip(active,active[1:]) if b[0]-a[0]==1 and a[17]==b[17]]
            conditions['continuous_travel']=bool(steps) and max(steps)<=13
            conditions['crosses_and_faces_opponent']=any(r[17]==-spec['facing'] for r in active)
            conditions['crossing_kick_hits']=any(r[5]<1000 for r in active)
        if spec['label']=='Prepared alternate super' and id in ['alejandro','armando']:
            conditions['prepared_followup']=any(r[9]>0 for r in window)
        if target==3500 and id=='felix':
            conditions['successful_repair']=any(r[4]==535 for r in window)
        if spec['label']=='Projectile trajectory' and id in PROJECTILE_USERS:
            flight=[r for r in window if r[9]>0]
            conditions['profile_speed']=any(abs(r[13]-p['speed'])<.05 for r in flight)
            if id=='armando': conditions['pingpong_bounces']=any(r[15]>=1 for r in flight)
        if spec['label']=='Ranged signature' and id in ['alejandro','leonardo']:
            conditions['blink_forward']=any(r[16]>-10 for r in window if r[1]==1020)
            conditions['blink_strike']=any(r[5]<1000 for r in window)
        if id in COUNTERS and target==COUNTERS[id]:
            if 'whiff' in spec['label'].lower():
                conditions['no_free_counter_damage']=all(r[5]==1000 for r in window)
                conditions['no_unprovoked_reply']=1070 not in states
            else:
                conditions['physical_counter_reply']=1070 in states
                reply=[r for r in window if r[1]==1070]
                if id=='felix': conditions['counter_repairs_on_hit']=any(r[4]>500 for r in reply)
                if id=='daniela': conditions['counter_becomes_grapple']=any(r[32]==1080 for r in reply)
                if id=='leonardo':
                    conditions['counter_steps_back']=any(r[31]<0 for r in reply)
                    conditions['counter_returns_with_kick']=any(r[31]>0 for r in reply)
        if spec['label']=='Full identity resource' and id in {'chan_kof','vladimir','cesar'}:
            conditions['resource_consumed']=any(r[24]==0 and r[25]==3 for r in window)
        if target==4000:
            if id=='gameros':conditions['boss_transformation']=any(r[7]>400 for r in window)
            if id=='jaime':conditions['knight_leap']=any(r[26]<-20 for r in window)
            if id=='vladimir':
                penalty=150+spec.get('resource',0)*50
                conditions['attendance_energy_penalty']=any(a[28]-b[28]>=penalty for a,b in zip(window,window[1:]) if a[1]==4000 and b[1]==4000)
        if spec['label']=='Identity receiving hit' and id in {'cesar','gameros'}:
            conditions['incoming_hit_lands']=any(r[4]<500 for r in window)
            conditions['identity_hit_reaction']=any(r[24]==(1 if id=='cesar' else 0) and r[4]<500 for r in window)
            jab=re.search(r'(?ims)^\[Statedef 200\](.*?)(?=^\[Statedef |\Z)',(ROOT/'chars/chava/chava.cns').read_text(encoding='utf-8'))
            damage=int(re.search(r'(?im)^damage\s*=\s*(\d+)',jab[1])[1])
            conditions['armor_did_not_leak']=any(r[4]==500-damage for r in window)
        if spec['label']=='Preparation expires' and id in {'alejandro','armando'}:
            conditions['preparation_expires']=any(r[24]==0 and r[7]==0 for r in window if r[0]>start+80)
        if spec['label']=='Repeated preparation' and id in {'alejandro','armando'}:
            conditions['can_accumulate_preparation']=any(r[24]>=2 for r in window)
        if spec['label']=='Calibrated serve' and id=='armando':
            conditions['extra_ground_rebounds']=any(r[15]>=5 for r in window)
            conditions['lateral_return']=any(r[13]<0 for r in window)
        conditions['resource_cap']=all(0<=r[24]<=3 for r in window)
        conditions['stays_above_floor']=all(r[26]<=1 for r in window)
        conditions['helpers_clean_up']=all(r[9]==0 and r[10]==0 and r[11]==0 and r[27]==0 for r in window if r[0]>start+230)
        if id=='daniela':
            conditions['victor_present']=all(r[12]==1 for r in window)
            idle=[r for r in window if r[19]==8200]
            conditions['desk_fixed_in_stage']=bool(idle) and all(abs(r[18]-120)<.02 for r in idle)
            if target in [3000,4000]:
                actor_states={int(r[19]) for r in window}
                conditions['victor_rises_punches_sits']={8210,8212,8214}<=actor_states
                conditions['victor_back_home']=any(r[19]==8200 and r[0]>start+140 for r in window)
            if spec['label'] in {'Desk camera left','Desk camera right'}:
                delta=window[-1][21]-window[0][21]
                conditions['camera_moved']=abs(delta)>1
                conditions['camera_direction']=(delta<-1 if spec['label']=='Desk camera left' else delta>1)
            if spec['label']=='Desk camera left':
                conditions['victor_can_leave_screen']=any(r[22]>160 for r in window)
        results.append(dict(label=spec['label'],facing=spec['facing'],checks=conditions,passed=all(conditions.values())))
    if id=='daniela':
        idle=[r for r in rows if r[19]==8200]
        camera_rows=[]
        for idx,spec in enumerate(specs_for(id)):
            if spec['label'] not in {'Desk camera left','Desk camera right'}: continue
            start=idx*SPAN+18
            camera_rows.extend(r for r in rows if start<=r[0]<start+260)
        checks={'typing_frames':len({int(r[23]) for r in idle if r[23]<=18})>=6,
                'phone_frames':any(r[23]>=21 for r in idle),
                'camera_sweeps_across_stage':bool(camera_rows) and max(r[21] for r in camera_rows)-min(r[21] for r in camera_rows)>60,
                'desk_fixed_through_whole_camera_sweep':bool(camera_rows) and all(abs(r[18]-120)<.02 for r in camera_rows)}
        results.append(dict(label='Victor typing and phone',checks=checks,passed=all(checks.values())))
    failures=[r for r in results if not r['passed']]
    print(id,len(results),'cases,',len(failures),'failed',flush=True)
    for r in failures: print(r,flush=True)
    return results


def main():
    names=[name for name in sys.argv[1:] if name!='--static']
    assert not set(names)-PROFILES.keys(),('Unknown characters',set(names)-PROFILES.keys())
    assert static_art_check(names or None),'Special animation failures (see art-validation.json)'
    if '--static' in sys.argv: return
    config_before=(ROOT/'save/config.ini').read_bytes()
    config=(ROOT/'save/config.ini').read_text(encoding='utf-8-sig')
    config=re.sub(r'(?m)^Lua\s*=.*','Lua = loop(), dofile("scratch/teacher-specials-qa/observer.lua")',config)
    config=re.sub(r'(?m)^ScreenshotFolder\s*=.*','ScreenshotFolder = scratch/teacher-specials-qa',config)
    (OUT/'config.ini').write_text(config,encoding='utf-8')
    (OUT/'observer.lua').write_text('''
if player(1) and roundState() == 2 then
  local t = var(58)
  if t > 0 and t ~= teacherLastTick then
    teacherLastTick = t
    local values = {t, stateNo(), time(), power(), life(), 0, var(40), var(46), var(48), numHelper(1005), numHelper(3010), numHelper(1006), numHelper(8200), fvar(29), fvar(30), fvar(31), posX(), facing(), fvar(32), fvar(33), numHelper(8219), fvar(35), fvar(34), fvar(36), var(44), var(45), posY(), numHelper(1050), 0, fvar(37), var(42), velX(), 0, 0, 0}
    if teacherQAID == "daniela" and (t == 120 or t == 260 or t == 1550 or t == 1590 or t == 1630) then screenshot() end
    local signature = {chan_kof=1010, felix=1010, alejandro=1040, daniela=1010, gameros=1040, armando=1040, vladimir=1000, jaime=1000, leonardo=1000, cesar=1000}
    teacherCaptured = teacherCaptured or {}
    if stateNo() == signature[teacherQAID] and time() >= 18 and not teacherCaptured[teacherQAID] then
      teacherCaptured[teacherQAID] = true
      screenshot()
    end
    if enemyNear() then values[6] = life(); values[29] = power(); values[33]=stateNo(); values[34]=posY(); values[35]=posX()+values[22] end
    player(1)
    local f = assert(io.open("scratch/teacher-specials-qa/" .. teacherQAID .. ".csv", "a"))
    f:write(table.concat(values, ",") .. "\\n")
    f:close()
    if t >= teacherQALimit then os.exit() end
  end
end
''',encoding='utf-8')
    report=OUT/'validation.json'
    results=json.loads(report.read_text(encoding='utf-8')) if names and report.exists() else {}
    for id in names or PROFILES:
        prepare(id)
        output=OUT/f'{id}.csv'
        if output.exists(): output.unlink()
        # One isolated module sets the identifier; it does not replace menus.
        (OUT/'id.lua').write_text(f'teacherQAID = "{id}"\nteacherQALimit = {len(specs_for(id))*SPAN}\n',encoding='utf-8')
        cfg=config.replace('loop(), dofile(', 'loop(), dofile("scratch/teacher-specials-qa/id.lua"), dofile(')
        (OUT/'config.ini').write_text(cfg,encoding='utf-8')
        proc=subprocess.run([str(ROOT/'TheKingOfUTc.exe'),'-config',str(OUT/'config.ini'),'-p1',f'{id}/teacher-qa.def','-p2','chava','-s','stages/patio.def','-rounds','1','-time','-1','-speedtest','-nosound','-windowed'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=45)
        assert proc.returncode==0,(id,proc.stdout.decode(errors='replace')[-2500:])
        results[id]=check(id)
    assert (ROOT/'save/config.ini').read_bytes()==config_before,'Global configuration changed'
    report.write_text(json.dumps(results,indent=2),encoding='utf-8')
    assert all(r['passed'] for cases in results.values() for r in cases),'Input/behavior failures (see validation.json)'


if __name__=='__main__': main()
