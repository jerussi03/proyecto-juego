"""Physical supers with different roles; no shared device shooting template."""

def second(id,p,state,ctl,hit,end):
    """Alternate super: a different role from each teacher's main super."""
    n=3500
    anim={'chan_kof':8736,'felix':8736,'alejandro':8730,'daniela':8721,
          'gameros':8721,'armando':8736,'vladimir':8730,'jaime':8736,
          'leonardo':8736,'cesar':8730}[id]
    out=state(n,anim,cost=1000)
    out+=ctl(n,'Super freeze','SuperPause','time = 18\nmovetime = 18\nanim = -1\ndarken = 1\np2defmul = 1')
    def strike(d,t,**kw):
        return hit(n,d,trigger=f'Time = {t}',supermove=True,**kw)
    def advance(speed,start,stop):
        return ctl(n,'Advance','VelSet',f'x = {speed}',f'Time = [{start},{stop}]')+ctl(n,'Plant feet','VelSet','x = 0',f'Time = {stop+1}')
    if id=='chan_kof':
        # Crossfit circuit: sustained alternating kicks rather than weight rush.
        out+=advance(2.2,4,32)
        for t in [8,16,24,32]: out+=strike(28,t,velocity='-0.5',stun=25)
        out+=strike(65,40,fall=True,lift=True)
    elif id=='felix':
        # Maintenance stance absorbs a hit and restores a little health at finish.
        out+=ctl(n,'Grounded maintenance','DefenceMulSet','value = 0.6','Time < 28')
        out+=strike(70,10,velocity='-0.5',stun=32)
        out+=strike(95,30,fall=True,lift=True)
        out+=ctl(n,'Successful repair','LifeAdd','value = 35\nkill = 0','Time = 38 && MoveHit')
    elif id=='alejandro':
        # Compiled combo stays in place; preparation adds one final component.
        for t in [8,16,24]: out+=strike(38,t,velocity='-0.5',stun=24)
        out+=strike(65,36,fall=True,lift=True)
        out+=ctl(n,'Compiled component','Helper','name = "Compiled component"\nID = 1005\nstateno = 1005\npostype = p1\npos = 35,-58\nownpal = 1','Time = 28 && var(46) > 0')
    elif id=='daniela':
        # Daniela fights this super herself; Victor continues his background work.
        out+=advance(3.8,5,24)
        out+=strike(55,12,velocity='-0.5',stun=27)
        out+=strike(55,24,velocity='-0.5',stun=27)
        out+=strike(70,36,fall=True,lift=True)
    elif id=='gameros':
        # Motorcycle cross-through; one hit per pass, then brake.
        out+=ctl(n,'Pass through','PlayerPush','value = 0','Time < 32')
        out+=advance(8,4,16)
        out+=strike(75,4,velocity='-0.5',stun=30)
        out+=ctl(n,'Turn motorcycle','Turn','','Time = 18 && P2Dist X < 0')
        out+=advance(6,19,30)
        out+=strike(100,19,fall=True,lift=True)
    elif id=='armando':
        # Prepared IoT adds a second bounce to a close-range sports combination.
        out+=advance(3,4,22)
        for t in [8,20,32]: out+=strike(55,t,velocity='-0.7',fall=t==32,lift=t==32)
        out+=ctl(n,'Prepared rebound','Helper','name = "IoT rebound"\nID = 1005\nstateno = 1005\npostype = p1\npos = 35,-35\nownpal = 1','Time = 26 && var(46) > 0')
    elif id=='vladimir':
        # Patrol pulls the student in, then sends them back to class.
        out+=advance(4.2,4,18)
        out+=strike(65,8,velocity='2',stun=35)
        out+=strike(105,28,fall=True,lift=True)
    elif id=='jaime':
        # Cycling footwork expressed as a stationary pedal kick series.
        for t in [6,12,18,24,30,36]: out+=strike(23,t,velocity='-0.3',stun=23)
        out+=strike(50,44,fall=True,lift=True)
    elif id=='leonardo':
        # Fast offensive alternative to the reactive counter super.
        out+=ctl(n,'Swipe afterimages','AfterImage','time = 32\nlength = 5\ntimegap = 2\nframegap = 2\ntrans = add','Time = 4')
        out+=advance(5.2,4,22)
        out+=strike(45,8,velocity='-0.5',stun=28)
        out+=strike(45,18,velocity='-0.5',stun=28)
        out+=strike(80,30,fall=True,lift=True)
    elif id=='cesar':
        # Strict examination: slow startup, two heavy blows, no chair rush.
        out+=strike(85,16,velocity='-0.5',stun=38)
        out+=strike(110,36,fall=True,lift=True)
        out+=ctl(n,'Strict finish','EnvShake','time = 10\nfreq = 60\nampl = -4','Time = 36')
    out+=end(n,58)
    return out

