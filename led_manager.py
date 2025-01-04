from helpers import led_stripe
import threading
import time
import copy

import Adafruit_WS2801 # type: ignore

# colors
ww = (255, 130, 40)
w = (255, 160, 80)
cw = (255, 255, 255)

class LEDState:
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
    pLastEffect = None
    selfcopy = None
    
    def __init__(self, stripe) -> None:
        self.LedState = LEDState()
        self.end = 1
        self.stripe = stripe
        self.overtime = False
        self.target_color = None
        self.target_color_save = (0, 0, 0)
    
    def _generate_8px_rgb(self, array, divider):
        line = [(0, 0, 0) for _ in range(8)]
        for i in range(8):
            led = int(i * (led_stripe.PIXEL_COUNT / 8))
            if array[led] is not None:
                if type(array[led]) == int:
                    line[i] = Adafruit_WS2801.color_to_RGB(array[led])
                line[i] = (line[i][0] // divider, line[i][1] // divider, line[i][2] // divider)
        return [line]
    def current_8px_rgb(self, divider):
        return self._generate_8px_rgb(self.arr, divider)
    
    def preview_effect_8px(self, t_off, divider, effect, targetColor=None):
        if self.selfcopy is None or effect != self.pLastEffect:
            self.selfcopy = copy.copy(self)
            self.pLastEffect = effect
        if self.selfcopy.overtime:
            self.selfcopy.target_color = None
            self.selfcopy.LedState.current = self.selfcopy.LedState.target
        pt = (time.time() * 2) - (t_off * 2)
        if effect == self.stripe.warm_white:
            self.selfcopy.LedState.target = self.selfcopy.LedState.STATIC_COLOR
            targetColor = ww
            x =self.selfcopy._generate_8px_rgb(self.selfcopy._generate_array(pt, self.selfcopy.LedState, targetColor), divider)
        elif effect == self.stripe.white:
            self.selfcopy.LedState.target = self.selfcopy.LedState.STATIC_COLOR
            targetColor = w
            x =self.selfcopy._generate_8px_rgb(self.selfcopy._generate_array(pt, self.selfcopy.LedState, targetColor), divider)
        elif effect == self.stripe.cold_white:
            self.selfcopy.LedState.target = self.selfcopy.LedState.STATIC_COLOR
            targetColor = cw
            x =self.selfcopy._generate_8px_rgb(self.selfcopy._generate_array(pt, self.selfcopy.LedState, targetColor), divider)
        elif effect == self.stripe.black:
            self.selfcopy.LedState.target = self.selfcopy.LedState.STATIC_COLOR
            targetColor = (0, 0, 0)
            x =self.selfcopy._generate_8px_rgb(self.selfcopy._generate_array(pt, self.selfcopy.LedState, targetColor), divider)
        elif effect == self.stripe.rgb_cycle:
            self.selfcopy.LedState.target = self.selfcopy.LedState.RGB_CYCLE
            x = self.selfcopy._generate_8px_rgb(Effects._generate_array(self.selfcopy, pt, self.selfcopy.LedState), divider)
        elif effect == self.stripe.argb_cycle:
            self.selfcopy.LedState.target = self.selfcopy.LedState.ARGB_CYCLE
            x = self.selfcopy._generate_8px_rgb(Effects._generate_array(self.selfcopy, pt, self.selfcopy.LedState), divider)
        else:
            print("error: cannot preview effect")
        
        return x

    
    def _generate_array(self, t:float, ledState:LEDState, target_color=None):
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
                print("wtf")
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
        self.effects.LedState.target = self.effects.LedState.STATIC_COLOR
    
    def rgb_cycle(self):
        self._callback()
        self.effects.LedState.target = self.effects.LedState.RGB_CYCLE
    
    def argb_cycle(self):
        self._callback()
        self.effects.LedState.target = self.effects.LedState.ARGB_CYCLE
    
    def warm_white(self):
        self._callback()
        self.target_color = ww
        self.effects.LedState.target = self.effects.LedState.STATIC_COLOR
    
    def white(self):
        self._callback()
        self.target_color = w
        self.effects.LedState.target = self.effects.LedState.STATIC_COLOR
    
    def cold_white(self):
        self._callback()
        self.target_color = cw
        self.effects.LedState.target = self.effects.LedState.STATIC_COLOR
    
    def black(self):
        self._callback()
        self.target_color = (0, 0, 0)
        self.effects.LedState.target = self.effects.LedState.STATIC_COLOR
    
    def sunrise(self):
        self._callback()
        self.effects.LedState.current = self.effects.LedState.SUNRISE
        self.effects.LedState.target = self.effects.LedState.SUNRISE
    
    def sunset(self):
        self._callback()
        self.effects.LedState.current = self.effects.LedState.SUNSET
        self.effects.LedState.target = self.effects.LedState.SUNSET
    
    def alarm(self):
        self._callback()
        self.effects.LedState.current = self.effects.LedState.ALARM
        self.effects.LedState.target = self.effects.LedState.ALARM
    
    def update(self):
        self.t = time.time() - self.t_offset
        if self.effects.overtime:
            self.target_color = None
        arr = self.effects._generate_array(self.t, self.effects.LedState, target_color=self.target_color)
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