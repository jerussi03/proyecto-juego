"""Playable identities: attacks, movement, resources and MAX2, not skin swaps.

Uses the cast's existing original art at native scale. 44 = resource (0..3),
45 = spent resource snapshot, 46 = prepared-mode ticks, 50 = hit latch.
42 is local to Jaime's airborne route choice and never survives his special.
"""
import re

IDENTITIES = {
 'chan_kof': dict(role='Precision / crossfit',resource='Correcciones',walk=1.65,run=4.1,jump=-8.7,tempo=1.05,
   notes=['Gana correcciones al conectar Examen SQL o punio fuerte.', 'Tras confirmar SQL, pulsa B para cancelar a Indice Cluster y gastar correcciones.', 'SQL es un golpe corto; Senderismo salta; Crossfit golpea alto.']),
 'felix': dict(role='Reparacion / contraataque',resource='Diagnosticos',walk=1.4,run=3.5,jump=-7.8,tempo=1.12,
   notes=['Gana diagnosticos conectando Llave o Cable a Tierra.', 'Reparacion baja cura mas con diagnosticos; Mantenimiento los consume.', 'Reinicio bloquea, responde sin teletransportarse y recupera vida al confirmar.']),
 'alejandro': dict(role='Preparacion / trampas',resource='Modulos',walk=1.8,run=4.6,jump=-8.6,tempo=.9,
   notes=['Importar prepara modulos durante cuatro segundos.', 'Cada copia Angular gasta un modulo real; el temporizador solo conserva el stock.', 'Refactor cruza al rival; Error planta una trampa de piso.']),
 'daniela': dict(role='Presion / asistencia',resource='Requisitos',walk=1.7,run=4,jump=-8.1,tempo=1,
   notes=['UML encadena tres golpes y acumula requisitos.', 'Documento prepara otro requisito; Victor los consume al acudir.', 'Revision intercepta golpes cuerpo a cuerpo con una llave; no refleja proyectiles.']),
 'gameros': dict(role='Rachas / gimnasio',resource='Racha',walk=1.95,run=5,jump=-9,tempo=.8,
   notes=['Encadena golpes para ganar racha; recibir un golpe la rompe.', 'En Gym y con dos puntos de racha, confirma Arcade y pulsa B para encadenar Pedal.', 'Boxeo, patada ascendente, moto y pedal tienen trayectorias propias.']),
 'armando': dict(role='Rebotes / IoT',resource='Calibraciones',walk=1.75,run=4.3,jump=-9.2,tempo=.95,
   notes=['Calibrar prepara rebotes extra y activa a distancia el sensor instalado.', 'Pingpong rebota; Clavada salta y golpea al caer.', 'El sensor espera proximidad y eleva al rival; una trampa de Angular solo golpea bajo.']),
 'vladimir': dict(role='Agarres / retencion',resource='Asistencias',walk=1.5,run=3.6,jump=-7.8,tempo=1.15,
   notes=['Invitacion es un agarre: no lanza objetos.', 'Gana asistencias con agarres o Pase de Lista.', 'Honores gasta asistencias: atrae al rival y le retira energia al conectar.']),
 'jaime': dict(role='Saltos / calculo',resource='Calculos',walk=1.85,run=4.8,jump=-9.4,tempo=.92,
   notes=['Calculo Mental prepara hasta tres calculos.', 'Durante Caballo, mantener adelante o atras consume un calculo y corrige la ruta.', 'Potencia gasta calculos para lanzar mas alto; Bicicleta avanza y Derivada retrocede.']),
 'leonardo': dict(role='Evasion / patadas',resource='Bateria',walk=2.15,run=5.4,jump=-8.9,tempo=.78,
   notes=['Modo Avion evade y carga bateria; contrarrestar tambien carga.', 'Push gasta bateria para una tercera patada.', 'Swipe cruza corriendo; Scroll retrocede y vuelve con una patada, sin teletransporte.']),
 'cesar': dict(role='Resistencia / castigo',resource='Rigor',walk=1.15,run=2.9,jump=-7.2,tempo=1.28,
   notes=['Recibir golpes aumenta Rigor: hasta tres puntos.', 'DELETE consume Rigor en un agarre; Silla usa un punto para reforzar su resistencia.', 'Pastillas curan tras una pausa larga; el baston castiga a distancia.']),
}
PROJECTILE_USERS={'alejandro','armando'}
COUNTERS={'felix':1010,'daniela':1010,'leonardo':1030}


