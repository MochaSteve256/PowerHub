import time
import datetime
import copy
from pprint import pprint

from helpers import u64led
import u64images
from helpers import psu
import clock

import Adafruit_WS2801 # type: ignore


class uiState():
    PSU = 0
    LED = 1
    LED_SLCT = 2
    WETH = 3
    CLCK = 4
    STBY = 5
    ALM = 6

class ledState():
    WW = 1
    W = 2
    CW = 3
    BLACK = 0
    RGB = 4
    ARGB = 5

#nav options
class NavOpts():
    ##    select, back, scroll
    psu = [True, False, True]
    led = [True, False, True]
    led_slct = [True, True, True]
    weth = [False, False, True]
    clck = [True, False, True]
    stby = [True, False, True]
    alm = [True, False, False]

class UI:
    standby = False
    ledEffectNum = 0
    led_t_offset = time.time()
    led_target_color = (0, 0, 0)
    before_stby_ui = 0
    auto_stby = True
    
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
            if self.before_stby_ui == uiState.LED_SLCT:
                self.before_stby_ui = uiState.LED
            self.state = self.before_stby_ui
            self.update()
            self.before_stby_ui = self.state
            return True
        return False
    
    def _stby_callback(self):
        print("standby callback")
        self.standby = True
        self._last_standby_switch = time.time()
        self.before_stby_ui = self.state

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
            if self.ledEffectNum == 6:
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
                self.ledEffectNum = 5
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
            self.led_t_offset = time.time()
        elif self.state == uiState.LED_SLCT:
            if self.ledEffectNum == ledState.WW:
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
        elif self.state == uiState.STBY:
            self.standby = True
            self._stby_callback()
            self.update()
        elif self.state == uiState.ALM:
            self.standby = True
            self._stby_callback()
            self.ledStripe.cold_white()
            self.state = uiState.LED
            self.auto_stby = True
    def back(self):
        if self._stby_check():
            return
        if self.state == uiState.LED_SLCT:
            self.state = uiState.LED
            self.update()
    
    def alarm(self):
        self._stby_check()
        self.state = uiState.ALM
        self.auto_stby = False
    
    def update(self):
        # auto standby
        if self.auto_stby:
            if time.time() - self.last_click > 10:
                if not self.standby:
                    self._stby_callback()
        
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
        elif self.state == uiState.WETH:
            self.weth_ui()
        elif self.state == uiState.CLCK:
            self.clck_ui()
        elif self.state == uiState.STBY:
            self.stby_ui()
        elif self.state == uiState.ALM:
            self.alarm_ui()
        
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
        m = u64images.add_navbar(u64images.led_text + u64images.nothing1 + self.ledStripe.effects.current_8px_rgb(2) + u64images.nothing1, *NavOpts.led)
        m = clean_convert_matrix(m)
        u64led.set_matrix(m)

    def led_slct_ui(self):
        m = None
        p = None
        if self.ledEffectNum == ledState.WW:
            p = self.ledStripe.effects.preview_effect_8px(self.led_t_offset, 2, self.ledStripe.warm_white)
        elif self.ledEffectNum == ledState.W:
            p = self.ledStripe.effects.preview_effect_8px(self.led_t_offset, 2, self.ledStripe.white)
        elif self.ledEffectNum == ledState.CW:
            p = self.ledStripe.effects.preview_effect_8px(self.led_t_offset, 2, self.ledStripe.cold_white)
        elif self.ledEffectNum == ledState.BLACK:
            p = self.ledStripe.effects.preview_effect_8px(self.led_t_offset, 2, self.ledStripe.black)
        elif self.ledEffectNum == ledState.RGB:
            p = self.ledStripe.effects.preview_effect_8px(self.led_t_offset, 2, self.ledStripe.rgb_cycle)
        elif self.ledEffectNum == ledState.ARGB:
            p = self.ledStripe.effects.preview_effect_8px(self.led_t_offset, 2, self.ledStripe.argb_cycle)
        else:
            print("error: invalid ledEffectNum")
        
        m = copy.deepcopy(u64images.add_navbar(copy.deepcopy(u64images.nothing3) + p + u64images.nothing1 + u64images.nothing3, *NavOpts.led_slct)) # type: ignore
        m = clean_convert_matrix(m)
        m[0][self.ledEffectNum + 1] = (0, 128, 0) # type: ignore
        u64led.set_matrix(m)
    
    def alarm_ui(self):
        m = u64images.add_navbar(u64images.blank_white, *NavOpts.alm)
        u64led.set_matrix(m)
    def weth_ui(self):
        m = u64images.add_navbar(u64images.number_to_matrix(-1), *NavOpts.weth)
        u64led.set_matrix(m)

    def clck_ui(self):
        u64led.set_matrix(u64images.add_navbar(clock.gen_matrix(), *NavOpts.clck))


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