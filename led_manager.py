from math import e
from helpers import led_stripe

import Adafruit_WS2801 # type: ignore

import threading
import time

class LedState:
    # Properties
    current = 0
    target = 0
    
    # States
    STATIC_COLOR = 0
    RGB_CYCLE = 1
    ARGB_CYCLE = 2
    SUNRISE = 3
    SUNSET = 4
    ALARM = 5
    

class Effects:
    arr = []
    current_colors_rgb = [(0, 0, 0) for _ in range(led_stripe.PIXEL_COUNT)]
    
    def __init__(self) -> None:
        self.ledState = LedState()
        self.end = 1
        self.overtime = False
        self.target_color = None
        self.target_color_save = None
    
    def _generate_8px_rgb(self, array):
        line = [[0, 0, 0] for _ in range(8)]
        for i in range(8):
            led = int(i * (led_stripe.PIXEL_COUNT / 8))
            if array[led] is not None:
                line[i] = array[led]
        return line
    def current_8px_rgb(self):
        return self._generate_8px_rgb(self.arr)
    
    def preview_effect_8px(self, t:float, effect:int, target_color=None):
        ledState = self.ledState
        ledState.target = effect
        return self._generate_8px_rgb(self._generate_array(t, ledState, target_color))
    
    def set_effect(self, effect:int):
        self.ledState.target = effect
    
    def _generate_array(self, t:float, ledState:LedState, target_color=None, start_colors=current_colors_rgb):
        arr = start_colors
        self.target_color = target_color
        if ledState.current != ledState.target:
            if (ledState.target == ledState.STATIC_COLOR) and (target_color is not None):
                self.target_color_save = target_color
                if ledState.current == ledState.STATIC_COLOR:
                    arr = [led_stripe.fade_cx_cy(i, start_colors[i], target_color, t) for i in range(led_stripe.PIXEL_COUNT)]
                    self.end = 1
                    print(start_colors, target_color, ledState.current, ledState.target)
                elif ledState.current == ledState.RGB_CYCLE:
                    arr = [led_stripe.fade_cx_cy(i, start_colors[i], target_color, t) for i in range(led_stripe.PIXEL_COUNT)]
                    self.end = 1
                elif ledState.current == ledState.ARGB_CYCLE:
                    if target_color == (0, 0, 0):
                        arr = [led_stripe.fade_black_argb(i, -t + 1) for i in range(led_stripe.PIXEL_COUNT)]
                        self.end = 1
                    else:
                        arr = [led_stripe.fade_cx_argb(i, start_colors[i], -t + 2) for i in range(led_stripe.PIXEL_COUNT)]
                        self.end = 2
            elif ledState.target == ledState.RGB_CYCLE:
                if ledState.current == ledState.STATIC_COLOR:
                    if start_colors[0] == (0, 0, 0):
                        arr = [led_stripe.fade_black_rgb(i, t) for i in range(led_stripe.PIXEL_COUNT)]
                        self.end = 1
                    else:
                        arr = [led_stripe.fade_cx_rgb(i, start_colors[i], t) for i in range(led_stripe.PIXEL_COUNT)] 
                        self.end = 2
                elif ledState.current == ledState.ARGB_CYCLE:
                    if t < 1:
                        arr = [led_stripe.fade_black_argb(i, -t + 1) for i in range(led_stripe.PIXEL_COUNT)]
                    else:
                        arr = [led_stripe.fade_black_rgb(i, t - 1) for i in range(led_stripe.PIXEL_COUNT)]
                    self.end = 2
            elif ledState.target == ledState.ARGB_CYCLE:
                if ledState.current == ledState.STATIC_COLOR:
                    if start_colors[0] == (0, 0, 0):
                        arr = [led_stripe.fade_black_argb(i, t) for i in range(led_stripe.PIXEL_COUNT)]
                        self.end = 1
                    else:
                        arr = [led_stripe.fade_cx_argb(i, start_colors[i], t) for i in range(led_stripe.PIXEL_COUNT)]
                        self.end = 2
                elif ledState.current == ledState.RGB_CYCLE:
                    if t < 1:
                        arr = [led_stripe.fade_black_rgb(i, -t + 1) for i in range(led_stripe.PIXEL_COUNT)]
                    else:
                        arr = [led_stripe.fade_black_argb(i, t - 1) for i in range(led_stripe.PIXEL_COUNT)]
                    self.end = 2
            if t >= self.end:
                ledState.current = ledState.target
                self.overtime = True
            else:
                self.overtime = False
        else:
            if ledState.current == ledState.RGB_CYCLE:
                arr = [led_stripe.rgb_cycle(i, t - self.end) for i in range(led_stripe.PIXEL_COUNT)]
            elif ledState.current == ledState.ARGB_CYCLE:
                arr = [led_stripe.argb_cycle(i, t - self.end) for i in range(led_stripe.PIXEL_COUNT)]
            elif ledState.current == ledState.SUNRISE:
                arr = [led_stripe.sunrise(i, t) for i in range(led_stripe.PIXEL_COUNT)]
            elif ledState.current == ledState.SUNSET:
                arr = [led_stripe.sunrise(i, -t + 30) for i in range(led_stripe.PIXEL_COUNT)]
            elif ledState.current == ledState.ALARM:
                arr = [led_stripe.alarm_cycle(i, t) for i in range(led_stripe.PIXEL_COUNT)]
            elif ledState.current == ledState.STATIC_COLOR:
                print('target_color_save', self.target_color_save)
                arr = [self.target_color_save for _ in range(led_stripe.PIXEL_COUNT)]
        self.current_colors_rgb = arr
        return arr