def build(id,p,state,ctl,hit,end,helper,projectile):
    out='; Independent teacher identity, generated from teacher_identity.py\n'
    def s(n,anim,duration,body='',kind='S',move='A',cost=0):
        return state(n,anim,kind=kind,move=move,cost=cost)+body+end(n,duration)
    def h(n,d,t=8,**kw): return hit(n,d,trigger=f'Time = {t}',**kw)
    def move(n,speed,a,b):
        return ctl(n,'Footwork','VelSet',f'x = {speed}',f'Time = [{a},{b}]')+ctl(n,'Brake','VelSet','x = 0',f'Time = {b+1}')
    def gain(n,t,amount=1):
        return ctl(n,'Resource gain','VarSet',f'v = 44\nvalue = min(3,var(44)+{amount})',f'Time = {t}')
    def spend(n):
        return ctl(n,'Remember resource','VarSet','v = 45\nvalue = var(44)')+ctl(n,'Spend resource','VarSet','v = 44\nvalue = 0')
    def leap(n,vx,vy,land=30):
        return (ctl(n,'Takeoff','VelSet',f'x = {vx}\ny = {vy}','Time = 3')
          +ctl(n,'Airborne','StateTypeSet','statetype = A','Time = 3')
          +ctl(n,'Arc gravity','VelAdd','y = 0.5',f'Time = [4,{land-1}] && StateType = A')
          +ctl(n,'Landing position','PosSet','y = 0',f'Time >= {land}\ntrigger2 = Time > 3 && Vel Y>0 && Pos Y+Vel Y>=0')
          +ctl(n,'Landing brake','VelSet','x = 0\ny = 0',f'Time >= {land}\ntrigger2 = Time > 3 && Vel Y>0 && Pos Y+Vel Y>=0')
          +ctl(n,'Grounded','StateTypeSet','statetype = S',f'Time >= {land}\ntrigger2 = Time > 3 && Pos Y>=0 && Vel Y>=0'))
    def counter(n):
        # Daniela catches an arm to revise the student's work. A distant
        # projectile cannot become a magical command throw on its owner.
        attr='SCA,NA,SA,HA' if id=='daniela' else 'SCA,NA,SA,HA,NP,SP,HP'
        return ctl(n,'Read incoming attack','HitOverride',f'attr = {attr}\nslot = 0\nstateno = 1070\ntime = 1','Time = [3,23]')
    def grab(n,damage):
        return (ctl(n,'Command grab','HitDef',f'attr = S,ST\nhitflag = M-\nguardflag =\npriority = 1,Miss\ndamage = {damage},0\npausetime = 0,0\nsparkno = -1\np2stateno = 1080\nfall = 1\ngetpower = 30,0','Time = 8')
          +ctl(n,'Hold opponent','TargetBind','time = 1\npos = 32,-4','Time = [9,20] && NumTarget > 0')
          +ctl(n,'Release opponent','TargetState','value = 1081','Time = 21 && NumTarget > 0'))
    def trap(n,child,duration):
        if id=='armando':
            # IoT is an armed proximity sensor. Unlike Alejandro's immediate
            # low trap, it remains harmless until a visitor or remote signal.
            out=state(child,8703,kind='C',move='I')
            out+=ctl(child,'Sensor rests on floor','PosSet','y = -12','1')
            out+=ctl(child,'Sensor stays in the stage','ScreenBound','value = 0\nmovecamera = 0,0','1')
            out+=ctl(child,'Sensor no push','PlayerPush','value = 0','1')
            out+=ctl(child,'Sensor can be broken','HitOverride','attr = SCA,AA,AP,AT\nslot = 0\nstateno = 3021\ntime = 1','1')
            out+=ctl(child,'Detect nearby visitor','ChangeState','value = 1051','Time >= 8 && Abs(P2Dist X)<46 && P2Dist Y > -85')
            out+=ctl(child,'Remote calibration signal','ChangeState','value = 1051','Root,StateNo = 1040 && Root,Time = 24')
            out+=ctl(child,'Sensor timeout','DestroySelf','',f'Time >= {duration}\ntrigger2 = RoundState != 2\ntrigger3 = Root,Life <= 0')
            out+=state(1051,8750,kind='C')
            out+=ctl(1051,'Active sensor no push','PlayerPush','value = 0','1')
            out+=ctl(1051,'Active sensor stage bounds','ScreenBound','value = 0\nmovecamera = 0,0','1')
            out+=hit(1051,'55+(Root,var(44))*9',trigger='Time = 0',projectile=True,fall=True,lift=True)
            out+=ctl(1051,'Sensor contact cleanup','ChangeState','value = 3021','MoveContact')
            out+=ctl(1051,'Sensor burst cleanup','DestroySelf','','Time >= 16\ntrigger2 = RoundState != 2\ntrigger3 = Root,Life <= 0')
            return out
        return (state(child,8700 if id=='alejandro' else 8703,kind='C')
          +ctl(child,'Keep trap on floor','PosSet','y = -12','1')
          +ctl(child,'Trap does not move camera','ScreenBound','value = 0\nmovecamera = 0,0','1')
          +ctl(child,'No push','PlayerPush','value = 0','1')
          +ctl(child,'Trap can be broken','HitOverride','attr = SCA,AA,AP,AT\nslot = 0\nstateno = 3021\ntime = 1','1')
          +hit(child,'ifelse(Root,var(46)>0,80,55)',trigger='Time = 0',projectile=True,low=True,fall=True)
          +ctl(child,'Impact','ChangeState','value = 3021','MoveContact')
          +ctl(child,'Trap timeout','DestroySelf','',f'Time >= {duration}\ntrigger2 = RoundState != 2\ntrigger3 = Root,Life <= 0'))

    if id=='chan_kof':
        body=h(1000,55,8,velocity='-1.5',stun=25)
        body+=ctl(1000,'Correct the confirmed query','ChangeState','value = 1030\nctrl = 0','Time >= 9 && MoveHit && var(44)>0 && command = "a"')
        out+=s(1000,8740,30,body)
        out+=s(1010,8741,38,h(1010,88,24,fall=True,lift=True)+ctl(1010,'Crossfit brace','DefenceMulSet','value = .7','Time < 14'))
        out+=s(1020,8742,46,leap(1020,3.9,-5.5,28)+h(1020,78,16,fall=True))
        body=spend(1030)
        for t in [8,16,24]: body+=h(1030,'22+var(45)*5',t,low=True,velocity='-0.5',stun=24,fall=t==24)
        out+=s(1030,8743,36,body,kind='C')
    elif id=='felix':
        out+=s(1000,8740,35,move(1000,2.6,3,11)+h(1000,64,8,stun=27))
        out+=s(1010,8741,34,counter(1010),move='I')
        out+=s(1020,8742,38,move(1020,3.3,4,16)+h(1020,65,12,low=True)+ctl(1020,'Repair on contact','LifeAdd','value = 12+var(44)*4\nkill = 0','Time = 24 && MoveHit'),kind='C')
        out+=s(1030,8743,40,h(1030,52,10,low=True,velocity='-0.3',stun=38)+ctl(1030,'Grounded cable','VelSet','x = -1.8','Time = [20,30]'),kind='C')
    elif id=='alejandro':
        body=ctl(1000,'Clear confirm','VarSet','v = 43\nvalue = 0')+helper(1000,1005,trigger='Time = 8')
        body+=helper(1000,1005,35,-84,'Time = 14 && var(44)>0',identity=1006)
        body+=ctl(1000,'Consume imported module','VarSet','v = 44\nvalue = max(0,var(44)-1)','Time = 15 && var(44)>0')
        out+=s(1000,8740,30,body)+projectile(1005,p)
        out+=s(1010,8741,36,ctl(1010,'Inject next to opponent','PosAdd','x = min(65,max(0,P2BodyDist X-24))','Time = 5')+h(1010,75,10,fall=True,lift=True))
        body=ctl(1020,'Refactor trail','AfterImage','time = 24\nlength = 6\ntimegap = 2\nframegap = 2\ntrans = add')
        body+=ctl(1020,'Cross through','PlayerPush','value = 0','Time < 16')
        body+=ctl(1020,'Refactor position','PosAdd','x = min(150,max(0,P2BodyDist X+28))','Time = 8')
        body+=ctl(1020,'Face refactored opponent','Turn','','Time = 9 && P2Dist X < 0')+h(1020,68,12,stun=27)
        out+=s(1020,8742,34,body)
        out+=s(1030,8743,32,helper(1030,1050,42,-12,'Time = 8 && NumHelper(1050)=0')+ctl(1030,'Step away from error','VelSet','x = -2.2','Time = [10,20]')+ctl(1030,'Stop','VelSet','x = 0','Time = 21'))
        out+=trap(1030,1050,90)
    elif id=='daniela':
        body=''
        for t in [7,15,23]: body+=h(1000,23,t,velocity='-0.4',stun=24)
        out+=s(1000,8740,34,body)
        out+=s(1010,8741,34,counter(1010),move='I')
        out+=s(1020,8742,40,move(1020,4.2,4,16)+h(1020,82,12,fall=True))
        out+=s(1030,8743,34,move(1030,2,2,7)+grab(1030,80))
    elif id=='gameros':
        body=move(1000,'ifelse(var(46)>0,2.4,1.4)',2,12)
        for t in [6,12,18]: body+=h(1000,'17+var(44)*3+ifelse(var(46)>0,5,0)',t,velocity='-0.4',stun=22)
        body+=ctl(1000,'Arcade gym follow-up','ChangeState','value = 1030\nctrl = 0','Time >= 19 && MoveHit && var(46)>0 && var(44)>=2 && command = "a"')
        out+=s(1000,8740,28,body)
        out+=s(1010,8741,42,leap(1010,1.8,-5.8,27)+h(1010,76,8,fall=True,lift=True))
        out+=s(1020,8742,36,move(1020,'ifelse(var(46)>0,9,7.4)',3,20)+h(1020,'80+var(44)*6',6,fall=True)+ctl(1020,'Ride through','PlayerPush','value = 0','Time < 21'))
        out+=s(1030,8743,36,move(1030,4.2,3,12)+h(1030,32,7,low=True,velocity='-0.5')+h(1030,40,19,low=True,fall=True),kind='C')
    elif id=='armando':
        out+=s(1000,8740,30,helper(1000,1005,trigger='Time = 8'))+projectile(1005,p)
        out+=s(1010,8741,44,leap(1010,2.5,-6,27)+h(1010,42,10,velocity='-0.5')+h(1010,65,27,fall=True,lift=True)+ctl(1010,'Court impact','EnvShake','time = 8\nfreq = 70\nampl = -3','Time = 27'))
        out+=s(1020,8742,32,helper(1020,1050,42,-12,'Time = 8 && NumHelper(1050)=0'))+trap(1020,1050,110)
        out+=s(1030,8743,35,move(1030,2.5,3,18)+h(1030,35,8,velocity='-0.5')+h(1030,'40+var(44)*7',20,fall=True))
    elif id=='vladimir':
        out+=s(1000,8740,34,move(1000,2.5,2,7)+grab(1000,78))
        out+=s(1010,8741,38,h(1010,73,12,velocity='2',fall=True,lift=True))
        out+=s(1020,8742,42,ctl(1020,'Door brace','DefenceMulSet','value = .5','Time = [4,24]')+h(1020,70,18,velocity='-7',stun=32))
        body=spend(1030)+h(1030,'65+var(45)*14',16,low=True,fall=True,velocity='ifelse(var(45)>0,2,-4)',stun=34)
        body+=ctl(1030,'Retain attendance energy','TargetPowerAdd','value = -50*var(45)','Time = 17 && MoveHit && NumTarget>0 && var(45)>0')
        body+=ctl(1030,'Attendance shake','EnvShake','time = 10\nfreq = 65\nampl = -4','Time = 16')
        out+=s(1030,8743,42,body)
    elif id=='jaime':
        body=ctl(1000,'Reset knight route','VarSet','v = 42\nvalue = 0')+leap(1000,2.5,-6,29)
        body+=ctl(1000,'Calculate an airborne square','VarSet','v = 42\nvalue = ifelse(command="holdback",-1,1)','Time = [10,17] && var(42)=0 && var(44)>0 && (command="holdfwd" || command="holdback")')
        body+=ctl(1000,'Apply calculated knight route','VelSet','x = ifelse(var(42)<0,-3.8,5.2)','Time = [10,17] && Abs(var(42))=1')
        body+=ctl(1000,'Pay for calculation','VarSet','v = 44\nvalue = max(0,var(44)-1)','Time = [10,17] && Abs(var(42))=1')
        body+=ctl(1000,'Latch chosen route','VarSet','v = 42\nvalue = var(42)*2','Time = [10,17] && Abs(var(42))=1')
        body+=h(1000,'64+var(44)*5',21,fall=True)
        out+=s(1000,8740,42,body)
        body=spend(1010)+h(1010,'72+var(45)*15',10,fall=True,lift=True)
        body+=ctl(1010,'Calculated launch height','TargetVelSet','y = -7-var(45)*1.5','Time = 11 && MoveHit && NumTarget>0')
        out+=s(1010,8741,35,body)
        out+=s(1020,8742,36,move(1020,6.4,3,20)+h(1020,76,7,fall=True))
        out+=s(1030,8743,37,h(1030,60,9,low=True,fall=True)+move(1030,-3,14,25),kind='C')
    elif id=='leonardo':
        body=ctl(1000,'Remember battery','VarSet','v = 45\nvalue = var(44)')
        for t in [10,20]: body+=h(1000,26,t,velocity='-0.5',stun=24)
        body+=hit(1000,36,trigger='Time = 25 && var(45)>0',fall=True)
        body+=ctl(1000,'Battery spent','VarSet','v = 44\nvalue = max(0,var(44)-1)')
        out+=s(1000,8740,30,body)
        out+=s(1010,8741,38,leap(1010,2,-5.2,26)+h(1010,67,8,fall=True,lift=True)+ctl(1010,'Low evasion','NotHitBy','value = C,NA,SA\ntime = 1','Time = [3,9]'))
        body=ctl(1020,'Swipe trail','AfterImage','time = 20\nlength = 5\ntimegap = 2\nframegap = 2\ntrans = add')
        body+=ctl(1020,'Pass through','PlayerPush','value = 0','Time <= 18')
        body+=ctl(1020,'Measured swipe stride','VelSet','x = min(12,max(3,(P2Dist X+24)/14))','Time = 3')
        body+=ctl(1020,'Plant after swipe','VelSet','x = 0','Time = 17')
        body+=ctl(1020,'Face opponent after crossing','Turn','','Time = 17 && P2Dist X < 0')+h(1020,63,18)
        out+=s(1020,8742,29,body)
        out+=s(1030,8743,34,counter(1030),move='I')
    elif id=='cesar':
        out+=s(1000,8740,50,h(1000,82,24,stun=28))
        out+=s(1010,8741,46,h(1010,100,18,fall=True,lift=True))
        body=ctl(1020,'Remember rigor for support','VarSet','v = 45\nvalue = min(1,var(44))')
        body+=ctl(1020,'Pay for supported guard','VarSet','v = 44\nvalue = max(0,var(44)-1)')
        body+=move(1020,2.6,5,26)+ctl(1020,'Supported advance','DefenceMulSet','value = ifelse(var(45)>0,.35,.55)','Time = [5,28]')+h(1020,94,18,fall=True)
        out+=s(1020,8742,48,body)
        out+=s(1030,8743,44,spend(1030)+move(1030,1.6,2,7)+grab(1030,'90+var(45)*20'))

    # Supports now have different uses, rather than all charging the same bar.
    body=ctl(1040,'Support cooldown','VarSet',f'v = 48\nvalue = {p["cooldown"]}')
    if id in {'chan_kof','alejandro','armando','jaime'}:
        body+=gain(1040,24)
        if id in {'alejandro','armando'}: body+=ctl(1040,'Prepared mode','VarSet','v = 46\nvalue = 240','Time = 24')
    elif id=='felix':
        body+=spend(1040)+ctl(1040,'Diagnostic repair','LifeAdd','value = 40+var(45)*10\nkill = 0','Time = 30')
    elif id=='daniela':
        body+=gain(1040,26)+ctl(1040,'Approved documentation','PowerAdd','value = 180','Time = 26')
    elif id=='gameros':
        body+=ctl(1040,'Gym stance','VarSet','v = 46\nvalue = 300','Time = 24')
    elif id=='vladimir':
        body+=gain(1040,28)+ctl(1040,'Attendance energy','PowerAdd','value = 180','Time = 28')
    elif id=='leonardo':
        body+=ctl(1040,'Airplane dodge','NotHitBy','value = SCA,NA,SA,HA,NP,SP,HP\ntime = 1','Time = [3,16]')
        body+=move(1040,-4.5,3,14)+gain(1040,18,2)
    elif id=='cesar':
        body+=ctl(1040,'Pill recovery','LifeAdd','value = 65\nkill = 0','Time = 40')
        body+=ctl(1040,'Supported recovery','VarSet','v = 46\nvalue = 180','Time = 40')
    out+=s(1040,8744,54 if id=='cesar' else 42 if id!='leonardo' else 26,body,move='I',cost=p['cost'])

    if id in COUNTERS:
        body=ctl(1070,'Face attacker','Turn','','Time = 0 && P2Dist X < 0')
        body+=ctl(1070,'Counter protection','NotHitBy','value = SCA\ntime = 1','Time < 12')
        if id=='felix':
            body+=move(1070,2,2,7)+h(1070,98,12,low=True,fall=True,velocity='-2',stun=32)
            body+=ctl(1070,'Repair confirmed reboot','LifeAdd','value = 8+var(44)*4\nkill = 0','Time = 20 && MoveHit')
        elif id=='daniela':
            body+=move(1070,2.8,2,7)+grab(1070,90)
        else:
            body+=move(1070,-2.8,0,4)+move(1070,6.3,5,10)
            body+=h(1070,90,12,fall=True,lift=True)
        body+=gain(1070,18)
        out+=s(1070,8745,35,body)
    if id in {'daniela','vladimir','cesar'}:
        out+=state(1080,5000,move='H',kind='A')
        out+=ctl(1080,'Use victim animation','ChangeAnim','value = 5000')
        out+=ctl(1080,'Safe release','SelfState','value = 5050\nctrl = 0','Time >= 24')
        out+=state(1081,5050,move='H',kind='A')+ctl(1081,'Throw velocity','VelSet','x = -4\ny = -4')
        out+=ctl(1081,'Return victim control','SelfState','value = 5050\nctrl = 0')
    out+=s(750,240,28,h(750,85,8,fall=True))
    out+=state(3021,8705,move='I',kind='A')+ctl(3021,'Impact no push','PlayerPush','value = 0','1')+ctl(3021,'Impact cleanup','DestroySelf','','AnimTime = 0\ntrigger2 = RoundState != 2')
    return out


