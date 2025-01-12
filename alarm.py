import schedule
import time

from helpers import psu
import led_manager
import ui_manager

class Alarm():
    led = None
    ui = None
    
    sunriseTime = "07:00"
    alarmTime = "07:01"
    cwTime = "07:02"
    schoolPowerOffTime = "07:45"
    schoolPsuOffTime = "07:50"
    wwTime = "22:00"
    sunsetTime = "23:00"
    sunsetPsuOffTime = "23:05"

    
    def _sunrise(self):
        if not psu.is_on():
            psu.on()
        
        self.led.sunrise()# type: ignore
        
    def _schoolPowerOff(self):
        self.led.black()# type: ignore
    
    def _warmWhite(self):
        if not psu.is_on():
            psu.on()
        
        self.led.warm_white()# type: ignore
    
    def _alarm(self):
        self.led.alarm()# type: ignore
        self.ui.alarm()# type: ignore
    
    def update_times(self):
        schedule.clear()
        
        schedule.every().day.at(self.sunriseTime).do(self._sunrise)
        schedule.every().day.at(self.alarmTime).do(self._alarm)
        schedule.every().day.at(self.cwTime).do(self.led.cold_white) # type: ignore
        schedule.every().day.at(self.schoolPowerOffTime).do(self._schoolPowerOff)
        schedule.every().day.at(self.schoolPsuOffTime).do(psu.off)
        schedule.every().day.at(self.wwTime).do(self._warmWhite)
        schedule.every().day.at(self.sunsetTime).do(self.led.sunset) # type: ignore
        schedule.every().day.at(self.sunsetPsuOffTime).do(psu.off)
        
    def __init__(self, led: led_manager.LED_Stripe, ui: ui_manager.UI) -> None:
        self.led = led
        self.ui = ui

        self.update_times()
    
    def update(self):
        schedule.run_pending()

