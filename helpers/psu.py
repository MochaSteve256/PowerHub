import RPi.GPIO as gp
from time import sleep

gp.setmode(gp.BCM)

_pin = 23

gp.setup(_pin, gp.OUT)

def on():
    gp.output(_pin, True)

def off():
    gp.output(_pin, False)

def is_on():
    return gp.input(_pin)

if __name__ == "__main__":
    on()
    sleep(5)
    off()

