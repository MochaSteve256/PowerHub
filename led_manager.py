from helpers import led_stripe
import threading
import time
import copy

import Adafruit_WS2801 # type: ignore

# colors
ww = (255, 130, 40)
w = (255, 160, 80)
cw = (255, 255, 255)

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
    arr = [(0, 0, 0) for _ in range(led_stripe.PIXEL_COUNT)]
    current_colors_rgb = [(0, 0, 0) for _ in range(led_stripe.PIXEL_COUNT)]
    start_colors = [(0, 0, 0) for _ in range(led_stripe.PIXEL_COUNT)]
    
    def __init__(self, stripe) -> None:
        self.ledState = LedState()
        self.end = 1
        self.stripe = stripe
        self.overtime = False
        self.target_color = None
        self.target_color_save = (0, 0, 0)
    
    def _generate_8px_rgb(self, array):
        line = [[0, 0, 0] for _ in range(8)]
        for i in range(8):
            led = int(i * (led_stripe.PIXEL_COUNT / 8))
            if array[led] is not None:
                line[i] = array[led]
        return [line]
    def current_8px_rgb(self):
        return self._generate_8px_rgb(self.arr)
    
    def preview_effect_8px(self, t_off, effect, target_color=None):
        ledState = copy.deepcopy(self.ledState)
        selfcopy = copy.deepcopy(self)
        t = (time.time() * 2) - (t_off * 2)
        if effect == self.stripe.warm_white:
            ledState.target = ledState.STATIC_COLOR
            return selfcopy._generate_8px_rgb(selfcopy._generate_array(t, ledState, target_color=ww))
        elif effect == self.stripe.white:
            ledState.target = ledState.STATIC_COLOR
            return selfcopy._generate_8px_rgb(selfcopy._generate_array(t, ledState, target_color=w))
        elif effect == self.stripe.cold_white:
            ledState.target = ledState.STATIC_COLOR
            return selfcopy._generate_8px_rgb(selfcopy._generate_array(t, ledState, target_color=cw))
        elif effect == self.stripe.black:
            ledState.target = ledState.STATIC_COLOR
            return selfcopy._generate_8px_rgb(selfcopy._generate_array(t, ledState, target_color=(0, 0, 0)))
        elif effect == self.stripe.rgb_cycle:
            ledState.target = ledState.RGB_CYCLE
            if selfcopy.overtime:
                ledState.current = ledState.RGB_CYCLE
            return selfcopy._generate_8px_rgb(selfcopy._generate_array(t, ledState))
        elif effect == self.stripe.argb_cycle:
            ledState.target = ledState.ARGB_CYCLE
            if selfcopy.overtime:
                ledState.current = ledState.ARGB_CYCLE
            return selfcopy._generate_8px_rgb(selfcopy._generate_array(t, ledState))
        else:
            print("error: cannot preview effect")
    def set_effect(self, effect:int):
        self.ledState.target = effect
    
    def _generate_array(self, t:float, ledState:LedState, target_color=None):
        for i in range(led_stripe.PIXEL_COUNT):
            if type(self.start_colors[i]) == int:
                self.start_colors[i] = Adafruit_WS2801.color_to_RGB(self.start_colors[i])
        self.target_color = copy.deepcopy(target_color)
        if t >= self.end:
            self.start_colors = copy.deepcopy(self.current_colors_rgb)
        if (ledState.current != ledState.target) or (target_color is not None):
            if (ledState.target == ledState.STATIC_COLOR) and (target_color is not None):
                self.target_color_save = target_color
                self.arr =[led_stripe.fade_cx_cy(i, self.start_colors[i], target_color, t) for i in range(led_stripe.PIXEL_COUNT)]
                self.end = 1
            elif ledState.target == ledState.RGB_CYCLE:
                if ledState.current == ledState.STATIC_COLOR or ledState.current == ledState.SUNRISE or ledState.current == ledState.SUNSET or ledState.current == ledState.ALARM:
                    self.arr =[led_stripe.fade_cx_rgb(i, self.start_colors[i], t) for i in range(led_stripe.PIXEL_COUNT)] 
                    self.end = 2
                elif ledState.current == ledState.ARGB_CYCLE:
                    if t < 1:
                        self.arr =[led_stripe.fade_cx_cy(i, self.start_colors[i], (0, 0, 0), t) for i in range(led_stripe.PIXEL_COUNT)]
                    else:
                        self.arr =[led_stripe.fade_black_rgb(i, t - 1) for i in range(led_stripe.PIXEL_COUNT)]
                    self.end = 2
            elif ledState.target == ledState.ARGB_CYCLE:
                if ledState.current == ledState.STATIC_COLOR or ledState.current == ledState.SUNRISE or ledState.current == ledState.SUNSET or ledState.current == ledState.ALARM:
                    self.arr =[led_stripe.fade_cx_argb(i, self.start_colors[i], t) for i in range(led_stripe.PIXEL_COUNT)]
                    self.end = 2
                elif ledState.current == ledState.RGB_CYCLE:
                    if t < 1:
                        self.arr =[led_stripe.fade_cx_cy(i, self.start_colors[i], (0, 0, 0), t) for i in range(led_stripe.PIXEL_COUNT)]
                    else:
                        self.arr =[led_stripe.fade_black_argb(i, t - 1) for i in range(led_stripe.PIXEL_COUNT)]
                    self.end = 2
            if t > self.end:
                ledState.current = ledState.target
                self.overtime = True
            else:
                self.overtime = False
        else:
            if ledState.current == ledState.RGB_CYCLE:
                self.arr =[led_stripe.rgb_cycle(i, t - self.end) for i in range(led_stripe.PIXEL_COUNT)]
            elif ledState.current == ledState.ARGB_CYCLE:
                self.arr =[led_stripe.argb_cycle(i, t - self.end) for i in range(led_stripe.PIXEL_COUNT)]
            elif ledState.current == ledState.SUNRISE:
                self.arr =[led_stripe.sunrise(i, t) for i in range(led_stripe.PIXEL_COUNT)]
            elif ledState.current == ledState.SUNSET:
                self.arr =[led_stripe.sunrise(i, -t + 30) for i in range(led_stripe.PIXEL_COUNT)]
            elif ledState.current == ledState.ALARM:
                self.arr =[led_stripe.alarm_cycle(i, t) for i in range(led_stripe.PIXEL_COUNT)]
            elif ledState.current == ledState.STATIC_COLOR:
                self.arr =[self.target_color_save for _ in range(led_stripe.PIXEL_COUNT)]
        self.current_colors_rgb = copy.deepcopy(self.arr)
        return self.arr