def passive(id,ctl):
    out=ctl(-2,'Reset temporary armor','DefenceMulSet','value = 1','!IsHelper')
    out+=ctl(-2,'New action resource latch','VarSet','v = 50\nvalue = 0','!IsHelper && Time = 0')
    eligible={
      'chan_kof':'StateNo = 1000 || StateNo = 210',
      'felix':'StateNo = 1000 || StateNo = 1030',
      'daniela':'StateNo = 1000',
      'gameros':'MoveType = A && StateNo < 3000',
      'vladimir':'StateNo = 1000 || StateNo = 3000',
    }.get(id)
    if eligible:
        trigger=f'!IsHelper && MoveHit && var(50)=0 && ({eligible})'
        out+=ctl(-2,'Confirmed identity resource','VarSet','v = 44\nvalue = min(3,var(44)+1)',trigger)
        out+=ctl(-2,'Latch identity gain','VarSet','v = 50\nvalue = 1',trigger)
    if id=='gameros': out+=ctl(-2,'Broken combo streak','VarSet','v = 44\nvalue = 0','!IsHelper && MoveType = H')
    if id=='gameros': out+=ctl(-2,'Gym attack strength','AttackMulSet','value = ifelse(var(46)>0,1.15,1)','!IsHelper')
    if id=='cesar':
        out+=ctl(-2,'Rigor after taking a hit','VarSet','v = 44\nvalue = min(3,var(44)+1)','!IsHelper && MoveType = H && Time = 0 && GetHitVar(damage)>0')
        out+=ctl(-2,'Recovery protection','DefenceMulSet','value = .8','!IsHelper && var(46)>0 && MoveType != A')
    if id in {'alejandro','armando'}:
        out+=ctl(-2,'Preparation expires','VarSet','v = 44\nvalue = 0','!IsHelper && var(46)=1')
    # Three small subject icons show the resource, with fixed screen positions.
    for i in range(1,4):
        out+=ctl(-2,'Identity resource indicator','Explod',f'anim = 8790\nID = {8890+i}\npostype = left\npos = ifelse(TeamSide=1,35,250)+{i*9},43\nscale = .18,.18\nbindtime = -1\nremovetime = 2\nsprpriority = 7\nownpal = 1',f'!IsHelper && RoundState=2 && var(44)>={i} && NumExplod({8890+i})=0')
    return out