class LED_Stripe:
    t_offset = time.time()
    t = 0
    target_color = None
    
    def __init__(self) -> None:
        self.effects = Effects()
        self.arr = [None for _ in range(led_stripe.PIXEL_COUNT)]
    
    def _callback(self):
        self.t_offset = time.time()
        self.effects.overtime = False
    
    def new_color(self, rgb):
        self._callback()
        self.target_color = rgb
        self.effects.ledState.target = self.effects.ledState.STATIC_COLOR
    
    def rgb_cycle(self):
        self._callback()
        self.effects.ledState.target = self.effects.ledState.RGB_CYCLE
    
    def argb_cycle(self):
        self._callback()
        self.effects.ledState.target = self.effects.ledState.ARGB_CYCLE
    
    def warm_white(self):
        self._callback()
        self.target_color = (255, 210, 90)
        self.effects.ledState.target = self.effects.ledState.STATIC_COLOR
    
    def white(self):
        self._callback()
        self.target_color = (255, 230, 130)
        self.effects.ledState.target = self.effects.ledState.STATIC_COLOR
    
    def cold_white(self):
        self._callback()
        self.target_color = (255, 255, 255)
        self.effects.ledState.target = self.effects.ledState.STATIC_COLOR
    
    def sunrise(self):
        self._callback()
        self.effects.ledState.current = self.effects.ledState.SUNRISE
        self.effects.ledState.target = self.effects.ledState.SUNRISE
    
    def sunset(self):
        self._callback()
        self.effects.ledState.current = self.effects.ledState.SUNSET
        self.effects.ledState.target = self.effects.ledState.SUNSET
    
    def alarm(self):
        self._callback()
        self.effects.ledState.current = self.effects.ledState.ALARM
        self.effects.ledState.target = self.effects.ledState.ALARM
    
    def update(self):
        self.t = time.time() - self.t_offset
        if self.effects.overtime:
            self.target_color = None
        self.arr = self.effects._generate_array(self.t, self.effects.ledState, target_color=self.target_color)
        if type(self.arr[0]) == tuple:
            led_stripe.set_array(self.arr)
        elif type(self.arr[0]) == int:
            led_stripe.set_array_color(self.arr)


if __name__ == '__main__':
    stripe = LED_Stripe()
    
    def thread():
        while True:
            stripe.update()
            time.sleep(0.05)
            
    t = threading.Thread(target=thread)
    t.start()
    
    try:
        while True:
            x = input("Enter command: ")
            if x == 'w':
                stripe.white()
            elif x == 'cw':
                stripe.cold_white()
            elif x == 'ww':
                stripe.warm_white()
            elif x == 'red':
                stripe.new_color((255, 0, 0))
            elif x == 'green':
                stripe.new_color((0, 255, 0))
            elif x == 'blue':
                stripe.new_color((0, 0, 255))
            elif x == 'rgb':
                stripe.rgb_cycle()
            elif x == 'argb':
                stripe.argb_cycle()
            elif x == 'sunrise':
                stripe.sunrise()
            elif x == 'sunset':
                stripe.sunset()
            elif x == 'alarm':
                stripe.alarm()
            elif x == 'print':
                print(stripe.arr, stripe.effects.current_colors_rgb)
            elif x == 'q':
                break
            else:
                print('unknown command')
    except KeyboardInterrupt:
        pass