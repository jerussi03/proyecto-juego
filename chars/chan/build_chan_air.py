from pathlib import Path

ROOT = Path(__file__).parent
OUTPUT = ROOT / "chan.air"

IDLE_FRAMES = 192
IDLE_TICK = 2

WALK_FRAMES = 31
WALK_TICK = 3

PUNCH_FRAMES = 31
PUNCH_TICK = 1
# The fist is extended forward between these animation elements.
PUNCH_ACTIVE_START = 8
PUNCH_ACTIVE_END = 26
PUNCH_CLSN1 = "16, -85, 52, -28"

MONGO_FRAMES = 55
MONGO_TICK = 1
MONGO_ACTIVE_START = 8
MONGO_ACTIVE_END = 37
MONGO_CLSN1 = "20, -100, 75, -25"

KICK_FRAMES = 31
KICK_TICK = 1
# The leg/foot is extended forward between these animation elements.
KICK_ACTIVE_START = 11
KICK_ACTIVE_END = 20
KICK_CLSN1 = "18, -80, 42, -25"

KICK_STRONG_FRAMES = 53
KICK_STRONG_TICK = 1
# The foot is extended far forward between these animation elements.
KICK_STRONG_ACTIVE_START = 15
KICK_STRONG_ACTIVE_END = 33
KICK_STRONG_CLSN1 = "20, -85, 78, -40"

HIT_FRAMES = 20
HIT_TICK = 1
# Get-hit (receiving damage) animations. The common states play 5000/5001/5002
# for the standing shake and 5005/5006/5007 for the knocked back, all using
# the same "dparada" sprites.
HIT_ACTIONS = [5000, 5001, 5002, 5005, 5006, 5007]

JUMP_START_FRAMES = 13
JUMP_START_TICK = 1
JUMP_AIR_FRAMES = 6
JUMP_AIR_TICK = 2
JUMP_LAND_FRAMES = 8
JUMP_LAND_TICK = 2

CROUCH_DOWN_FRAMES = 11
CROUCH_DOWN_TICK = 1
CROUCH_IDLE_FRAMES = 30
CROUCH_IDLE_TICK = 2
CROUCH_WALK_FRAMES = 25
CROUCH_WALK_TICK = 2

CLSN = [
    "Clsn2Default: 2",
    "Clsn2[0] = -20, -100, 20, -50",
    "Clsn2[1] = -22, -50, 22, 0",
]


def clsn():
    return [f"    {line}" for line in CLSN]


def emit_attack(lines, action, group, frames, tick, active_start, active_end,
                clsn1_box):
    # In MUGEN an explicit "Clsn1:" line only applies to the very next frame
    # element (after that the parser falls back to Clsn1Default), so the
    # hitbox must be repeated before every active element.
    lines.append(f"[Begin Action {action}]")
    lines.extend(clsn())
    lines.append("    Clsn1Default: 0")
    for i in range(frames):
        if active_start <= i <= active_end:
            lines.append("    Clsn1: 1")
            lines.append(f"    Clsn1[0] = {clsn1_box}")
        lines.append(f"{group},{i}, 0,0, {tick}")
    lines.append("")


def emit_hurt(lines, action, group, frames, tick):
    # Defensive animation (get-hit): hurtbox only, no attack hitbox.
    lines.append(f"[Begin Action {action}]")
    lines.extend(clsn())
    for i in range(frames):
        lines.append(f"{group},{i}, 0,0, {tick}")
    lines.append("")


lines = []
lines.append("; Chan animations.")
lines.append("; 0 = idle, 20 = walk fwd, 21 = walk back.")
lines.append("")

# Idle
lines.append("[Begin Action 0]")
lines.extend(clsn())
for i in range(IDLE_FRAMES):
    lines.append(f"0,{i}, 0,0, {IDLE_TICK}")
lines.append("")

# Walk forward
lines.append("[Begin Action 20]")
lines.extend(clsn())
for i in range(WALK_FRAMES - 1):
    lines.append(f"20,{i}, 0,0, {WALK_TICK}")
lines.append(f"20,{WALK_FRAMES - 1}, 0,0, 6")
lines.append("")

# Walk backward
lines.append("[Begin Action 21]")
lines.extend(clsn())
for i in range(WALK_FRAMES - 1, 0, -1):
    lines.append(f"20,{i}, 0,0, 4")
lines.append("20,0, 0,0, 4")
lines.append("")

# Standing light punch (state 200). The hitbox (Clsn1) is only active while
# the fist is extended forward.
emit_attack(lines, 200, 200, PUNCH_FRAMES, PUNCH_TICK, PUNCH_ACTIVE_START,
            PUNCH_ACTIVE_END, PUNCH_CLSN1)

# Mongo punch: heavy overhead strike. Played by the strong punch state (210)
# and also available as action 220 (same sprites).
for action in (210, 220):
    emit_attack(lines, action, 220, MONGO_FRAMES, MONGO_TICK,
                MONGO_ACTIVE_START, MONGO_ACTIVE_END, MONGO_CLSN1)