def actions(id):
    """Each move gets its own pose order, timing and contact windows."""
    # Five independently choreographed specials, then a counter reply.
    sequences={
      'chan_kof':[(200,[0,1,2,3,2,0],5),(8701,list(range(6)),6),(240,[0,1,2,3,4,5],7),(440,[0,2,3,2,3,5],6),(200,[0,0,1,0,0,0],7)],
      'felix':[(200,[0,1,2,3,4,5],6),(120,[0,1,2,1,0,0],6),(440,[0,1,2,3,4,5],6),(440,[0,2,3,3,4,0],7),(200,[0,0,1,1,0,0],7)],
      'alejandro':[(200,[0,1,2,3,4,5],5),(410,[0,1,2,3,4,5],6),(200,[0,1,3,4,3,0],6),(440,[0,1,2,2,1,0],6),(200,[0,1,1,0,1,0],7)],
      'daniela':[(200,[0,2,3,2,3,0],6),(120,[0,1,2,1,0,0],6),(8701,[0,1,2,3,4,5],7),(200,[0,1,2,3,2,0],6),(200,[0,0,1,0,1,0],7)],
      'gameros':[(200,[0,2,3,2,3,0],5),(240,[0,1,2,3,4,5],7),(8701,[0,1,2,3,4,5],6),(440,[0,2,3,2,3,0],6),(410,[0,1,0,1,0,0],7)],
      'armando':[(200,[0,1,2,3,4,5],5),(8701,[0,1,2,3,4,5],7),(440,[0,1,2,2,1,0],6),(240,[0,2,3,2,3,0],6),(200,[0,1,1,0,1,0],7)],
      'vladimir':[(200,[0,1,2,3,2,0],6),(410,[0,1,2,3,4,5],6),(8701,[0,1,2,3,4,5],7),(440,[0,1,2,3,4,5],7),(200,[0,1,0,1,0,0],7)],
      'jaime':[(240,[0,1,2,3,4,5],7),(410,[0,1,2,3,4,5],6),(8701,[0,1,2,3,4,5],6),(440,[0,1,2,3,4,5],6),(200,[0,1,0,1,0,0],7)],
      'leonardo':[(240,[0,2,3,2,3,0],5),(240,[0,1,2,3,4,5],6),(8701,[0,1,2,3,4,5],5),(120,[0,1,2,1,0,0],6),(20,[0,1,2,3,4,5],5)],
      'cesar':[(200,[0,1,2,3,4,5],8),(410,[0,1,2,3,4,5],8),(8701,[0,1,2,3,4,5],8),(200,[0,1,2,3,2,0],8),(200,[0,0,1,1,0,0],9)],
    }
    out=''
    for k,(group,indices,ticks) in enumerate(sequences[id]+[(410,list(range(6)),6)]):
        custom={'chan_kof':1,'felix':1,'alejandro':4,'daniela':1,'gameros':4,'armando':4,'vladimir':0,'jaime':0,'leonardo':0,'cesar':0}
        if k==custom[id]:
            group=8760
            indices=[0,1,2,3,4,2] if id=='leonardo' else list(range(6))
        if k==5 and id in {'felix','daniela'}:
            group,indices=8760,[2,3,4,5,4,0]
        anim=8740+k
        low=group==440
        out+=f'\n[Begin Action {anim}]\nClsn2Default: 1\nClsn2[0] = -22,{"-65" if low else "-98"},22,0\n'
        for i in indices:
            if k!=4 and not (id in COUNTERS and [1000,1010,1020,1030,1040,1070][k]==COUNTERS[id]):
                box='-88,-32,88,0' if id=='vladimir' and k==3 else '8,-48,68,-8' if low else '8,-100,72,-18'
                if id=='cesar' and k==0: box='8,-85,104,-22'
                if id=='leonardo' and k==0: box='18,-100,105,-25'
                if id=='chan_kof' and k==1: box='0,-135,50,-35'
                out+=f'Clsn1: 1\nClsn1[0] = {box}\n'
            out+=f'{group},{i}, 0,0, {ticks}\n'
    out+='\n[Begin Action 8790]\n8703,0, 0,0, -1\n'
    if id=='armando':
        out+='\n[Begin Action 8750]\nClsn2Default: 1\nClsn2[0] = -18,-14,18,14\nClsn1Default: 1\nClsn1[0] = -60,-75,60,14\n'
        for i in range(6): out+=f'8703,{i}, 0,0, 3\n'
    finishers={
      'chan_kof':[(8701,i) for i in [0,2,3,4,2,3,4,5]],
      'felix':[(120,i) for i in [0,1,2]]+[(200,i) for i in [1,2,3]]+[(410,i) for i in [2,3,4]],
      'alejandro':[(200,i) for i in [0,2,3,2,3]]+[(410,i) for i in [1,2,3,4]],
      'daniela':[(8701,i) for i in [0,1,2,3,2,3,4,5]],
      'gameros':[(410,i) for i in [0,1,0]]+[(240,i) for i in [1,2,3,2,3,4]],
      'armando':[(8701,i) for i in [0,1,2,3,4,5,2,3,4,5]],
      'vladimir':[(200,i) for i in [0,1,2,3,2,3,4,5]],
      'jaime':[(240,i) for i in [0,1,2,3,4,1,2,3,4,5]],
      'leonardo':[(240,i) for i in [0,2,3,2,3,2,3,4,5]],
      'cesar':[(8701,i) for i in [0,1,2,3]]+[(410,i) for i in [0,1,2,3,4,5]],
    }
    out+='\n[Begin Action 8746]\nClsn2Default: 1\nClsn2[0] = -22,-98,22,0\n'
    for group,i in finishers[id]:
        out+='Clsn1: 1\nClsn1[0] = 8,-100,80,-12\n'
        out+=f'{group},{i}, 0,0, 7\n'
    return out


