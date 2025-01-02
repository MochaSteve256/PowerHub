from typing import Callable, Tuple, Union, Optional
import time
import datetime
from typing import Callable

from helpers import u64led
from helpers import u64images
from helpers import psu
import led_manager


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
    
    def __init__(self, ledStripe:led_manager.LED_Stripe):
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
            else:
                func = self.translate_led(self.ledEffectNum)
                # Case 1: func is a tuple (Callable + target_color)
                if isinstance(func, tuple):
                    callabl, target_color = func  # Unpack the tuple safely
                    if callable(callabl):
                        callabl(target_color)  # Pass target_color (even if it's None)
                    else:
                        print("Error: Expected a callable in the tuple, got", type(callabl))

                # Case 2: func is directly callable (like warm_white)
                elif callable(func):
                    func()

                # Case 3: func is None
                elif func is None:
                    print("translate_led returned None")

                # Case 4: Unexpected type (should never happen if the types are correct)
                else:
                    print("Unexpected return type:", type(func))
                self.state = uiState.LED
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
                divider = 2.5
            matrix = u64led.get_matrix()
            for i in range(8):
                for j in range(8):
                    for k in range(3):
                        matrix[i][j][k] = int(matrix[i][j][k] / divider)
            u64led.set_matrix(matrix)
        
        u64led.show_matrix()

    def psu_ui(self):
        if psu.is_on():
            u64led.set_matrix(u64images.add_navbar(u64images.psu_text + u64images.psu_on, *NavOpts.psu))
        else:
            u64led.set_matrix(u64images.add_navbar(u64images.psu_text + u64images.psu_off, *NavOpts.psu))

    def led_ui(self):
        u64led.set_matrix(u64images.add_navbar(u64images.led_text + u64images.nothing1 + self.ledStripe.effects.current_8px_rgb() + u64images.nothing1, *NavOpts.led_slct))

    def led_slct_ui(self):
        if self.ledEffectNum == 0:
            u64led.set_matrix(u64images.add_navbar(u64images.nothing3 + self.ledStripe.effects.preview_effect_8px(time.time() - self.led_t_offset, self.ledEffectNum, target_color=self.led_target_color) + u64images.nothing3 + u64images.nothing1, *NavOpts.led_slct))
        else:
            u64led.set_matrix(u64images.add_navbar(u64images.nothing3 + self.ledStripe.effects.preview_effect_8px(time.time() - self.led_t_offset, self.ledEffectNum) + u64images.nothing3 + u64images.nothing1, *NavOpts.led_slct))

    def weth_ui(self):
        u64led.set_matrix(u64images.add_navbar(u64images.blank, *NavOpts.weth))#TODO

    def clck_ui(self):
        u64led.set_matrix(u64images.add_navbar(u64images.blank, *NavOpts.clck))#TODO

    def stby_ui(self):
        u64led.set_matrix(u64images.add_navbar(u64images.stby_text + u64images.nothing3, *NavOpts.stby))

    def translate_led(self, effectNum, target_color: Optional[Tuple[int, int, int]] = None) -> Union[
    Callable[[], None],  # Functions with no arguments
    Tuple[Callable[[Optional[Tuple[int, int, int]]], None], Optional[Tuple[int, int, int]]],
    None
]:
        if effectNum == ledState.WW:
            return self.ledStripe.warm_white
        elif effectNum == ledState.W:
            return self.ledStripe.white
        elif effectNum == ledState.CW:
            return self.ledStripe.cold_white
        elif effectNum == ledState.BLACK:
            return self.ledStripe.new_color, (0, 0, 0)
        elif effectNum == ledState.RGB:
            return self.ledStripe.rgb_cycle
        elif effectNum == ledState.ARGB:
            return self.ledStripe.argb_cycle
        elif effectNum == ledState.CUSTOM:
            return self.ledStripe.new_color, target_color
        else:
            print("invalid effectNum: " + str(effectNum))
            return None