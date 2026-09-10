[Remap]
x=x
y=y
z=z
a=a
b=b
c=c
s=s
[Defaults]
command.time=20
command.buffer.time=3

[Command]
name="ultimate"
command=~D, DF, F, D, DF, F, z
time=40

[Command]
name="ultimate"
command=y+z
time=1

[Command]
name="super"
command=x+y
time=1

[Command]
name="throw"
command=a+b
time=1

[Command]
name="FF"
command=F,F
time=12

[Command]
name="BB"
command=B,B
time=12

[Command]
name="recovery"
command=x+y
time=1

[Command]
name="backtap"
command=B
time=1

[Command]
name="x"
command=x
time=1

[Command]
name="y"
command=y
time=1

[Command]
name="z"
command=z
time=1

[Command]
name="a"
command=a
time=1

[Command]
name="b"
command=b
time=1

[Command]
name="c"
command=c
time=1

[Command]
name="s"
command=s
time=1

[Command]
name="holdfwd"
command=/$F
time=1

[Command]
name="holdback"
command=/$B
time=1

[Command]
name="holddown"
command=/$D
time=1

[Command]
name="holdup"
command=/$U
time=1

[Statedef -1]

[State -1, Finisher]
type=ChangeState
triggerall = Ctrl
triggerall = StateType != A
trigger1 = command = "z" && command = "holdback" && Power >= 1000 && (EnemyNear, Life) <= 120
value=4100

[State -1, Denial of service]
type=ChangeState
triggerall = Ctrl
triggerall = StateType != A
trigger1 = command = "ultimate" && Power >= 3000 && NumHelper(4010) = 0
value=4000

[State -1, CTRL ALT SUPR]
type=ChangeState
triggerall = Ctrl
triggerall = StateType != A
trigger1 = command = "super" && Power >= 1500
value=3500

[State -1, Handshake]
type=ChangeState
triggerall = Ctrl
triggerall = StateType != A
trigger1 = command = "throw" && P2BodyDist X < 40
value=800

[State -1, Sin conexion]
type=ChangeState
triggerall = Ctrl
triggerall = StateType != A
trigger1 = command = "z" && command = "holddown" && Power >= 750 && NumHelper(7015) = 0
value=3100

[State -1, Modo FPV]
type=ChangeState
triggerall = Ctrl
triggerall = StateType != A
trigger1 = command = "z" && command = "holdfwd" && Power >= 750 && NumHelper(3030) = 0
value=3300

[State -1, Drone Deploy]
type=ChangeState
triggerall = Ctrl
triggerall = StateType != A
trigger1 = command = "z" && Power >= 1000 && NumHelper(3010) = 0
value=3200

[State -1, DDoS]
type=ChangeState
triggerall = Ctrl
triggerall = StateType != A
trigger1 = command = "b" && Power >= 500 && NumHelper(3015) = 0
value=3000

[State -1, Packet Loss]
type=ChangeState
triggerall = Ctrl
triggerall = StateType != A
trigger1 = command = "c" && command = "holddown"
value=720

[State -1, Parry]
type=ChangeState
triggerall = Ctrl
triggerall = StateType != A
trigger1 = command = "c" || (command = "backtap" && P2BodyDist X < 100 && (EnemyNear, MoveType = A))
value=700

[State -1, Ping]
type=ChangeState
triggerall = Ctrl
triggerall = StateType != A
trigger1 = command = "x"
value=200

[State -1, RJ45]
type=ChangeState
triggerall = Ctrl
triggerall = StateType != A
trigger1 = command = "y"
value=210

[State -1, Capa Fisica]
type=ChangeState
triggerall = Ctrl
triggerall = StateType != A
trigger1 = command = "a" && command = "holddown"
value=430

[State -1, Packet Kick]
type=ChangeState
triggerall = Ctrl
triggerall = StateType != A
trigger1 = command = "a"
value=230

[State -1, Air punch]
type=ChangeState
triggerall = Ctrl
trigger1 = command = "x" && StateType = A
value=600

[State -1, Air kick]
type=ChangeState
triggerall = Ctrl
trigger1 = command = "a" && StateType = A
value=630

[State -1, Run]
type=ChangeState
triggerall = Ctrl
triggerall = StateType != A
trigger1 = command = "FF"
value=100

[State -1, Backstep]
type=ChangeState
triggerall = Ctrl
triggerall = StateType != A
trigger1 = command = "BB"
value=105

[State -1, Dato curioso]
type=ChangeState
triggerall = Ctrl
triggerall = StateType != A
trigger1 = command = "s"
value=195

[State -1, CPU]
type=ChangeState
triggerall = Ctrl
triggerall = StateType != A
trigger1 = AILevel > 0 && Power >= 3000 && Random < 6 && NumHelper(4010) = 0
value=4000

[State -1, CPU]
type=ChangeState
triggerall = Ctrl
triggerall = StateType != A
trigger1 = AILevel > 0 && Power >= 1000 && NumHelper(3010) = 0 && Random < 8
value=3200

[State -1, CPU]
type=ChangeState
triggerall = Ctrl
triggerall = StateType != A
trigger1 = AILevel > 0 && Power >= 500 && NumHelper(3015) = 0 && P2BodyDist X > 90 && Random < 16
value=3000

[State -1, CPU]
type=ChangeState
triggerall = Ctrl
triggerall = StateType != A
trigger1 = AILevel > 0 && (EnemyNear, MoveType = A) && P2BodyDist X < 75 && Random < 60
value=700

[State -1, CPU]
type=ChangeState
triggerall = Ctrl
triggerall = StateType != A
trigger1 = AILevel > 0 && P2BodyDist X < 90 && Random < 22
value=210

[State -1, CPU]
type=ChangeState
triggerall = Ctrl
triggerall = StateType != A
trigger1 = AILevel > 0 && P2BodyDist X < 50 && Random < 60
value=200

[State -1, CPU]
type=ChangeState
triggerall = Ctrl
triggerall = StateType != A
trigger1 = AILevel > 0 && P2BodyDist X < 65 && Random < 25
value=230
