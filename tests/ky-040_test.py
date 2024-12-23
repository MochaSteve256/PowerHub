import RPi.GPIO as GPIO
from helpers.KY040 import KY040
import os, time


def rotaryChange(direction):
    if direction == 1:
        print("clockwise")
    else:
        print("counterclockwise")
def switchPressed():
    print("button pressed")


if __name__ == "__main__":

    CLOCKPIN = 21
    DATAPIN = 16
    SWITCHPIN = 13

    
    GPIO.setmode(GPIO.BCM)
    
    ky040 = KY040(CLOCKPIN, DATAPIN, SWITCHPIN, rotaryChange, switchPressed)

    ky040.start()

    try:
        while True:
            time.sleep(0.05)
    finally:
        ky040.stop()
        GPIO.cleanup()
