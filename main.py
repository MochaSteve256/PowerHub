import ui_manager
from helpers import ky040
from helpers import led_stripe

import time


press_time = 0
release_time = 0

def press():
    global press_time
    press_time = time.time()

def release():
    global press_time, release_time
    release_time = time.time()
    if release_time - press_time < 0.5:
        ui.select()
    else:
        ui.back()

if __name__ == "__main__":
    
    ui = ui_manager.UI()
    
    ky040 = ky040.KY040(ui.clockwise, ui.counterclockwise, press, release)

    try:
        while True:
            time.sleep(1)
    finally:
        ky040.stop()