; Chava: four attack buttons, one optional shortcut for the super.
[Remap]
x = x
y = y
z = z
a = a
b = b
c = c
s = s

[Defaults]
command.time = 15
command.buffer.time = 3

[Command]
name = "IA"
command = ~D, DF, F, x+y
time = 24

[Command]
name = "IA"
command = z
time = 1

[Command]
name = "FF"
command = F, F
time = 12

[Command]
name = "BB"
command = B, B
time = 12

[Command]
name = "recovery"
command = x+y
time = 1

[Command]
name = "x"
command = x
time = 1

[Command]
name = "y"
command = y
time = 1

[Command]
name = "a"
command = a
time = 1

[Command]
name = "b"
command = b
time = 1

[Command]
name = "c"
command = c
time = 1

[Command]
name = "s"
command = s
time = 1

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
name = "holdup"
command = /$U
time = 1
buffer.time = 1

[Command]
name = "holddown"
command = /$D
time = 1
buffer.time = 1

[Statedef -1]

[State -1, Call IA]
type = ChangeState
value = 3000
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = Power >= 1000
triggerall = NumHelper(3010) = 0
triggerall = StateType != A
triggerall = Ctrl
trigger1 = command = "IA"
trigger1 = AILevel = 0
trigger2 = AILevel > 0
trigger2 = P2BodyDist X > 70
trigger2 = Random < 7 * AILevel

[State -1, Run]
type = ChangeState
value = 100
triggerall = !IsHelper
triggerall = StateType = S
triggerall = Ctrl
trigger1 = command = "FF"
trigger1 = AILevel = 0

[State -1, Back hop]
type = ChangeState
value = 105
triggerall = !IsHelper
triggerall = StateType = S
triggerall = Ctrl
trigger1 = command = "BB"
trigger1 = AILevel = 0

[State -1, Taunt]
type = ChangeState
value = 195
triggerall = !IsHelper
triggerall = AILevel = 0
triggerall = StateType = S
triggerall = Ctrl
trigger1 = command = "s"


[State -1, Attack 600]
type = ChangeState
value = 600
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = command = "x"
triggerall = StateType = A

trigger1 = Ctrl


[State -1, Attack 610]
type = ChangeState
value = 610
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = command = "y"
triggerall = StateType = A

trigger1 = Ctrl

trigger2 = (StateNo = 600 || StateNo = 630)
trigger2 = MoveHit
trigger2 = AnimElemTime(5) >= 0


[State -1, Attack 630]
type = ChangeState
value = 630
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = command = "a"
triggerall = StateType = A

trigger1 = Ctrl


[State -1, Attack 640]
type = ChangeState
value = 640
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = command = "b"
triggerall = StateType = A

trigger1 = Ctrl

trigger2 = (StateNo = 600 || StateNo = 630)
trigger2 = MoveHit
trigger2 = AnimElemTime(5) >= 0


[State -1, Attack 400]
type = ChangeState
value = 400
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = command = "x"
triggerall = StateType = C

trigger1 = Ctrl


[State -1, Attack 410]
type = ChangeState
value = 410
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = command = "y"
triggerall = StateType = C

trigger1 = Ctrl

trigger2 = (StateNo = 400 || StateNo = 430)
trigger2 = MoveHit
trigger2 = AnimElemTime(5) >= 0


[State -1, Attack 430]
type = ChangeState
value = 430
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = command = "a"
triggerall = StateType = C

trigger1 = Ctrl


[State -1, Attack 440]
type = ChangeState
value = 440
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = command = "b"
triggerall = StateType = C

trigger1 = Ctrl

trigger2 = (StateNo = 400 || StateNo = 430)
trigger2 = MoveHit
trigger2 = AnimElemTime(5) >= 0


[State -1, Attack 200]
type = ChangeState
value = 200
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = command = "x"
triggerall = StateType = S
triggerall = command != "holddown"
trigger1 = Ctrl


[State -1, Attack 210]
type = ChangeState
value = 210
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = command = "y"
triggerall = StateType = S
triggerall = command != "holddown"
trigger1 = Ctrl

trigger2 = (StateNo = 200 || StateNo = 230)
trigger2 = MoveHit
trigger2 = AnimElemTime(5) >= 0


[State -1, Attack 230]
type = ChangeState
value = 230
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = command = "a"
triggerall = StateType = S
triggerall = command != "holddown"
trigger1 = Ctrl


[State -1, Attack 240]
type = ChangeState
value = 240
triggerall = !IsHelper
triggerall = RoundState = 2
triggerall = AILevel = 0
triggerall = command = "b"
triggerall = StateType = S
triggerall = command != "holddown"
trigger1 = Ctrl

trigger2 = (StateNo = 200 || StateNo = 230)
trigger2 = MoveHit
trigger2 = AnimElemTime(5) >= 0


; Small, bounded AI for CPU matches. Human controls are unaffected.
[State -1, AI defend]
type = ChangeState
triggerall = !IsHelper
triggerall = AILevel > 0
triggerall = RoundState = 2
triggerall = Ctrl
triggerall = StateType != A
trigger1 = P2MoveType = A
trigger1 = P2BodyDist X < 95
trigger1 = Random < 30 * AILevel
value = 120

[State -1, AI attack]
type = ChangeState
triggerall = !IsHelper
triggerall = AILevel > 0
triggerall = RoundState = 2
triggerall = Ctrl
triggerall = StateType = S
triggerall = P2BodyDist X < 56
trigger1 = Random < 18 * AILevel
value = ifelse(Random < 400,200,ifelse(Random < 500,210,240))

[State -1, AI low]
type = ChangeState
triggerall = !IsHelper
triggerall = AILevel > 0
triggerall = RoundState = 2
triggerall = Ctrl
triggerall = StateType = C
trigger1 = P2BodyDist X < 55
value = 440

[State -1, AI air]
type = ChangeState
triggerall = !IsHelper
triggerall = AILevel > 0
triggerall = RoundState = 2
triggerall = Ctrl
triggerall = StateType = A
trigger1 = P2BodyDist X < 60
value = 640

[State -1, AI walk]
type = ChangeState
triggerall = !IsHelper
triggerall = AILevel > 0
triggerall = RoundState = 2
triggerall = Ctrl
triggerall = StateType = S
triggerall = StateNo != 20
trigger1 = P2BodyDist X > 52
value = 20

[State -1, AI advance]
type = VelSet
triggerall = !IsHelper
triggerall = AILevel > 0
triggerall = RoundState = 2
trigger1 = StateNo = 20
x = ifelse(P2BodyDist X > 50,1.55,0)
