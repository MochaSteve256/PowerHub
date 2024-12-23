from helpers.KY040 import KY040
from helpers import psu
from helpers import u64led
from helpers import led_stripe
import u64images

import time

def rotaryChange(direction):
    if direction == 1:
        print("clockwise")
    else:
        print("counterclockwise")
def switchPressed():
    psu.off()
    u64led.set_matrix(u64images.psu_off)

if __name__ == "__main__":

    psu.on()
    led_stripe.clear()
    
    u64led.set_matrix(u64images.psu_on)
