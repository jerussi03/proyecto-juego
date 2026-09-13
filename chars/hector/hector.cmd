; KOF notation: A=x, B=a, C=y, D=b. Xbox X/A/Y/B.
[Remap]
x=x
y=y
z=z
a=a
b=b
c=c
s=s

[Defaults]
command.time=22
command.buffer.time=4

[Command]
name = "x"
command = x
time = 1
buffer.time = 4

[Command]
name = "y"
command = y
time = 1
buffer.time = 4

[Command]
name = "a"
command = a
time = 1
buffer.time = 4

[Command]
name = "b"
command = b
time = 1
buffer.time = 4

[Command]
name = "c"
command = c
time = 1
buffer.time = 4

[Command]
name = "z"
command = z
time = 1
buffer.time = 4

[Command]
name = "s"
command = s
time = 1
buffer.time = 4

[Command]
name = "holdfwd"
command = /$F
time = 1
buffer.time = 1

[Command]
name = "holdback"
command = /$B
time = 1
buffer.time = 1

[Command]
name = "holddown"
command = /$D
time = 1
buffer.time = 1

[Command]
name = "holdup"
command = /$U
time = 1
buffer.time = 1

[Command]
name = "FF"
command = F,F
time = 12
buffer.time = 4

[Command]
name = "BB"
command = B,B
time = 12
buffer.time = 4

[Command]
name = "roll"
command = x+a
time = 1
buffer.time = 4

[Command]
name = "roll"
command = c
time = 1
buffer.time = 4

[Command]
name = "max"
command = a+y
time = 1
buffer.time = 4

[Command]
name = "max"
command = z
time = 1
buffer.time = 4

[Command]
name = "blowback"
command = y+b
time = 1
buffer.time = 4

[Command]
name = "recovery"
command = x+a
time = 1
buffer.time = 4

[Command]
name = "qcf_x"
command = ~D, DF, F, x
time = 24
buffer.time = 4

[Command]
name = "qcf_y"
command = ~D, DF, F, y
time = 24
buffer.time = 4

[Command]
name = "qcf_a"
command = ~D, DF, F, a
time = 24
buffer.time = 4

[Command]
name = "qcf_b"
command = ~D, DF, F, b
time = 24
buffer.time = 4

[Command]
name = "qcb_x"
command = ~D, DB, B, x
time = 24
buffer.time = 4

[Command]
name = "qcb_y"
command = ~D, DB, B, y
time = 24
buffer.time = 4

[Command]
name = "qcb_a"
command = ~D, DB, B, a
time = 24
buffer.time = 4

[Command]
name = "qcb_b"
command = ~D, DB, B, b
time = 24
buffer.time = 4

[Command]
name = "dp_x"
command = ~F, D, DF, x
time = 24
buffer.time = 4

[Command]
name = "dp_y"
command = ~F, D, DF, y
time = 24
buffer.time = 4

[Command]
name = "dp_a"
command = ~F, D, DF, a
time = 24
buffer.time = 4

[Command]
name = "dp_b"
command = ~F, D, DF, b
time = 24
buffer.time = 4

[Command]
name = "hcf_x"
command = ~B, DB, D, DF, F, x
time = 24
buffer.time = 4

[Command]
name = "hcf_y"
command = ~B, DB, D, DF, F, y
time = 24
buffer.time = 4

[Command]
name = "hcf_a"
command = ~B, DB, D, DF, F, a
time = 24
buffer.time = 4

[Command]
name = "hcf_b"
command = ~B, DB, D, DF, F, b
time = 24
buffer.time = 4

[Command]
name = "hcb_x"
command = ~F, DF, D, DB, B, x
time = 24
buffer.time = 4

[Command]
name = "hcb_y"
command = ~F, DF, D, DB, B, y
time = 24
buffer.time = 4

[Command]
name = "hcb_a"
command = ~F, DF, D, DB, B, a
time = 24
buffer.time = 4

[Command]
name = "hcb_b"
command = ~F, DF, D, DB, B, b
time = 24
buffer.time = 4

[Command]
name = "dqcf_x"
command = ~D, DF, F, D, DF, F, x
time = 36
buffer.time = 4

[Command]
name = "dqcf_y"
command = ~D, DF, F, D, DF, F, y
time = 36
buffer.time = 4

[Command]
name = "dqcf_a"
command = ~D, DF, F, D, DF, F, a
time = 36
buffer.time = 4

[Command]
name = "dqcf_b"
command = ~D, DF, F, D, DF, F, b
time = 36
buffer.time = 4

[Command]
name = "dqcb_x"
command = ~D, DB, B, D, DB, B, x
time = 36
buffer.time = 4

[Command]
name = "dqcb_y"
command = ~D, DB, B, D, DB, B, y
time = 36
buffer.time = 4

[Command]
name = "dqcb_a"
command = ~D, DB, B, D, DB, B, a
time = 36
buffer.time = 4

[Command]
name = "dqcb_b"
command = ~D, DB, B, D, DB, B, b
time = 36
buffer.time = 4

[Command]
name = "qcfhcb_x"
command = ~D, DF, F, DF, D, DB, B, x
time = 36
buffer.time = 4

