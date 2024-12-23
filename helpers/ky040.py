import RPi.GPIO as GPIO
from .KY040_lib import KY040 as KY
import os, time

CLOCKPIN = 21
DATAPIN = 16
SWITCHPIN = 13

GPIO.setmode(GPIO.BCM)

clockwiseFunc = None
counterclockwiseFunc = None
switchFunc = None

def rotaryChange(direction):
    if direction == 1:
        clockwiseFunc()
    else:
        counterclockwiseFunc()
def switchPressed():
    switchFunc()


class KY040:
    def __init__(self, clockwiseCallback, counterclockwiseCallback, switchCallback):
        self.ky040 = KY(CLOCKPIN, DATAPIN, SWITCHPIN, rotaryChange, switchPressed)
        self.ky040.start()
        
        global clockwiseFunc, counterclockwiseFunc, switchFunc
        clockwiseFunc = clockwiseCallback
        counterclockwiseFunc = counterclockwiseCallback
        switchFunc = switchCallback
    
    def stop(self):
        self.ky040.stop()


if __name__ == "__main__":

    ky040 = KY040(CLOCKPIN, DATAPIN, SWITCHPIN, rotaryChange, switchPressed)

    ky040.start()

    try:
        while True:
            time.sleep(0.05)
    finally:
        ky040.stop()
