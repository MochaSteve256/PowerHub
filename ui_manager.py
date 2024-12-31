from helpers import u64led
from helpers import u64images

from helpers import psu
from helpers import led_stripe

import time
import datetime
import threading
import watchpoints

class UIState():
    PSU = 0
    LED = 1
    LED_SLCT = 2
    WETH = 3
    CLCK = 4
    STBY = 5


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
    def __init__(self):
        self.state = UIState.PSU
        self.last_click = time.time()
        self.update()
        watchpoints.watch(self.standby, callback=self._stby_callback, when=lambda x: x == True)

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
        if self.state == UIState.PSU:
            self.state = UIState.LED
            self.update()
        elif self.state == UIState.LED:
            self.state = UIState.CLCK
            self.update()
        elif self.state == UIState.LED_SLCT:
            pass#TODO
        elif self.state == UIState.WETH:
            self.state = UIState.STBY
            self.update()
        elif self.state == UIState.CLCK:
            self.state = UIState.WETH
            self.update()
        elif self.state == UIState.STBY:
            self.state = UIState.PSU
            self.update()
    def counterclockwise(self):
        if self._stby_check():
            return
        if self.state == UIState.PSU:
            self.state = UIState.STBY
            self.update()
        elif self.state == UIState.LED:
            self.state = UIState.PSU
            self.update()
        elif self.state == UIState.LED_SLCT:
            pass#TODO
        elif self.state == UIState.WETH:
            self.state = UIState.CLCK
            self.update()
        elif self.state == UIState.CLCK:
            self.state = UIState.LED
            self.update()
        elif self.state == UIState.STBY:
            self.state = UIState.WETH
            self.update()
    def select(self):
        if self._stby_check():
            return
        if self.state == UIState.PSU:
            if psu.is_on():
                psu.off()
                self.update()
            else:
                psu.on()
                self.update()
        elif self.state == UIState.LED:
            self.state = UIState.LED_SLCT
            self.update()
        elif self.state == UIState.LED_SLCT:
            led_stripe.set_all((0, 0, 0))#TODO
            self.state = UIState.LED
            self.update()
        elif self.state == UIState.STBY:
            self.standby = not self.standby
            self.update()
    def back(self):
        if self._stby_check():
            return
        if self.state == UIState.LED_SLCT:
            self.state = UIState.LED
            self.update()
    
    def update(self):
        # auto standby
        if time.time() - self.last_click > 10:
            if not self.standby:
                self.standby = True
        
        # standby logic
        if self.standby:
            if not self._nighttime_check():
                if time.time() - self._last_standby_switch > 10:
                    self.state = UIState.CLCK
                elif time.time() - self._last_standby_switch > 20:
                    self.state = UIState.WETH
                    self._last_standby_switch = time.time()
            else:
                if time.time() - self._last_standby_switch > 60:
                    self.state = UIState.CLCK
                    self._last_standby_switch = time.time()
        
        # ui functions
        if self.state == UIState.PSU:
            psu_ui()
        elif self.state == UIState.LED:
            led_ui()
        elif self.state == UIState.LED_SLCT:
            led_slct_ui()
        elif self.state == UIState.WETH:
            weth_ui()
        elif self.state == UIState.CLCK:
            clck_ui()
        elif self.state == UIState.STBY:
            stby_ui()
        
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
                        matrix[i][j][k] = matrix[i][j][k] // divider
            u64led.set_matrix(matrix)
        
        u64led.show_matrix()

def psu_ui():
    if psu.is_on():
        u64led.set_matrix(u64images.add_navbar(u64images.psu_text + u64images.psu_on, *NavOpts.psu))
    else:
        u64led.set_matrix(u64images.add_navbar(u64images.psu_text + u64images.psu_off, *NavOpts.psu))

def led_ui():
    u64led.set_matrix(u64images.add_navbar(u64images.led_text + u64images.nothing, *NavOpts.led))

def led_slct_ui():
    u64led.set_matrix(u64images.add_navbar(u64images.blank, *NavOpts.led_slct))#TODO

def weth_ui():
    u64led.set_matrix(u64images.add_navbar(u64images.blank, *NavOpts.weth))#TODO

def clck_ui():
    u64led.set_matrix(u64images.add_navbar(u64images.blank, *NavOpts.clck))#TODO

def stby_ui():
    u64led.set_matrix(u64images.add_navbar(u64images.stby_text + u64images.nothing, *NavOpts.stby))