[Command]
name = "qcfhcb_y"
command = ~D, DF, F, DF, D, DB, B, y
time = 36
buffer.time = 4

[Command]
name = "qcfhcb_a"
command = ~D, DF, F, DF, D, DB, B, a
time = 36
buffer.time = 4

[Command]
name = "qcfhcb_b"
command = ~D, DF, F, DF, D, DB, B, b
time = 36
buffer.time = 4

[Command]
name = "max2"
command = ~D, DB, B, D, DB, B, x+y
time = 40
buffer.time = 4

[Statedef -1]

[State -1, Guard cancel roll]
type = ChangeState
value = ifelse(command = "holdback",923,922)
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = StateType != A
triggerall = Power >= 1000
trigger1 = command = "roll"
trigger1 = StateNo = [150,153]

[State -1, Emergency evasion AB or RT]
type = ChangeState
value = ifelse(command = "holdback",921,920)
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = StateType != A
triggerall = Ctrl
trigger1 = command = "roll"

[State -1, MAX BC or RB]
type = ChangeState
value = 900
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = StateType != A
triggerall = var(40) = 0
triggerall = command = "max"
trigger1 = Ctrl
trigger1 = Power >= 1000
trigger2 = (StateNo = [200,240]) || (StateNo = [400,440])
trigger2 = MoveContact
trigger2 = Power >= 2000

[State -1, MAX2]
type = ChangeState
value = 4000
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = StateType != A
triggerall = Power >= 2000
triggerall = var(40) > 0
triggerall = command = "max2"
triggerall = NumHelper(4010) = 0
trigger1 = Ctrl
trigger2 = (StateNo = [200,240]) || (StateNo = [400,440])
trigger2 = MoveContact
trigger3 = (StateNo = [1000,1030])
trigger3 = MoveContact

[State -1, Double quarter circle super]
type = ChangeState
value = 3200
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = StateType != A
triggerall = Power >= 1000
triggerall = NumHelper(3010) = 0
triggerall = command = "dqcf_x" || command = "dqcf_y"
trigger1 = Ctrl
trigger2 = (StateNo = [200,240]) || (StateNo = [400,440])
trigger2 = MoveContact
trigger3 = (StateNo = [1000,1030])
trigger3 = MoveContact
trigger3 = var(40) > 0

[State -1, Rush super]
type = ChangeState
value = 3500
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = StateType != A
triggerall = Power >= 1000
triggerall = command = "qcfhcb_x" || command = "qcfhcb_y"
trigger1 = Ctrl
trigger2 = (StateNo = [200,240]) || (StateNo = [400,440])
trigger2 = MoveContact
trigger3 = (StateNo = [1000,1030])
trigger3 = MoveContact
trigger3 = var(40) > 0

[State -1, DDoS super]
type = ChangeState
value = 3000
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = StateType != A
triggerall = Power >= 1000
triggerall = NumHelper(3015) = 0
triggerall = command = "dqcf_a" || command = "dqcf_b"
trigger1 = Ctrl
trigger2 = (StateNo = [200,240]) || (StateNo = [400,440])
trigger2 = MoveContact

[State -1, FPV super]
type = ChangeState
value = 3300
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = StateType != A
triggerall = Power >= 1000
triggerall = NumHelper(3030) = 0
triggerall = command = "dqcb_a" || command = "dqcb_b"
trigger1 = Ctrl
trigger2 = (StateNo = [200,240]) || (StateNo = [400,440])
trigger2 = MoveContact

[State -1, Shutdown finisher]
type = ChangeState
value = 4100
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = StateType != A
triggerall = Ctrl
triggerall = Power >= 1000
triggerall = (EnemyNear, Life) <= 120
trigger1 = command = "hcb_y"

[State -1, Firewall parry]
type = ChangeState
value = 700
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = StateType != A
triggerall = Ctrl
trigger1 = command = "qcb_a" || command = "qcb_b"

[State -1, Sin conexion]
type = ChangeState
value = 3100
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = StateType != A
triggerall = Ctrl
triggerall = Power >= 1000
triggerall = NumHelper(7015) = 0
trigger1 = command = "hcf_x" || command = "hcf_y"

[State -1, Handshake throw]
type = ChangeState
value = 800
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = StateType != A
triggerall = Ctrl
triggerall = P2BodyDist X < 35
triggerall = P2BodyDist X >= 0
triggerall = P2StateType != A
triggerall = P2MoveType != H
trigger1 = command = "hcb_x"

[State -1, Motion special 1010]
type = ChangeState
value = 1010
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = StateType != A
triggerall = command = "dp_x" || command = "dp_y"
trigger1 = Ctrl
trigger2 = (StateNo = [200,240]) || (StateNo = [400,440])
trigger2 = MoveContact
trigger3 = (StateNo = [1000,1030])
trigger3 = StateNo != 1010
trigger3 = MoveContact || (StateNo = 1000 && var(43) > 0)
trigger3 = var(40) >= 90