class LED_Stripe:
    t_offset = time.time()
    t = 0
    target_color = None
    
    def __init__(self) -> None:
        self.effects = Effects(self)
    
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
        self.target_color = ww
        self.effects.ledState.target = self.effects.ledState.STATIC_COLOR
    
    def white(self):
        self._callback()
        self.target_color = w
        self.effects.ledState.target = self.effects.ledState.STATIC_COLOR
    
    def cold_white(self):
        self._callback()
        self.target_color = cw
        self.effects.ledState.target = self.effects.ledState.STATIC_COLOR
    
    def black(self):
        self._callback()
        self.target_color = (0, 0, 0)
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
        arr = self.effects._generate_array(self.t, self.effects.ledState, target_color=self.target_color)
        if type(arr[0]) == tuple:
            led_stripe.set_array(arr)
        elif type(arr[0]) == int:
            led_stripe.set_array_color(arr)


if __name__ == '__main__':
    stripe = LED_Stripe()
    
    def thread():
        while True:
            stripe.update()
            time.sleep(0.01)
            
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
            elif x == 'yellow':
                stripe.new_color((255, 220, 0))
            elif x == 'black':
                stripe.black()
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
                print(stripe.effects.arr, stripe.effects.current_colors_rgb)
            else:
                print('unknown command')
    except KeyboardInterrupt:
        stripe.black()