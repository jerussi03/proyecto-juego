import subprocess
import time
from PIL import ImageGrab

p = subprocess.Popen([
    ".\\Ikemen_GO.exe",
    "-p1", "chava",
    "-p2", "hector",
    "-s", "stages/patio.def",
    "-time", "30"
])

# Wait for game window and fight to load
time.sleep(3.8)

try:
    shot = ImageGrab.grab()
    shot.save("scratch/match_screen.png")
    print("Screenshot saved to scratch/match_screen.png")
finally:
    p.kill()
    p.wait()
    print("Process finished cleanly")