# Standing light kick (state 230). The hitbox is active while the leg/foot is
# extended forward.
emit_attack(lines, 230, 230, KICK_FRAMES, KICK_TICK, KICK_ACTIVE_START,
            KICK_ACTIVE_END, KICK_CLSN1)

# Standing strong kick (state 240). The hitbox is active while the foot is
# extended far forward.
emit_attack(lines, 240, 240, KICK_STRONG_FRAMES, KICK_STRONG_TICK,
            KICK_STRONG_ACTIVE_START, KICK_STRONG_ACTIVE_END,
            KICK_STRONG_CLSN1)

# Get-hit animations (receiving damage). All use the same "dparada" sprites.
for action in HIT_ACTIONS:
    emit_hurt(lines, action, 5000, HIT_FRAMES, HIT_TICK)

# Jump start (state 40). The jump velocity is applied when this animation ends.
lines.append("[Begin Action 40]")
lines.extend(clsn())
for i in range(JUMP_START_FRAMES):
    lines.append(f"40,{i}, 0,0, {JUMP_START_TICK}")
lines.append("")

# Air poses (state 50). 41 = neutral, 42/43 = forward/back, all reuse the
# same airborne sprites.
for action in (41, 42, 43):
    lines.append(f"[Begin Action {action}]")
    lines.extend(clsn())
    for i in range(JUMP_AIR_FRAMES):
        lines.append(f"41,{i}, 0,0, {JUMP_AIR_TICK}")
    lines.append("")

# Landing (state 52).
lines.append("[Begin Action 47]")
lines.extend(clsn())
for i in range(JUMP_LAND_FRAMES):
    lines.append(f"47,{i}, 0,0, {JUMP_LAND_TICK}")
lines.append("")

# Crouch walk forward (state 11 movement).
lines.append("[Begin Action 8]")
lines.extend(clsn())
for i in range(CROUCH_WALK_FRAMES):
    lines.append(f"8,{i}, 0,0, {CROUCH_WALK_TICK}")
lines.append("")

# Crouch walk backward.
lines.append("[Begin Action 9]")
lines.extend(clsn())
for i in range(CROUCH_WALK_FRAMES - 1, 0, -1):
    lines.append(f"8,{i}, 0,0, {CROUCH_WALK_TICK}")
lines.append(f"8,0, 0,0, {CROUCH_WALK_TICK}")
lines.append("")

# Stand to crouch (state 10).
lines.append("[Begin Action 10]")
lines.extend(clsn())
for i in range(CROUCH_DOWN_FRAMES):
    lines.append(f"10,{i}, 0,0, {CROUCH_DOWN_TICK}")
lines.append("")

# Crouching (state 11).
lines.append("[Begin Action 11]")
lines.extend(clsn())
for i in range(CROUCH_IDLE_FRAMES):
    lines.append(f"11,{i}, 0,0, {CROUCH_IDLE_TICK}")
lines.append("")

# Crouch to stand (state 12, plays crouch-down frames in reverse).
lines.append("[Begin Action 12]")
lines.extend(clsn())
for i in range(CROUCH_DOWN_FRAMES - 1, 0, -1):
    lines.append(f"10,{i}, 0,0, {CROUCH_DOWN_TICK}")
lines.append(f"10,0, 0,0, {CROUCH_DOWN_TICK}")
lines.append("")

# Fallback poses used by the standard KFM states.
fallback_single = [5, 6, 170, 181, 190, 191,
                   192, 195, 400, 410, 430, 440, 600, 610,
                   630, 640, 800, 810, 820, 1000, 1010, 1020, 1025, 1027, 1050,
                   1051, 1052, 1055, 1056, 1060, 1061, 1070, 1071, 1100, 1110,
                   1120, 1200, 1210, 1220, 1300, 1310, 1320, 1330, 1340, 1350,
                   1400, 1410, 1420, 3000, 3050, 3051, 5010, 5020, 5030,
                   5040, 5050, 5060, 5070, 5080, 5090, 5100, 5110, 5120, 5150,
                   5160, 5170, 5200, 5210, 5300]
for n in fallback_single:
    lines.append(f"[Begin Action {n}]")
    lines.append("0,0, 0,0, -1")
    lines.append("")

# Run forward (reuses first walk frames)
lines.append("[Begin Action 100]")
lines.append("20,0, 0,0, 3")
lines.append("20,1, 0,0, 3")
lines.append("20,2, 0,0, 3")
lines.append("20,3, 0,0, 3")
lines.append("")

# Hop backwards (reuses first walk frames)
lines.append("[Begin Action 105]")
lines.append("20,0, 0,0, 3")
lines.append("20,1, 0,0, 3")
lines.append("20,2, 0,0, 3")
lines.append("20,3, 0,0, -1")
lines.append("")

OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Created {OUTPUT} with idle action 0 ({IDLE_FRAMES} frames)")