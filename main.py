from helpers.ky040 import KY040
from helpers import psu
from helpers import u64led
from helpers import led_stripe
import u64images

import time
import threading

leds = False

def ky040clockwiseFunc():
    global leds
    if leds:
        led_stripe.clear()
        leds = False
    else:
        led_stripe.set_all((255, 255, 255))
        leds = True

def ky040counterclockwiseFunc():
    print("counterclockwise")

def ky040switchFunc():
    if psu.is_on():
        print("psu off")
        psu.off()
        u64led.set_matrix(u64images.psu_off)
    else:
        psu.on()
        psuON = threading.Thread(target=psu_ON_actions)
        psuON.start()
        print("psu on")
        u64led.set_matrix(u64images.psu_on)

def psu_ON_actions():
    for i in range(100):
        leds = True
        led_stripe.clear()
        time.sleep(.005)

if __name__ == "__main__":

    psu.on()
    
    psuON = threading.Thread(target=psu_ON_actions)
    psuON.start()
    
    u64led.set_matrix(u64images.psu_on)
    
    ky040 = KY040(ky040clockwiseFunc, ky040counterclockwiseFunc, ky040switchFunc)
    
    try:
        while True:
            time.sleep(0.05)
    finally:
        ky040.stop()