import icoon
import threading
import time
import os

os.system("rm .stop_icon")
threading.Thread(target=lambda: icoon.start()).start()
while True:
    time.sleep(0.3)
    if os.path.isfile(".stop_icon"):
        break

icoon.icon.stop()
os.system("rm .stop_icon")
