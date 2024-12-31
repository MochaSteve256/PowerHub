from helpers import led_stripe

import Adafruit_WS2801 # type: ignore

import time

class ledState:
    cycling = False
    static = True
    transitioning = False
    
    current_action = 0

    NONE = -1
    NEW_COLOR = 0
    RGB_CYCLE = 1
    ARGB_CYCLE = 2
    WARM_WHITE = 3
    WHITE = 4
    COLD_WHITE = 5
    SUNRISE = 6
    SUNSET = 7
    ALARM = 8


class Effects:
    arr = []
    
    def __init__(self) -> None:
        pass
    
    def current_8px_rgb(self):
        line = [[0, 0, 0] for _ in range(8)]
        for i in range(8):
            led = int(i * (led_stripe.PIXEL_COUNT / 8))
            if self.arr[led] is not None:
                line[i] = Adafruit_WS2801.color_to_RGB(self.arr[led])
        return line
    
    def update(self):
        pass