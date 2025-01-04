import time
import schedule

import led_manager

class Alarm():
    sunriseTime = "06:55"
    alarmTime = "07:00"
    cwTime = "07:02"
    schoolPowerOffTime = "07:45"
    wwTime = "22:00"
    sunsetTime = "23:00"
    
    def __init__(self, led: led_manager.LED_Stripe) -> None:
        print("sunrise")
        schedule.every().day.at(self.sunriseTime).do(led.sunrise)
        print("alarm")
        schedule.every().day.at(self.alarmTime).do(led.alarm)
        print("cw")
        schedule.every().day.at(self.cwTime).do(led.cold_white)
        print("black")
        schedule.every().day.at(self.schoolPowerOffTime).do(led.black)
        print("ww")
        schedule.every().day.at(self.wwTime).do(led.warm_white)
        print("sunset")
        schedule.every().day.at(self.sunsetTime).do(led.sunset)
    
    def update(self):
        schedule.run_pending()

