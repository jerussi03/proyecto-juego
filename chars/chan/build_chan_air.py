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
PUNCH_ACTIVE_END = 27
PUNCH_CLSN1 = "20, -82, 42, -30"

CLSN = [
    "Clsn2Default: 2",
    "Clsn2[0] = -20, -100, 20, -50",
    "Clsn2[1] = -22, -50, 22, 0",
]


def clsn():
    return [f"    {line}" for line in CLSN]


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
lines.append("[Begin Action 200]")
lines.extend(clsn())
lines.append("    Clsn1Default: 0")
for i in range(PUNCH_FRAMES):
    if i == PUNCH_ACTIVE_START:
        lines.append("    Clsn1: 1")
        lines.append(f"    Clsn1[0] = {PUNCH_CLSN1}")
    elif i == PUNCH_ACTIVE_END + 1:
        lines.append("    Clsn1: 0")
    lines.append(f"200,{i}, 0,0, {PUNCH_TICK}")
lines.append("")

# Fallback poses used by the standard KFM states.
fallback_single = [5, 6, 10, 11, 12, 40, 41, 42, 43, 47, 170, 181, 190, 191,
                   192, 195, 210, 230, 240, 400, 410, 430, 440, 600, 610,
                   630, 640, 800, 810, 820, 1000, 1010, 1020, 1025, 1027, 1050,
                   1051, 1052, 1055, 1056, 1060, 1061, 1070, 1071, 1100, 1110,
                   1120, 1200, 1210, 1220, 1300, 1310, 1320, 1330, 1340, 1350,
                   1400, 1410, 1420, 3000, 3050, 3051, 5000, 5010, 5020, 5030,
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