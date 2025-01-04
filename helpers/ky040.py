import RPi.GPIO as GPIO # type: ignore
KY = None
try:
    from .KY040_lib import KY040 as KY
except:
    try:
        from helpers.KY040_lib import KY040 as KY
    except:
        from KY040_lib import KY040 as KY

import os, time

CLOCKPIN = 21
DATAPIN = 16
SWITCHPIN = 13

GPIO.setmode(GPIO.BCM)

_clockwiseFunc = None
_counterclockwiseFunc = None
_switchPressFunc = None
_switchReleaseFunc = None

def _rotaryChange(direction):
    if direction == 1:
        _clockwiseFunc() #type: ignore
    else:
        _counterclockwiseFunc() #type: ignore
def _switchPressed():
    _switchPressFunc() #type: ignore

def _switchReleased():
    _switchReleaseFunc() #type: ignore

class KY040:
    def __init__(self, clockwiseCallback, counterclockwiseCallback, switchPressCallback, switchReleaseCallback):
        self.ky040 = KY(CLOCKPIN, DATAPIN, SWITCHPIN, _rotaryChange, _switchPressed, _switchReleased) #type: ignore
        #self.ky040.start()
        
        global _clockwiseFunc, _counterclockwiseFunc, _switchPressFunc, _switchReleaseFunc
        _clockwiseFunc = clockwiseCallback
        _counterclockwiseFunc = counterclockwiseCallback
        _switchPressFunc = switchPressCallback
        _switchReleaseFunc = switchReleaseCallback
    
    def stop(self):
        self.ky040.stop()
        
    def update(self):
        self.ky040.update()


if __name__ == "__main__":
    def ky040clockwiseFunc():
        print('clockwise')
    def ky040counterclockwiseFunc():
        print('counterclockwise')
    def ky040switchPressFunc():
        print('switch pressed')
    def ky040switchReleaseFunc():
        print('switch released')

    ky040 = KY040(ky040clockwiseFunc, ky040counterclockwiseFunc, ky040switchPressFunc, ky040switchReleaseFunc)
    try:
        while True:
            time.sleep(10)
    finally:
        print('Stopping GPIO monitoring...')
        ky040.stop()
        print('Program ended.')