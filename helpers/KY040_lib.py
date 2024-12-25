"""
KY040 Python Class
Martin O'Hanlon
stuffaboutcode.com


Additional code added by Conrad Storz 2015 and 2016

Additional code added by Adrian Steyer 2024
"""

import RPi.GPIO as GPIO
from time import sleep
import threading


class KY040:

    CLOCKWISE = 0
    ANTICLOCKWISE = 1
    DEBOUNCE = 50
    

    def __init__(self, clockPin, dataPin, switchPin, rotaryCallback, switchPressCallback, switchReleaseCallback):
        #persist values
        self.clockPin = clockPin
        self.dataPin = dataPin
        self.switchPin = switchPin
        self.rotaryCallback = rotaryCallback
        self.switchPressCallback = switchPressCallback
        self.switchReleaseCallback = switchReleaseCallback
        self._switch_state = False
        self._switch_thread = None
        self.running = False

        #setup pins
        GPIO.setup(clockPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(dataPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(switchPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
    def _switch_thread(self):
        while self.running:
            sleep(0.01)
            _switch_state = GPIO.input(self.switchPin)
            print(_switch_state)
            print(self._switch_state)
            if _switch_state != self._switch_state:
                sleep(self.DEBOUNCE * 0.001)
                if _switch_state == 0:
                    self.switchPressCallback()
                else:
                    self.switchReleaseCallback()
            self._switch_state = _switch_state

    def start(self):
        GPIO.add_event_detect(self.clockPin, GPIO.FALLING, callback=self._clockCallback, bouncetime=self.DEBOUNCE)
        self.switch_thread = threading.Thread(target=self._switch_thread)
        self.running = True
        self.switch_thread.start()

    def stop(self):
        GPIO.remove_event_detect(self.clockPin)
        GPIO.remove_event_detect(self.switchPin)
        self.running = False
        self.switch_thread.join()
    
    def _clockCallback(self, pin):
        if GPIO.input(self.clockPin) == 0:
            self.rotaryCallback(GPIO.input(self.dataPin))
        """
            data = GPIO.input(self.dataPin)
            if data == 1:
                self.rotaryCallback(self.ANTICLOCKWISE)
            else:
                self.rotaryCallback(self.CLOCKWISE)
        
        self.rotaryCallback(GPIO.input(self.dataPin))
        """

    def _switchPressCallback(self, pin):    
        self.switchPressCallback()
    
    def _switchReleaseCallback(self, pin):
        self.switchReleaseCallback()

#test
if __name__ == "__main__":

    print('Program start.')

    CLOCKPIN = 27
    DATAPIN = 22
    SWITCHPIN = 17

    def rotaryChange(direction):
        print("turned - " + str(direction))
    def switchPressed(pin):
        print("button connected to pin:{} pressed".format(pin))

    GPIO.setmode(GPIO.BCM)
    ky040 = KY040(CLOCKPIN, DATAPIN, SWITCHPIN, rotaryChange, switchPressed)

    print('Launch switch monitor class.')

    ky040.start()
    print('Start program loop...')
    try:
        while True:
            sleep(10)
            print('Ten seconds...')
    finally:
        print('Stopping GPIO monitoring...')
        ky040.stop()
        GPIO.cleanup()
        print('Program ended.')