def maximum(id,state,ctl,hit,end,helper):
    n=4000
    out=state(n,8746,cost=2000)
    out+=ctl(n,'MAX2 freeze','SuperPause','time = 22\nmovetime = 22\nanim = -1\ndarken = 1\np2defmul = 1')
    out+=ctl(n,'Snapshot identity resource','VarSet','v = 45\nvalue = var(44)')
    out+=ctl(n,'MAX2 spends resource','VarSet','v = 44\nvalue = 0')
    def h(d,t,**kw): return hit(n,d,trigger=f'Time = {t}',supermove=True,**kw)
    def step(speed,start,stop):
        return ctl(n,'MAX2 step','VelSet',f'x = {speed}',f'Time = [{start},{stop}]')+ctl(n,'MAX2 brake','VelSet','x = 0',f'Time = {stop+1}')
    def jump(start,speed,up,land):
        return (ctl(n,'MAX2 leap','VelSet',f'x = {speed}\ny = {up}',f'Time = {start}')
          +ctl(n,'MAX2 airborne','StateTypeSet','statetype = A',f'Time = {start}')
          +ctl(n,'MAX2 gravity','VelAdd','y = .5',f'Time = [{start+1},{land-1}] && StateType = A')
          +ctl(n,'MAX2 land','PosSet','y = 0',f'Time = {land}\ntrigger2 = Time > {start} && Time < {land} && Vel Y>0 && Pos Y+Vel Y>=0')
          +ctl(n,'MAX2 land stop','VelSet','x = 0\ny = 0',f'Time = {land}\ntrigger2 = Time > {start} && Time < {land} && Vel Y>0 && Pos Y+Vel Y>=0')
          +ctl(n,'MAX2 grounded','StateTypeSet','statetype = S',f'Time = {land}\ntrigger2 = Time > {start} && Time < {land} && Pos Y>=0 && Vel Y>=0'))
    if id=='chan_kof':
        out+=step(2.2,3,16)
        for t in [14,28]: out+=h('65+var(45)*7',t,velocity='-0.4',stun=32)
        out+=h('100+var(45)*10',42,fall=True,lift=True)
        out+=ctl(n,'Crossfit floor shock','EnvShake','time = 16\nfreq = 80\nampl = -6','Time = 42')
    elif id=='felix':
        out+=ctl(n,'Full maintenance protection','DefenceMulSet','value = .4','Time = [3,34]')
        out+=step(2.5,4,16)+h(60,12,velocity='-0.5',stun=38)+h(150,34,fall=True,lift=True)
        out+=ctl(n,'Restored system','LifeAdd','value = 55+var(45)*10\nkill = 0','Time = 43 && MoveHit')
    elif id=='alejandro':
        out+=ctl(n,'Deploy afterimages','AfterImage','time = 45\nlength = 8\ntimegap = 2\nframegap = 2\ntrans = add','Time = 3')
        out+=ctl(n,'Deploy step','PosAdd','x = min(130,max(0,P2BodyDist X-20))','Time = 5')
        out+=h(70,8,velocity='-0.5',stun=34)
        out+=helper(n,1005,35,-55,'Time = 19')+helper(n,1005,35,-80,'Time = 29',identity=1006)
        out+=h('105+var(45)*12',40,fall=True,lift=True)
    elif id=='daniela':
        out+=ctl(n,'Call Victor for joint audit','VarSet','v = 47\nvalue = 1','Time = 8')
        out+=step(3.5,10,28)+h(65,16,velocity='-0.5',stun=28)+h('85+var(45)*10',32,fall=True)
    elif id=='gameros':
        out+=ctl(n,'Final Boss gym mode','VarSet','v = 46\nvalue = 480','Time = 4')
        out+=ctl(n,'Full combo streak','VarSet','v = 44\nvalue = 3','Time = 4')
        out+=ctl(n,'Final Boss appearance','PalFX','time = 36\nadd = 60,30,0\nmul = 256,220,180','Time = 4')
        out+=step(4.5,6,26)
        for t in [12,22,32]: out+=h(55,t,velocity='-0.5',stun=26)
        out+=h(70,42,fall=True,lift=True)
    elif id=='armando':
        out+=jump(3,2.4,-6,29)+h(65,12,velocity='-0.5',stun=34)+h(105,29,velocity='-0.5',stun=34)
        out+=step(3.2,33,43)+h('90+var(45)*12',44,fall=True,lift=True)
        out+=ctl(n,'Calibrated court impact','EnvShake','time = 12\nfreq = 80\nampl = -5','Time = 29')
    elif id=='vladimir':
        out+=step(3.5,3,12)
        out+=ctl(n,'Mandatory conference grab','HitDef','attr = S,HT\nhitflag = M-\npriority = 1,Miss\ndamage = 220+var(45)*15,0\npausetime = 0,0\nsparkno = -1\np2stateno = 8850\nfall = 1\ngetpower = 0,0','Time = 13')
        out+=ctl(n,'Hold for attendance','TargetBind','time = 1\npos = 35,-8','Time = [14,33] && NumTarget>0')
        out+=ctl(n,'Attendance penalty','TargetPowerAdd','value = -150-var(45)*50','Time = 24 && NumTarget>0')
        out+=ctl(n,'Release conference','TargetState','value = 8851','Time = 34 && NumTarget>0')
    elif id=='jaime':
        out+=jump(3,3.2,-6,28)+h(85,12,velocity='-0.5',stun=34)
        out+=ctl(n,'Next knight square','Turn','','Time = 30 && P2Dist X<0')
        out+=jump(31,2.4,-5.5,54)+h(80,39,velocity='-0.5',stun=34)+h('100+var(45)*10',55,fall=True,lift=True)
    elif id=='leonardo':
        out+=ctl(n,'Release afterimages','AfterImage','time = 42\nlength = 8\ntimegap = 2\nframegap = 2\ntrans = add','Time = 3')
        out+=step(5.8,4,23)
        for t in [7,14,21,28]: out+=h(38,t,velocity='-0.3',stun=26)
        out+=h('95+var(45)*12',38,fall=True,lift=True)
        out+=step(-3.5,42,49)
    elif id=='cesar':
        out+=ctl(n,'Final exam support','DefenceMulSet','value = .35','Time = [4,32]')
        out+=step(2.1,5,24)+h(85,18,velocity='-0.5',stun=38)+h('165+var(45)*22',40,fall=True,lift=True)
        out+=ctl(n,'Backend impact','EnvShake','time = 14\nfreq = 60\nampl = -6','Time = 40')
    out+=end(n,68 if id=='jaime' else 60)
    return out


