import schedule
import time

from helpers import psu
import led_manager
import ui_manager

class Alarm:
    def __init__(self, led: led_manager.LED_Stripe, ui: ui_manager.UI) -> None:
        self.led = led
        self.ui = ui
        # use a separate attribute for schedule entries to keep them isolated
        self.schedule_entries = self.default_schedule.copy()
        self.update_times()

    # PSU control methods
    def _psu_on(self):
        psu.on()

    def _psu_off(self):
        psu.off()

    # LED control methods (each action does exactly one thing)
    def _sunrise(self):
        self.led.sunrise()

    def _sunset(self):
        self.led.sunset()

    def _alarm(self):
        self.led.alarm()
        self.ui.alarm()

    def _warm_white(self):
        self.led.warm_white()

    def _cold_white(self):
        self.led.cold_white()

    def _white(self):
        self.led.white()

    def _lights_off(self):
        self.led.black()

    def _rgb_cycle(self):
        self.led.rgb_cycle()

    def _argb_cycle(self):
        self.led.argb_cycle()

    def _new_color(self, color=(255, 0, 0)):
        self.led.new_color(color)

    # Actions mapping: keys are the snake_case names referenced in schedules.
    actions = {
        "psu_on": lambda self: self._psu_on(),
        "psu_off": lambda self: self._psu_off(),
        "sunrise": lambda self: self._sunrise(),
        "sunset": lambda self: self._sunset(),
        "alarm": lambda self: self._alarm(),
        "cold_white": lambda self: self._cold_white(),
        "warm_white": lambda self: self._warm_white(),
        "white": lambda self: self._white(),
        "lights_off": lambda self: self._lights_off(),
        "rgb_cycle": lambda self: self._rgb_cycle(),
        "argb_cycle": lambda self: self._argb_cycle(),
        "new_color": lambda self: self._new_color(),  # uses a default color
    }

    # Default schedules with human‐readable names (now with spaces) and action keys
    default_schedule = [
        {"name": "PSU On", "action": "psu_on", "repeat": "daily", "time": "06:55", "enabled": True},
        {"name": "Sunrise", "action": "sunrise", "repeat": "daily", "time": "07:00", "enabled": True},
        {"name": "Alarm", "action": "alarm", "repeat": "daily", "time": "07:01", "enabled": True},
        {"name": "Cold White", "action": "cold_white", "repeat": "daily", "time": "07:02", "enabled": True},
        {"name": "School Power Off", "action": "lights_off", "repeat": "daily", "time": "07:45", "enabled": True},
        {"name": "PSU Off School", "action": "psu_off", "repeat": "daily", "time": "07:50", "enabled": True},
        {"name": "Warm White", "action": "warm_white", "repeat": "daily", "time": "22:00", "enabled": True},
        {"name": "Sunset", "action": "sunset", "repeat": "daily", "time": "23:00", "enabled": True},
        {"name": "PSU Off Sunset", "action": "psu_off", "repeat": "daily", "time": "23:05", "enabled": True},
    ]

    def add_schedule(self, name: str, action: str, repeat: str, time: str, enabled: bool = True):
        self.schedule_entries.append({
            "name": name,
            "action": action,
            "repeat": repeat,
            "time": time,
            "enabled": enabled
        })
        self.update_times()

    def remove_schedule(self, name: str):
        self.schedule_entries = [s for s in self.schedule_entries if s["name"] != name]
        self.update_times()

    def enable_schedule(self, name: str):
        for s in self.schedule_entries:
            if s["name"] == name:
                s["enabled"] = True
        self.update_times()

    def disable_schedule(self, name: str):
        for s in self.schedule_entries:
            if s["name"] == name:
                s["enabled"] = False
        self.update_times()

    def update_times(self):
        # Clear previous schedules
        schedule.clear()
        for entry in self.schedule_entries:
            if not entry["enabled"]:
                continue

            action_callable = self.actions.get(entry["action"])
            if action_callable:
                repeat = entry["repeat"]
                time_str = entry["time"]
                if repeat == "daily":
                    schedule.every().day.at(time_str).do(action_callable, self)
                else:
                    # Support for specific days (e.g., "mo", "tu", etc.)
                    day_map = {
                        "mo": schedule.every().monday,
                        "tu": schedule.every().tuesday,
                        "we": schedule.every().wednesday,
                        "th": schedule.every().thursday,
                        "fr": schedule.every().friday,
                        "sa": schedule.every().saturday,
                        "su": schedule.every().sunday,
                    }
                    # assume repeat is a concatenated string of two-letter day codes
                    for i in range(0, len(repeat), 2):
                        day_code = repeat[i:i+2].lower()
                        if day_code in day_map:
                            day_map[day_code].at(time_str).do(action_callable, self)

    def update(self):
        schedule.run_pending()
