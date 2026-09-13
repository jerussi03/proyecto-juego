import subprocess
import time
from PIL import ImageGrab

p = subprocess.Popen([".\\Ikemen_GO.exe"])
time.sleep(3.5)

try:
    shot = ImageGrab.grab()
    shot.save("scratch/title_screen_actual.png")
    print("Screenshot saved to scratch/title_screen_actual.png")
finally:
    p.kill()
    p.wait()
    print("Ikemen terminated cleanly")
