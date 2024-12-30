from helpers import u64led
from helpers import u64images

from helpers import psu
from helpers import led_stripe

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
    state = UIState.PSU
    standby = False
    
    def __init__(self):
        self.state = UIState.PSU
        self._update()
    
    def clockwise(self):
        if self.standby:
            self.standby = False
            return
        if self.state == UIState.PSU:
            self.state = UIState.LED
            self._update()
        elif self.state == UIState.LED:
            self.state = UIState.WETH
            self._update()
        elif self.state == UIState.LED_SLCT:
            pass#TODO
        elif self.state == UIState.WETH:
            self.state = UIState.CLCK
            self._update()
        elif self.state == UIState.CLCK:
            self.state = UIState.STBY
            self._update()
        elif self.state == UIState.STBY:
            self.state = UIState.PSU
            self._update()
    def counterclockwise(self):
        if self.standby:
            self.standby = False
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
            self.state = UIState.LED
            self._update()
        elif self.state == UIState.CLCK:
            self.state = UIState.WETH
            self._update()
        elif self.state == UIState.STBY:
            self.state = UIState.CLCK
            self._update()
    def select(self):
        if self.standby:
            self.standby = False
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
    def back(self):
        if self.state == UIState.LED_SLCT:
            self.state = UIState.LED
            self._update()
    
    def _update(self):
        if self.state == UIState.PSU:
            if psu.is_on():
                u64led.set_matrix(u64images.add_navbar(u64images.psu_text + u64images.psu_on, *NavOpts.psu))
            else:
                u64led.set_matrix(u64images.add_navbar(u64images.psu_text + u64images.psu_off, *NavOpts.psu))
        elif self.state == UIState.LED:
            u64led.set_matrix(u64images.add_navbar(u64images.led_text + u64images.nothing, *NavOpts.led))
        elif self.state == UIState.LED_SLCT:
            u64led.set_matrix(u64images.add_navbar(u64images.blank, *NavOpts.led_slct))#TODO
        elif self.state == UIState.WETH:
            u64led.set_matrix(u64images.add_navbar(u64images.blank, *NavOpts.weth))#TODO
        elif self.state == UIState.CLCK:
            u64led.set_matrix(u64images.add_navbar(u64images.blank, *NavOpts.clck))#TODO
        elif self.state == UIState.STBY:
            u64led.set_matrix(u64images.add_navbar(u64images.stby_text + u64images.nothing, *NavOpts.stby))
        
        if self.standby:
            matrix = u64led.get_matrix()
            for i in range(8):
                for j in range(8):
                    for k in range(3):
                        matrix[i][j][k] = matrix[i][j][k] // 3
            u64led.set_matrix(matrix)