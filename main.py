import time

import ui_manager
import led_manager
from helpers import ky040


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
    
    led = led_manager.LED_Stripe()
    ui = ui_manager.UI(led)
    ky040 = ky040.KY040(ui.clockwise, ui.counterclockwise, press, release)

    try:
        while True:
            ui.update()
            time.sleep(.01)
    finally:
        ky040.stop()