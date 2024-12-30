import ui_manager
from helpers import ky040
from helpers import led_stripe

import time

press_time = 0
back_triggered = False
is_pressed = False  # Track whether the button is currently pressed

def press():
    global press_time, back_triggered, is_pressed
    press_time = time.time()
    back_triggered = False
    is_pressed = True  # Button is now pressed

def update():  # Call this in your main loop
    global back_triggered, is_pressed
    # Only check for back trigger if button is still pressed
    if is_pressed and time.time() - press_time >= 0.5 and not back_triggered:
        back_triggered = True
        ui.back()

def release():
    global is_pressed, back_triggered
    if is_pressed:
        if time.time() - press_time < 0.5 and not back_triggered:
            ui.select()
        is_pressed = False  # Button is no longer pressed

if __name__ == "__main__":
    
    ui = ui_manager.UI()
    
    ky040 = ky040.KY040(ui.clockwise, ui.counterclockwise, press, release)

    try:
        while True:
            time.sleep(.01)
            update()
    finally:
        ky040.stop()