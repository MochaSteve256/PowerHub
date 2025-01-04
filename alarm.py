import time
import schedule

import led_manager

class Alarm():
    sunriseTime = "6:55"
    alarmTime = "7:00"
    cwTime = "7:02"
    schoolPowerOffTime = "7:45"
    wwTime = "22:00"
    sunsetTime = "23:00"
    
    def __init__(self, led: led_manager.LED_Stripe) -> None:
        schedule.every().day.at(self.sunriseTime).do(led.sunrise)
        schedule.every().day.at(self.alarmTime).do(led.alarm)
        schedule.every().day.at(self.cwTime).do(led.cold_white)
        schedule.every().day.at(self.schoolPowerOffTime).do(led.black)
        schedule.every().day.at(self.wwTime).do(led.warm_white)
        schedule.every().day.at(self.sunsetTime).do(led.sunset)
    
    def update(self):
        schedule.run_pending()