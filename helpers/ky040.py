import RPi.GPIO as GPIO
from .KY040_lib import KY040 as KY
import os, time

CLOCKPIN = 21
DATAPIN = 16
SWITCHPIN = 13

GPIO.setmode(GPIO.BCM)

_clockwiseFunc = None
_counterclockwiseFunc = None
_switchFunc = None

def _rotaryChange(direction):
    if direction == 1:
        _clockwiseFunc()
    else:
        _counterclockwiseFunc()
def _switchPressed():
    _switchFunc()


class KY040:
    def __init__(self, clockwiseCallback, counterclockwiseCallback, switchCallback):
        self.ky040 = KY(CLOCKPIN, DATAPIN, SWITCHPIN, _rotaryChange, _switchPressed)
        self.ky040.start()
        
        global _clockwiseFunc, _counterclockwiseFunc, _switchFunc
        _clockwiseFunc = clockwiseCallback
        _counterclockwiseFunc = counterclockwiseCallback
        _switchFunc = switchCallback
    
    def stop(self):
        self.ky040.stop()