[State -1, Motion special 1030]
type = ChangeState
value = 1030
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = StateType != A
triggerall = command = "hcf_a" || command = "hcf_b"
trigger1 = Ctrl
trigger2 = (StateNo = [200,240]) || (StateNo = [400,440])
trigger2 = MoveContact
trigger3 = (StateNo = [1000,1030])
trigger3 = StateNo != 1030
trigger3 = MoveContact || (StateNo = 1000 && var(43) > 0)
trigger3 = var(40) >= 90

[State -1, Motion special 1020]
type = ChangeState
value = 1020
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = StateType != A
triggerall = command = "qcb_x" || command = "qcb_y"
trigger1 = Ctrl
trigger2 = (StateNo = [200,240]) || (StateNo = [400,440])
trigger2 = MoveContact
trigger3 = (StateNo = [1000,1030])
trigger3 = StateNo != 1020
trigger3 = MoveContact || (StateNo = 1000 && var(43) > 0)
trigger3 = var(40) >= 90

[State -1, Motion special 1000]
type = ChangeState
value = 1000
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = StateType != A
triggerall = command = "qcf_x" || command = "qcf_y"
triggerall = NumHelper(1005) = 0
trigger1 = Ctrl
trigger2 = (StateNo = [200,240]) || (StateNo = [400,440])
trigger2 = MoveContact
trigger3 = (StateNo = [1000,1030])
trigger3 = StateNo != 1000
trigger3 = MoveContact || (StateNo = 1000 && var(43) > 0)
trigger3 = var(40) >= 90

[State -1, CD blowback]
type = ChangeState
value = 750
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = StateType != A
triggerall = Ctrl
trigger1 = command = "blowback"

[State -1, Normal 600]
type = ChangeState
value = 600
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = command = "x"
triggerall = StateType = A
trigger1 = Ctrl

[State -1, Normal 630]
type = ChangeState
value = 630
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = command = "a"
triggerall = StateType = A
trigger1 = Ctrl

[State -1, Normal 610]
type = ChangeState
value = 610
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = command = "y"
triggerall = StateType = A
trigger1 = Ctrl
trigger2 = StateNo = 600 || StateNo = 630
trigger2 = MoveHit
trigger2 = AnimElemTime(5) >= 0

[State -1, Normal 640]
type = ChangeState
value = 640
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = command = "b"
triggerall = StateType = A
trigger1 = Ctrl
trigger2 = StateNo = 600 || StateNo = 630
trigger2 = MoveHit
trigger2 = AnimElemTime(5) >= 0

[State -1, Normal 400]
type = ChangeState
value = 400
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = command = "x"
triggerall = StateType != A
triggerall = command = "holddown"
trigger1 = Ctrl

[State -1, Normal 430]
type = ChangeState
value = 430
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = command = "a"
triggerall = StateType != A
triggerall = command = "holddown"
trigger1 = Ctrl

[State -1, Normal 410]
type = ChangeState
value = 410
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = command = "y"
triggerall = StateType != A
triggerall = command = "holddown"
trigger1 = Ctrl
trigger2 = StateNo = 400 || StateNo = 430
trigger2 = MoveHit
trigger2 = AnimElemTime(5) >= 0

[State -1, Normal 440]
type = ChangeState
value = 440
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = command = "b"
triggerall = StateType != A
triggerall = command = "holddown"
trigger1 = Ctrl
trigger2 = StateNo = 400 || StateNo = 430
trigger2 = MoveHit
trigger2 = AnimElemTime(5) >= 0

[State -1, Normal 200]
type = ChangeState
value = 200
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = command = "x"
triggerall = StateType = S
triggerall = command != "holddown"
trigger1 = Ctrl

[State -1, Normal 230]
type = ChangeState
value = 230
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = command = "a"
triggerall = StateType = S
triggerall = command != "holddown"
trigger1 = Ctrl

[State -1, Normal 210]
type = ChangeState
value = 210
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = command = "y"
triggerall = StateType = S
triggerall = command != "holddown"
trigger1 = Ctrl
trigger2 = StateNo = 200 || StateNo = 230
trigger2 = MoveHit
trigger2 = AnimElemTime(5) >= 0

[State -1, Normal 240]
type = ChangeState
value = 240
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = command = "b"
triggerall = StateType = S
triggerall = command != "holddown"
trigger1 = Ctrl
trigger2 = StateNo = 200 || StateNo = 230
trigger2 = MoveHit
trigger2 = AnimElemTime(5) >= 0

[State -1, Run]
type = ChangeState
value = 100
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = StateType != A
triggerall = Ctrl
trigger1 = command = "FF"

[State -1, Backstep]
type = ChangeState
value = 105
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = StateType != A
triggerall = Ctrl
trigger1 = command = "BB"

[State -1, Taunt]
type = ChangeState
value = 195
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = StateType != A
triggerall = Ctrl
trigger1 = command = "s"
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
trigger1 = AILevel > 0 && Power >= 1000 && NumHelper(3015) = 0 && P2BodyDist X > 90 && Random < 16
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

[State -1, CPU roll]
type = ChangeState
value = 920
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel > 0
triggerall = Ctrl
triggerall = StateType != A
trigger1 = P2MoveType = A
trigger1 = P2BodyDist X < 100
trigger1 = Random < 8 * AILevel
