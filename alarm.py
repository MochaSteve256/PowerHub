import schedule
import time

from helpers import psu
import led_manager
import ui_manager

class Alarm():
    led = None
    ui = None

    # Actions map to callables
    actions = {
        "sunrise": lambda self: self._sunrise(),
        "schoolPowerOff": lambda self: self._schoolPowerOff(),
        "warmWhite": lambda self: self._warmWhite(),
        "alarm": lambda self: self._alarm(),
        "coldWhite": lambda self: self.led.cold_white(),  # type: ignore
        "sunset": lambda self: self.led.sunset(),  # type: ignore
        "psuOff": lambda self: psu.off(),
    }

    # Default schedules
    default_schedule = [
        {"name": "sunrise", "action": "sunrise", "repeat": "daily", "time": "07:00", "enabled": True},
        {"name": "alarm", "action": "alarm", "repeat": "daily", "time": "07:01", "enabled": True},
        {"name": "coldWhite", "action": "coldWhite", "repeat": "daily", "time": "07:02", "enabled": True},
        {"name": "schoolPowerOff", "action": "schoolPowerOff", "repeat": "daily", "time": "07:45", "enabled": True},
        {"name": "psuOffSchool", "action": "psuOff", "repeat": "daily", "time": "07:50", "enabled": True},
        {"name": "warmWhite", "action": "warmWhite", "repeat": "daily", "time": "22:00", "enabled": True},
        {"name": "sunset", "action": "sunset", "repeat": "daily", "time": "23:00", "enabled": True},
        {"name": "psuOffSunset", "action": "psuOff", "repeat": "daily", "time": "23:05", "enabled": True},
    ]

    def __init__(self, led: led_manager.LED_Stripe, ui: ui_manager.UI) -> None:
        self.led = led
        self.ui = ui
        self.schedule = self.default_schedule.copy()
        self.update_times()

    def _sunrise(self):
        if not psu.is_on():
            psu.on()
        self.led.sunrise()  # type: ignore

    def _schoolPowerOff(self):
        self.led.black()  # type: ignore

    def _warmWhite(self):
        if not psu.is_on():
            psu.on()
        self.led.warm_white()  # type: ignore

    def _alarm(self):
        self.led.alarm()  # type: ignore
        self.ui.alarm()  # type: ignore

    def add_schedule(self, name: str, action: str, repeat: str, time: str, enabled: bool = True):
        self.schedule.append({"name": name, "action": action, "repeat": repeat, "time": time, "enabled": enabled})
        self.update_times()

    def remove_schedule(self, name: str):
        self.schedule = [s for s in self.schedule if s["name"] != name]
        self.update_times()

    def enable_schedule(self, name: str):
        for s in self.schedule:
            if s["name"] == name:
                s["enabled"] = True
        self.update_times()

    def disable_schedule(self, name: str):
        for s in self.schedule:
            if s["name"] == name:
                s["enabled"] = False
        self.update_times()

    def update_times(self):
        schedule.clear()
        for entry in self.schedule:
            if not entry["enabled"]:
                continue

            action_callable = self.actions.get(entry["action"], None)
            if action_callable:
                days = entry["repeat"]
                time = entry["time"]

                if days == "daily":
                    schedule.every().day.at(time).do(action_callable, self)
                else:
                    day_map = {
                        "mo": schedule.every().monday,
                        "tu": schedule.every().tuesday,
                        "we": schedule.every().wednesday,
                        "th": schedule.every().thursday,
                        "fr": schedule.every().friday,
                        "sa": schedule.every().saturday,
                        "su": schedule.every().sunday,
                    }

                    for i in range(0, len(days), 2):
                        day_code = days[i:i+2]
                        if day_code in day_map:
                            day_map[day_code].at(time).do(action_callable, self)

    def update(self):
        schedule.run_pending()
