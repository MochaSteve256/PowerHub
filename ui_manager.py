from calendar import c
import time
import datetime
import copy
from pprint import pprint

from helpers import u64led
from helpers import u64images
from helpers import psu
import led_manager
import Adafruit_WS2801 # type: ignore


class uiState():
    PSU = 0
    LED = 1
    LED_SLCT = 2
    LED_CUSTOM = 6
    WETH = 3
    CLCK = 4
    STBY = 5

class ledState():
    WW = 0
    W = 1
    CW = 2
    BLACK = 3
    RGB = 4
    ARGB = 5
    CUSTOM = 6

#nav options
class NavOpts():
    ##    select, back, scroll
    psu = [True, False, True]
    led = [True, False, True]
    led_slct = [True, True, True]
    weth = [False, False, True]
    clck = [True, False, True]
    stby = [True, False, True]

class UI:
    standby = False
    ledEffectNum = 0
    led_t_offset = time.time()
    led_target_color = (0, 0, 0)
    
    def __init__(self, ledStripe):
        self.ledStripe = ledStripe
        self.state = uiState.PSU
        self.last_click = time.time()
        self.update()
        #watchpoints.watch(self.standby, callback=self._stby_callback, when=lambda x: x == True)

    def _stby_check(self):
        self.last_click = time.time()
        if self.standby:
            self.standby = False
            self.update()
            return True
        return False
    
    def _stby_callback(self, *_args):
        print("standby callback")
        self._last_standby_switch = time.time()
    

    def _nighttime_check(self):
        if datetime.datetime.now().hour < 6 or datetime.datetime.now().hour > 22:
            return True
        return False
    
    def clockwise(self):
        if self._stby_check():
            return
        if self.state == uiState.PSU:
            self.state = uiState.LED
            self.update()
        elif self.state == uiState.LED:
            self.state = uiState.CLCK
            self.update()
        elif self.state == uiState.LED_SLCT:
            self.ledEffectNum += 1
            if self.ledEffectNum == 7:
                self.ledEffectNum = 0
            self.led_t_offset = time.time()
        elif self.state == uiState.WETH:
            self.state = uiState.STBY
            self.update()
        elif self.state == uiState.CLCK:
            self.state = uiState.WETH
            self.update()
        elif self.state == uiState.STBY:
            self.state = uiState.PSU
            self.update()
    def counterclockwise(self):
        if self._stby_check():
            return
        if self.state == uiState.PSU:
            self.state = uiState.STBY
            self.update()
        elif self.state == uiState.LED:
            self.state = uiState.PSU
            self.update()
        elif self.state == uiState.LED_SLCT:
            self.ledEffectNum -= 1
            if self.ledEffectNum == -1:
                self.ledEffectNum = 6
            self.led_t_offset = time.time()
        elif self.state == uiState.WETH:
            self.state = uiState.CLCK
            self.update()
        elif self.state == uiState.CLCK:
            self.state = uiState.LED
            self.update()
        elif self.state == uiState.STBY:
            self.state = uiState.WETH
            self.update()
    def select(self):
        if self._stby_check():
            return
        if self.state == uiState.PSU:
            if psu.is_on():
                psu.off()
                self.update()
            else:
                psu.on()
                self.update()
        elif self.state == uiState.LED:
            self.state = uiState.LED_SLCT
            self.update()
        elif self.state == uiState.LED_SLCT:
            if self.ledEffectNum == ledState.CUSTOM:
                self.state = uiState.LED_CUSTOM
                self.update()
            elif self.ledEffectNum == ledState.WW:
                self.ledStripe.warm_white()
            elif self.ledEffectNum == ledState.W:
                self.ledStripe.white()
            elif self.ledEffectNum == ledState.CW:
                self.ledStripe.cold_white()
            elif self.ledEffectNum == ledState.BLACK:
                self.ledStripe.new_color((0, 0, 0))
            elif self.ledEffectNum == ledState.RGB:
                self.ledStripe.rgb_cycle()
            elif self.ledEffectNum == ledState.ARGB:
                self.ledStripe.argb_cycle()
            self.state = uiState.LED
            self.update()
        elif self.state == uiState.LED_CUSTOM:
            self.state = uiState.LED
            self.update()
        elif self.state == uiState.STBY:
            self.standby = not self.standby
            if self.standby:
                self._last_standby_switch = time.time()
            self.update()
    def back(self):
        if self._stby_check():
            return
        if self.state == uiState.LED_SLCT:
            self.state = uiState.LED
            self.update()
        if self.state == uiState.LED_CUSTOM:
            self.state = uiState.LED_SLCT
            self.update()
    
    def update(self):
        # auto standby
        if time.time() - self.last_click > 10:
            if not self.standby:
                self.standby = True
                self._last_standby_switch = time.time()
        
        # standby logic
        if self.standby:
            if not self._nighttime_check():
                self.state = uiState.CLCK
                if time.time() - self._last_standby_switch > 10:
                    self.state = uiState.WETH
                if time.time() - self._last_standby_switch > 20:
                    self._last_standby_switch = time.time()
            else:
                self.state = uiState.CLCK
                if time.time() - self._last_standby_switch > 60:
                    self._last_standby_switch = time.time()
        
        # ui functions
        if self.state == uiState.PSU:
            self.psu_ui()
        elif self.state == uiState.LED:
            self.led_ui()
        elif self.state == uiState.LED_SLCT:
            self.led_slct_ui()
        elif self.state == uiState.LED_CUSTOM:
            self.led_custom_ui()
        elif self.state == uiState.WETH:
            self.weth_ui()
        elif self.state == uiState.CLCK:
            self.clck_ui()
        elif self.state == uiState.STBY:
            self.stby_ui()
        
        # brightness adjustment at standby
        if self.standby:
            divider = 0
            if self._nighttime_check():
                divider = 5
            else:
                divider = 2
            matrix = u64led.get_matrix()
            for i in range(8):
                for j in range(8):
                    for k in range(3):
                        matrix[i][j][k] = int(matrix[i][j][k] / divider)
            u64led.set_matrix(matrix)
        
        u64led.show_matrix()

    def psu_ui(self):
        m = []
        if psu.is_on():
            m = u64images.add_navbar(u64images.psu_text + u64images.psu_on, *NavOpts.psu)
        else:
            m = u64images.add_navbar(u64images.psu_text + u64images.psu_off, *NavOpts.psu)
        u64led.set_matrix(m)

    def led_ui(self):
        m = u64images.add_navbar(u64images.led_text + u64images.nothing1 + self.ledStripe.effects.current_8px_rgb() + u64images.nothing1, *NavOpts.led)
        m = clean_convert_matrix(m)
        u64led.set_matrix(m)

    def led_slct_ui(self):
        m = None
        p = None
        if self.ledEffectNum == ledState.WW:
            p = self.ledStripe.effects.preview_effect_8px(self.led_t_offset, self.ledStripe.warm_white)
        elif self.ledEffectNum == ledState.W:
            p = self.ledStripe.effects.preview_effect_8px(self.led_t_offset, self.ledStripe.white)
        elif self.ledEffectNum == ledState.CW:
            p = self.ledStripe.effects.preview_effect_8px(self.led_t_offset, self.ledStripe.cold_white)
        elif self.ledEffectNum == ledState.BLACK:
            p = self.ledStripe.effects.preview_effect_8px(self.led_t_offset, self.ledStripe.black)
        elif self.ledEffectNum == ledState.RGB:
            p = self.ledStripe.effects.preview_effect_8px(self.led_t_offset, self.ledStripe.rgb_cycle)
        elif self.ledEffectNum == ledState.ARGB:
            p = self.ledStripe.effects.preview_effect_8px(self.led_t_offset, self.ledStripe.argb_cycle)
        elif self.ledEffectNum == ledState.CUSTOM:
            #something else
            p = [[(0, 0, 0) for _ in range(8)]]
        else:
            print("error: invalid ledEffectNum")
        
        x = u64images.add_navbar(u64images.nothing3 + p + u64images.nothing1 + u64images.nothing3, *NavOpts.led_slct) # type: ignore
        m = copy.deepcopy(x)
        m = clean_convert_matrix(m)
        print(m)
        m[0][self.ledEffectNum] = (0, 128, 0) # type: ignore
        print(m)
        u64led.set_matrix(m)
    
    def led_custom_ui(self):
        m = u64images.add_navbar(u64images.blank, *NavOpts.led_slct)
        u64led.set_matrix(m)

    def weth_ui(self):
        m = u64images.add_navbar(u64images.blank, *NavOpts.weth)#TODO
        u64led.set_matrix(m)

    def clck_ui(self):
        u64led.set_matrix(u64images.add_navbar(u64images.blank, *NavOpts.clck))#TODO

    def stby_ui(self):
        u64led.set_matrix(u64images.add_navbar(u64images.stby_text, *NavOpts.stby))
def clean_convert_matrix(mtx):
    for y in range(8):
        for x in range(8):
            try:
                if type(mtx[y][x]) == int: # type: ignore
                    mtx[y][x] = Adafruit_WS2801.color_to_RGB(mtx[y][x]) # type: ignore
            except Exception as e:
                print(e, mtx, y, x)
                return
    return mtx