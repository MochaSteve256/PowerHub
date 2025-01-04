"""
KY040 Python Class
Martin O'Hanlon
stuffaboutcode.com


Additional code added by Conrad Storz 2015 and 2016

Additional code added by Adrian Steyer 2024
"""

import RPi.GPIO as GPIO# type: ignore
from time import sleep
import threading


class KY040:

    CLOCKWISE = 0
    ANTICLOCKWISE = 1
    DEBOUNCE = 50

    def __init__(self, clockPin, dataPin, switchPin, rotaryCallback, switchPressCallback, switchReleaseCallback):
        # Persist values
        self.clockPin = clockPin
        self.dataPin = dataPin
        self.switchPin = switchPin
        self.rotaryCallback = rotaryCallback
        self.switchPressCallback = switchPressCallback
        self.switchReleaseCallback = switchReleaseCallback
        self._switch_state = True
        self.running = False
        self._switch_thread = None

        # Setup pins
        GPIO.setup(clockPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(dataPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(switchPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Relocate from start()
        print("Starting KY040")
        GPIO.add_event_detect(self.clockPin, GPIO.FALLING, callback=self._clockCallback, bouncetime=self.DEBOUNCE)

    def _switch_monitor(self):
        print("Switch monitoring thread running")
        while self.running:
            sleep(0.005)
    
    def update(self):
        switch_state = GPIO.input(self.switchPin)
        if switch_state != self._switch_state:
            sleep(self.DEBOUNCE * 0.001)
            if switch_state == GPIO.LOW:
                self.switchPressCallback()
            else:
                self.switchReleaseCallback()
            self._switch_state = switch_state

    def start(self):
        self.running = True
        self._switch_thread = threading.Thread(target=self._switch_monitor)
        self._switch_thread.start()

    def stop(self):
        print("Stopping KY040")
        GPIO.remove_event_detect(self.clockPin)
        self.running = False
        if self._switch_thread:
            self._switch_thread.join()

    def _clockCallback(self, pin):
        if GPIO.input(self.clockPin) == GPIO.LOW:
            data = GPIO.input(self.dataPin)
            if data == GPIO.HIGH:
                self.rotaryCallback(self.ANTICLOCKWISE)
            else:
                self.rotaryCallback(self.CLOCKWISE)

    def _switchPressCallback(self, pin):
        self.switchPressCallback()

    def _switchReleaseCallback(self, pin):
        self.switchReleaseCallback()


# Test
if __name__ == "__main__":
    print('Program start.')

    CLOCKPIN = 27
    DATAPIN = 22
    SWITCHPIN = 17

    def rotaryChange(direction):
        print("Turned - " + ("Clockwise" if direction == KY040.CLOCKWISE else "Anticlockwise"))

    def switchPressed(pin):
        print(f"Button connected to pin:{pin} pressed")

    def switchReleased(pin):
        print(f"Button connected to pin:{pin} released")

    GPIO.setmode(GPIO.BCM)

    try:
        ky040 = KY040(CLOCKPIN, DATAPIN, SWITCHPIN, rotaryChange, switchPressed, switchReleased)
        print('Launch switch monitor class.')

        ky040.start()
        print('Start program loop...')
        while True:
            sleep(1)
    except KeyboardInterrupt:
        print('Stopping GPIO monitoring...')
    finally:
        ky040.stop()
        GPIO.cleanup()
        print('Program ended.')