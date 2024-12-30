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
        bg_thread = threading.Thread(target=self._background_task)
        bg_thread.start()
        self._update()
        watchpoints.watch(self.standby)
    
    def _background_task(self):
        while True:
            if time.time() - self.last_click > 10:
                if not self.standby:
                    self.standby = True
                    self._update()
            time.sleep(1)
    
    def _stby_check(self):
        self.last_click = time.time()
        if self.standby:
            self.standby = False
            self._update()
            return True
        return False
    
    def _stby_task(self):
        while True:
            while self.standby:
                if not self._nighttime_check():
                    self.state = UIState.CLCK
                    self._update()
                    time.sleep(10)
                    if not self.standby:
                        break
                    self.state = UIState.WETH
                    self._update()
                    time.sleep(10)
                else:
                    self.state = UIState.CLCK
                    self._update()
                    time.sleep(60)

    def _nighttime_check(self):
        if datetime.datetime.now().hour < 6 or datetime.datetime.now().hour > 22:
            return True
        return False
    
    def clockwise(self):
        if self._stby_check():
            return
        if self.state == UIState.PSU:
            self.state = UIState.LED
            self._update()
        elif self.state == UIState.LED:
            self.state = UIState.CLCK
            self._update()
        elif self.state == UIState.LED_SLCT:
            pass#TODO
        elif self.state == UIState.WETH:
            self.state = UIState.STBY
            self._update()
        elif self.state == UIState.CLCK:
            self.state = UIState.WETH
            self._update()
        elif self.state == UIState.STBY:
            self.state = UIState.PSU
            self._update()
    def counterclockwise(self):
        if self._stby_check():
            return
        if self.state == UIState.PSU:
            self.state = UIState.STBY
            self._update()
        elif self.state == UIState.LED:
            self.state = UIState.PSU
            self._update()
        elif self.state == UIState.LED_SLCT:
            pass#TODO
        elif self.state == UIState.WETH:
            self.state = UIState.CLCK
            self._update()
        elif self.state == UIState.CLCK:
            self.state = UIState.LED
            self._update()
        elif self.state == UIState.STBY:
            self.state = UIState.WETH
            self._update()
    def select(self):
        if self._stby_check():
            return
        if self.state == UIState.PSU:
            if psu.is_on():
                psu.off()
                self._update()
            else:
                psu.on()
                self._update()
        elif self.state == UIState.LED:
            self.state = UIState.LED_SLCT
            self._update()
        elif self.state == UIState.LED_SLCT:
            led_stripe.set_all((0, 0, 0))#TODO
            self.state = UIState.LED
            self._update()
        elif self.state == UIState.STBY:
            self.standby = not self.standby
            self._update()
    def back(self):
        if self._stby_check():
            return
        if self.state == UIState.LED_SLCT:
            self.state = UIState.LED
            self._update()
    
    def _update(self):
        print("ui update")
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
        
        if self.standby:
            matrix = u64led.get_matrix()
            for i in range(8):
                for j in range(8):
                    for k in range(3):
                        matrix[i][j][k] = matrix[i][j][k] // 5
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
