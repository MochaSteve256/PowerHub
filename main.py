from helpers.ky040 import KY040
from helpers import psu
from helpers import u64led
from helpers import led_stripe
import u64images

import time

def clockwiseFunc():
    print("clockwise")

def counterclockwiseFunc():
    print("counterclockwise")

def switchFunc():
    if psu.is_on():
        print("psu off")
        psu.off()
        u64led.set_matrix(u64images.psu_off)
    else:
        print("psu on")
        psu.on()
        led_stripe.clear()
        u64led.set_matrix(u64images.psu_on)

if __name__ == "__main__":

    psu.on()
    
    time.sleep(1)
    led_stripe.clear()
    
    u64led.set_matrix(u64images.psu_on)
    
    ky040 = KY040(clockwiseFunc, counterclockwiseFunc, switchFunc)
    
    try:
        while True:
            time.sleep(0.05)
    finally:
        ky040.stop()