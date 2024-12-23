import RPi.GPIO as gp
from time import sleep

gp.setmode(gp.BCM)

pin = 23

gp.setup(pin, gp.OUT)

def on():
    gp.output(pin, True)

def off():
    gp.output(pin, False)

def is_on():
    return gp.input(pin)

if __name__ == "__main__":
    on()
    sleep(5)
    off()