def tune_basics(text,id):
    p=IDENTITIES[id]
    for key,val in [('walk.fwd',p['walk']),('walk.back',-p['walk']*.8),('run.fwd',f'{p["run"]},0'),('jump.neu',f'0,{p["jump"]}')]:
        text=re.sub(r'(?m)^'+re.escape(key)+r'\s*=.*',f'{key} = {val}',text)
    # Slow characters trade recovery and mobility for heavier normal contacts.
    damage={'chan_kof':(32,80),'felix':(30,74),'alejandro':(24,64),'daniela':(28,72),'gameros':(22,62),'armando':(29,72),'vladimir':(34,82),'jaime':(27,70),'leonardo':(20,58),'cesar':(38,94)}[id]
    for n,val in [(200,damage[0]),(210,damage[1])]:
        pattern=rf'(?ims)^\[Statedef {n}\].*?(?=^\[Statedef |\Z)'
        text=re.sub(pattern,lambda m:re.sub(r'(?m)^damage = .*',f'damage = {val},0',m.group(0)),text)
    # Generic AI walking must use the character's actual movement constant.
    return text


def normal_air(text,id):
    tempo=IDENTITIES[id]['tempo']
    # Recover original timings so a second build never compounds speed changes.
    from pathlib import Path
    reference=Path(__file__).resolve().parents[1]/'chars/chava/chava.air'
    original=reference.read_text(encoding='utf-8')
    for n in [200,201,210,211,230,240,600,610,630,640]:
        pattern=rf'(?ims)^\[Begin Action {n}\].*?(?=^\[Begin Action |\Z)'
        match=re.search(pattern,original)
        if not match: continue
        block=re.sub(r'(?m)^(\s*\d+,\d+,\s*[-\d]+,[-\d]+,\s*)(\d+)',lambda m:m[1]+str(max(2,round(int(m[2])*tempo))),match[0])
        text=re.sub(pattern,lambda _:block,text)
    return text


