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
    try:
        # For an output pin, we should check the output state, not input
        return gp.gpio_function(pin) == gp.OUT and gp.output(pin, gp.PUD_DOWN)
    except Exception as e:
        print(f"Error checking pin state: {e}")
        return None

if __name__ == "__main__":
    on()
    sleep(5)
    off()