def build(id,p,n,state,ctl,hit,end):
    maximum=n==4000
    cost=2000 if maximum else 1000
    factor=1.3 if maximum else 1
    def contact(damage,tick,**kwargs):
        return hit(n,round(damage*factor),trigger=f'Time = {tick}',supermove=True,**kwargs)
    anim=8730 if id in {'gameros','felix','leonardo','alejandro'} else 8721
    out=state(n,anim,cost=cost)
    out+=ctl(n,'Super freeze','SuperPause','time = 18\nmovetime = 18\nanim = -1\ndarken = 1\np2defmul = 1')
    if id=='daniela':
        out+=ctl(n,'Requirements for partner','VarSet','v = 45\nvalue = var(44)','Time = 8')
        out+=ctl(n,'Partner consumes requirements','VarSet','v = 44\nvalue = 0','Time = 8')
        out+=ctl(n,'Victor leave the desk','VarSet','v = 47\nvalue = 1','Time = 8')
        if maximum:
            out+=ctl(n,'Partner advance','VelSet','x = 3.5','Time = [12,28]')
            out+=ctl(n,'Brake','VelSet','x = 0','Time = 29')
            out+=contact(80,20,fall=False,velocity='-1')
        out+=end(n,54)
    elif id=='chan_kof':
        out+=ctl(n,'Crossfit power carry','VelSet','x = 4.0','Time = [5,28]')
        out+=ctl(n,'Brake','VelSet','x = 0','Time = 29')
        out+=contact(45,18,velocity='-1')
        out+=contact(45,28,velocity='-1')
        out+=contact(75,38,fall=True,lift=True)
        out+=ctl(n,'Weight impact','EnvShake','time = 12\nfreq = 70\nampl = -4','Time = 38')
        out+=end(n,54)
    elif id=='felix':
        out+=ctl(n,'Close circuit','VelSet','x = 2.6','Time = [5,14]')
        out+=ctl(n,'Stop','VelSet','x = 0','Time = 15')
        for tick in [8,14,20,26]:out+=contact(27,tick,velocity='-0.5',stun=26)
        out+=contact(60,32,fall=True,lift=True)
        out+=ctl(n,'Restart flash','PalFX','time = 10\nadd = 60,100,140','Time = 26')
        out+=end(n,48)
    elif id=='alejandro':
        out+=ctl(n,'Refactor step','PosAdd','x = min(95,max(0,P2BodyDist X-18))','Time = 5')
        out+=ctl(n,'Cross through the component','PlayerPush','value = 0','Time < 26')
        out+=ctl(n,'Component afterimages','AfterImage','time = 32\nlength = 7\ntimegap = 2\nframegap = 2\ntrans = add','Time = 4')
        out+=contact(50,8,velocity='-1')
        out+=ctl(n,'Second refactor','PosAdd','x = min(55,max(0,P2BodyDist X-14))','Time = 19')
        out+=contact(50,20,velocity='-1')
        out+=contact(75,32,fall=True,lift=True)
        out+=end(n,48)
    elif id=='gameros':
        out+=ctl(n,'Gym footwork','VelSet','x = 3.2','Time = [4,14]')
        out+=ctl(n,'Stop','VelSet','x = 0','Time = 15')
        out+=contact(45,8,velocity='-1')
        out+=contact(50,20,velocity='-1')
        out+=contact(80,32,fall=True,lift=True)
        out+=end(n,48)
    elif id=='armando':
        out+=ctl(n,'Jump','VelSet','x = 3.8\ny = -5.5','Time = 3')
        out+=ctl(n,'Gravity','VelAdd','y = 0.38','Time = [4,17]')
        out+=ctl(n,'Dunk descent','VelSet','x = 2.6\ny = 7','Time = 18')
        out+=contact(65,18,fall=False,velocity='-1')
        out+=ctl(n,'Plant feet','PosSet','y = 0','Time = 29')
        out+=ctl(n,'Land','VelSet','x = 0\ny = 0','Time = 29')
        out+=ctl(n,'Ground finish animation','ChangeAnim','value = 8732','Time = 29')
        out+=contact(105,29,fall=True,lift=True)
        out+=ctl(n,'Court shake','EnvShake','time = 14\nfreq = 80\nampl = -5','Time = 29')
        out+=end(n,50)
    elif id=='vladimir':
        out+=ctl(n,'Attendance grab animation','ChangeAnim','value = 8733')
        out+=ctl(n,'Grab approach','VelSet','x = 3.0','Time = [3,10]')
        out+=ctl(n,'Stop','VelSet','x = 0','Time = 11')
        out+=ctl(n,'Grab','HitDef',f'attr = S,HT\nhitflag = M-\nguardflag = \npriority = 1,Miss\ndamage = {round(155*factor)},0\npausetime = 0,0\nsparkno = -1\np1stateno = -1\np2stateno = 8850\nfall = 1\nground.velocity = -5,-4\nair.velocity = -5,-4\ngetpower = 0,0','Time = 12')
        out+=ctl(n,'Keep student for the conference','TargetBind','time = 1\npos = 38,-8','Time = [13,30] && NumTarget > 0')
        out+=ctl(n,'Release','TargetState','value = 8851','Time = 31 && NumTarget > 0')
        out+=end(n,48)
    elif id=='jaime':
        out+=ctl(n,'Cycling strike animation','ChangeAnim','value = 8734')
        out+=ctl(n,'Cycling gambit','PlayerPush','value = 0','Time < 25')
        out+=ctl(n,'Bike dash','VelSet','x = 7','Time = [4,16]')
        out+=contact(65,4,velocity='-1')
        out+=ctl(n,'Turn after passing','Turn','','Time = 17 && P2Dist X < 0')
        out+=ctl(n,'Return pass','VelSet','x = 3.5','Time = [18,24]')
        out+=ctl(n,'Brake','VelSet','x = 0','Time = 25')
        out+=contact(100,32,fall=True,lift=True)
        out+=end(n,54)
    elif id=='leonardo':
        out+=ctl(n,'Airplane counter stance','ChangeAnim','value = 120')
        out+=ctl(n,'Counter incoming strike','HitOverride','attr = SCA,NA,SA,HA,NP,SP,HP\nslot = 0\nstateno = 3015\ntime = 1','Time = [3,27]')
        out+=ctl(n,'Remember counter power','VarSet',f'v = 49\nvalue = {round(170*factor)}')
        out+=end(n,42)
    elif id=='cesar':
        out+=ctl(n,'Chair armor','DefenceMulSet','value = 0.55','Time = [4,32]')
        out+=ctl(n,'Walk with support','VelSet','x = 3.1','Time = [5,28]')
        out+=ctl(n,'Stop','VelSet','x = 0','Time = 29')
        out+=contact(175,24,fall=True,lift=True)
        out+=ctl(n,'Heavy finish','EnvShake','time = 10\nfreq = 60\nampl = -4','Time = 24')
        out+=end(n,54)
    return out


def extra(id,state,ctl,hit,end):
    out=''
    if id=='leonardo':
        out+=state(3015,8730)
        out+=ctl(3015,'Face the attacker','Turn','','Time = 0 && P2Dist X < 0')
        out+=ctl(3015,'Counter step','PosAdd','x = min(90,max(0,P2BodyDist X-18))')
        out+=ctl(3015,'Counter immunity','NotHitBy','value = SCA\ntime = 1','Time < 10')
        out+=hit(3015,'var(49)',trigger='Time = 8',supermove=True,fall=True,lift=True)
        out+=end(3015,42)
    if id=='vladimir':
        out+=state(8850,5000,move='H',kind='A')
        out+=ctl(8850,'Victim own animation','ChangeAnim','value = 5000')
        out+=ctl(8850,'Throw timeout','SelfState','value = 5050','Time > 24')
        out+=state(8851,5050,move='H',kind='A')
        out+=ctl(8851,'Release into own fall','SelfState','value = 5050\nctrl = 0')
    return out