def sprites(root,id):
    """Extract entire generated silhouettes; never normalize each pose's height."""
    import cv2
    import numpy as np
    from PIL import Image
    names=list(IDENTITIES)
    index=names.index(id)
    path=root/'data/teacher-identity-art'/('master-a.png' if index<5 else 'master-b.png')
    rgba=np.array(Image.open(path).convert('RGBA'))
    _,labels,stats,centers=cv2.connectedComponentsWithStats((rgba[:,:,3]>100).astype(np.uint8),8)
    figures=[i for i in range(1,len(stats)) if stats[i,4]>700]
    assert len(figures)==30,(path,len(figures))
    figures.sort(key=lambda i:centers[i,1])
    members=sorted(figures[(index%5)*6:(index%5+1)*6],key=lambda i:centers[i,0])
    scales={'chan_kof':.50,'felix':.53,'alejandro':.52,'daniela':.53,'gameros':.72,
            'armando':.50,'vladimir':.50,'jaime':.53,'leonardo':.55,'cesar':.53}
    scale=scales[id]
    frames={}
    art=root/'chars'/id/'art/identity-v2'
    art.mkdir(parents=True,exist_ok=True)
    preview=Image.new('RGB',(1080,160),(25,34,43))
    for col,component in enumerate(members):
        x,y,w,h,_=stats[component]
        mask=cv2.dilate((labels==component).astype(np.uint8),np.ones((3,3),np.uint8),iterations=1)
        pixels=rgba.copy(); pixels[:,:,3]*=mask
        body=Image.fromarray(pixels).crop((x-2,max(0,y-2),x+w+2,min(rgba.shape[0],y+h+2)))
        body=body.resize((round(body.width*scale),round(body.height*scale)),Image.Resampling.NEAREST)
        axis_x=round(((col+.5)*rgba.shape[1]/6-x+2)*scale)
        axis_y=body.height
        frames[8760,col]=(body,axis_x,axis_y)
        body.save(art/f'pose-{col}.png')
        preview.paste(body,(col*180+80-axis_x,150-axis_y),body)
    preview.save(art/'preview.png')
    return frames
