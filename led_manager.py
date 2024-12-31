from helpers import led_stripe

import Adafruit_WS2801 # type: ignore

import time

class ledState:
    #cycling = False
    static = True
    transitioning = False
    
    current = 0
    target = 0
    action = 0
    
    # States
    STATIC_COLOR = 0
    RGB_CYCLE = 1
    ARGB_CYCLE = 2
    SUNRISE = 3
    SUNSET = 4
    ALARM = 5
    
    # Actions
    Nothing = -1
    Fade_Cx_Cy = 0
    Fade_Cx_Rgb = 1
    Fade_Cx_Argb = 2
    Rgb_Cycle = 3
    Argb_Cycle = 4
    Sunrise = 5
    Sunset = 6
    Alarm = 7
    
class Effects:
    arr = []
    current_static_color_rgb = (0, 0, 0)
    
    def __init__(self) -> None:
        pass
    
    def _generate_8px_rgb(self, array):
        line = [[0, 0, 0] for _ in range(8)]
        for i in range(8):
            led = int(i * (led_stripe.PIXEL_COUNT / 8))
            if array[led] is not None:
                line[i] = Adafruit_WS2801.color_to_RGB(array[led])
        return line
    def current_8px_rgb(self):
        return self._generate_8px_rgb(self.arr)
    
    def preview_effect_8px(self):
        pass
    
    def set_effect(self, effect:int):
        pass
    
    def _generate_array(self, t, target_color=None, start_color=current_static_color_rgb):
        arr = []
        if ledState.current != ledState.target:
            if ledState.target == ledState.STATIC_COLOR:
                if ledState.current == ledState.STATIC_COLOR:
                    arr = [led_stripe.fade_cx_cy(i, start_color, target_color, t) for i in range(led_stripe.PIXEL_COUNT)]
                elif ledState.current == ledState.RGB_CYCLE:
                    if target_color == (0, 0, 0):
                        arr = [led_stripe.fade_black_rgb(i, -t + 1) for i in range(led_stripe.PIXEL_COUNT)]
                    else:
                        arr = [led_stripe.fade_cx_rgb(i, led_stripe.get_pixel_rgb(i), -t + 2) for i in range(led_stripe.PIXEL_COUNT)]
                elif ledState.current == ledState.ARGB_CYCLE:
                    arr = [led_stripe.fade_cx_argb(i, start_color, -t + 2) for i in range(led_stripe.PIXEL_COUNT)]
            elif ledState.target == ledState.RGB_CYCLE:
                if ledState.current == ledState.STATIC_COLOR:
                    arr = [led_stripe.fade_cx_rgb(i, start_color, t) for i in range(led_stripe.PIXEL_COUNT)] 
                elif ledState.current == ledState.ARGB_CYCLE:
                    if t < 1:
                        arr = [led_stripe.fade_black_argb(i, -t + 1) for i in range(led_stripe.PIXEL_COUNT)]
                    else:
                        arr = [led_stripe.fade_black_rgb(i, t - 1) for i in range(led_stripe.PIXEL_COUNT)]
            elif ledState.target == ledState.ARGB_CYCLE:
                if ledState.current == ledState.STATIC_COLOR:
                    arr = [led_stripe.fade_cx_argb(i, start_color, t) for i in range(led_stripe.PIXEL_COUNT)] 
                elif ledState.current == ledState.RGB_CYCLE:
                    if t < 1:
                        arr = [led_stripe.fade_black_rgb(i, -t + 1) for i in range(led_stripe.PIXEL_COUNT)]
                    else:
                        arr = [led_stripe.fade_black_argb(i, t - 1) for i in range(led_stripe.PIXEL_COUNT)]
        else:
            if ledState.current == ledState.RGB_CYCLE:
                arr = [led_stripe.rgb_cycle(i, t) for i in range(led_stripe.PIXEL_COUNT)]
            elif ledState.current == ledState.ARGB_CYCLE:
                arr = [led_stripe.argb_cycle(i, t) for i in range(led_stripe.PIXEL_COUNT)]
            elif ledState.current == ledState.SUNRISE:
                arr = [led_stripe.sunrise(i, t) for i in range(led_stripe.PIXEL_COUNT)]
            elif ledState.current == ledState.SUNSET:
                arr = [led_stripe.sunrise(i, -t + 30) for i in range(led_stripe.PIXEL_COUNT)]
            elif ledState.current == ledState.ALARM:
                arr = [led_stripe.alarm_cycle(i, t) for i in range(led_stripe.PIXEL_COUNT)]
        led_stripe.set_array_color(arr)


class LED_Stripe:
    def __init__(self) -> None:
        pass
    
    def new_color(self, rgb):
        pass
    
    def rgb_cycle(self):
        pass
    
    def argb_cycle(self):
        pass
    
    def warm_white(self):
        pass
    
    def white(self):
        pass
    
    def cold_white(self):
        pass
    
    def sunrise(self):
        pass
    
    def sunset(self):
        pass
    
    def alarm(self):
        pass
    
    def update(self, t):
        pass