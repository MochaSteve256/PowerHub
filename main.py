import threading
import time

import flask

from helpers import ky040
import ui_manager
import led_manager
import alarm
from helpers import psu


press_time = 0
release_time = 0
    
def press():
    global press_time
    press_time = time.time()

def release():
    global press_time, release_time
    release_time = time.time()
    if release_time - press_time < 0.5:
        ui.select()
    else:
        ui.back()

# weather state
class WeatherState:
    temp_current = 0
    cond_current = "cloudy"
    temp_tomorrow = 0
    cond_tomorrow = "cloudy"

weather = WeatherState()

dim_factor = 1

def api_auth_check(req):
    token = req.headers.get("token")
    if token == "br4d9c2ayqrk7iswse7v8t2x":
        print("Authorized")
        return True
    print("Unauthorized request, token: ", token)
    return False

app = flask.Flask(__name__)

@app.route('/')
def index_api():
    return "Hello World!", 200

@app.route('/dim', methods=['GET', 'POST'])
def dim_api():
    global dim_factor
    # check auth
    if not api_auth_check(flask.request): # type: ignore
        return "Unauthorized", 401
    # get
    if flask.request.method == "GET":
        return dict(
            dim = dim_factor
        ), 200

    # post
    elif flask.request.method == "POST":
        dim_factor = flask.request.json["dim"] # type: ignore
        return "OK", 200
    
    return "retard", 400

@app.route('/psu', methods=['GET', 'POST'])# type: ignore
def psu_api():
    # check auth
    if not api_auth_check(flask.request): # type: ignore
        return "Unauthorized", 401
    # get
    if flask.request.method == "GET":
        return dict(
            is_on = psu.is_on()
        ), 200

    # post
    elif flask.request.method == "POST":
        if flask.request.json["is_on"]: # type: ignore
            psu.on()
        else:
            psu.off()
        return "OK", 200



@app.route('/led', methods=['GET', 'POST'])
def led_api():
    # check auth
    if not api_auth_check(flask.request): # type: ignore
        return "Unauthorized", 401
    # get
    if flask.request.method == "GET":
        return dict(
            status = led.effects.LedState.current,
            color = led.effects.target_color_save,
            transitioning_color = led.effects.target_color
        ), 200

    # post
    elif flask.request.method == "POST":
        if flask.request.json["target"] == "SUNRISE": # type: ignore
            led.sunrise()
        elif flask.request.json["target"] == "SUNSET": # type: ignore
            led.sunset()
        elif flask.request.json["target"] == "ALARM": # type: ignore
            led.alarm()
        elif flask.request.json["target"] == "CUSTOM": # type: ignore
            if "color" in flask.request.json: # type: ignore
                if len(flask.request.json["color"]) == 3: # type: ignore
                    led.new_color(flask.request.json["color"]) # type: ignore
            return "Invalid color", 400
        elif flask.request.json["target"] == "WARM_WHITE": # type: ignore
            led.warm_white()
        elif flask.request.json["target"] == "COLD_WHITE": # type: ignore
            led.cold_white()
        elif flask.request.json["target"] == "WHITE": # type: ignore
            led.white()
        elif flask.request.json["target"] == "BLACK": # type: ignore
            led.black()
        elif flask.request.json["target"] == "RGB": # type: ignore
            led.rgb_cycle()
        elif flask.request.json["target"] == "ARGB": # type: ignore
            led.argb_cycle()
        else:
            return "Invalid target", 400
        return "OK", 200

    return "Hello World!"

@app.route('/alarm', methods=['GET', 'POST', 'DELETE', 'PATCH'])  # type: ignore
def alarm_api():
    # Check authentication
    if not api_auth_check(flask.request):  # type: ignore
        return "Unauthorized", 401

    # Handle GET request: List all schedules
    if flask.request.method == "GET":
        return {
            "schedules": [
                {
                    "name": entry["name"],
                    "action": entry["action"],
                    "repeat": entry["repeat"],
                    "time": entry["time"],
                    "enabled": entry["enabled"],
                }
                for entry in alarmManager.schedule_entries
            ]
        }, 200

    # Handle POST request: Add a new schedule
    elif flask.request.method == "POST":
        data = flask.request.json  # type: ignore
        if not all(key in data for key in ["name", "action", "repeat", "time", "enabled"]): # type: ignore
            return "Invalid request body", 400

        alarmManager.add_schedule(
            name=data["name"], # type: ignore
            action=data["action"], # type: ignore
            repeat=data["repeat"], # type: ignore
            time=data["time"], # type: ignore
            enabled=data["enabled"], # type: ignore
        )
        return "Schedule added", 201

    # Handle DELETE request: Remove a schedule
    elif flask.request.method == "DELETE":
        data = flask.request.json  # type: ignore
        if "name" not in data: # type: ignore
            return "Invalid request body", 400

        alarmManager.remove_schedule(data["name"]) # type: ignore
        return "Schedule removed", 200

    # Handle PATCH request: Enable/disable a schedule
    elif flask.request.method == "PATCH":
        data = flask.request.json  # type: ignore
        if not all(key in data for key in ["name", "enabled"]): # type: ignore
            return "Invalid request body", 400

        if data["enabled"]: # type: ignore
            alarmManager.enable_schedule(data["name"]) # type: ignore
        else:
            alarmManager.disable_schedule(data["name"]) # type: ignore
        return "Schedule updated", 200

    # Unsupported HTTP method
    return "Method not allowed", 405

@app.route('/alarm/actions', methods=['GET'])  # type: ignore
def alarm_actions_api():
    # Check authentication
    if not api_auth_check(flask.request):  # type: ignore
        return "Unauthorized", 401

    # Retrieve all available action keys from the alarm manager
    actions_list = list(alarmManager.actions.keys())
    return {"actions": actions_list}, 200


@app.route('/dismiss', methods=['POST'])
def dismiss_api():
    # check auth
    if not api_auth_check(flask.request): # type: ignore
        return "Unauthorized", 401
    # dismiss alarm screen
    ui.dismiss_alarm()
    
    return "OK", 200


@app.route('/weather', methods=['POST'])
def weather_api():
    # check auth
    if not api_auth_check(flask.request): # type: ignore
        return "Unauthorized", 401
    
    print(flask.request.json)

    # post
    weather.temp_current = flask.request.json["temp_current"] # type: ignore
    weather.cond_current = flask.request.json["cond_current"] # type: ignore
    weather.temp_tomorrow = flask.request.json["temp_tomorrow"] # type: ignore
    weather.cond_tomorrow = flask.request.json["cond_tomorrow"] # type: ignore

    return "OK", 200


if __name__ == "__main__":
    
    def api_thread():
        app.run(host='0.0.0.0')
    
    apiT = threading.Thread(target=api_thread)
    apiT.start()
    
    led = led_manager.LED_Stripe()
    ui = ui_manager.UI(led, weather)
    ky040 = ky040.KY040(ui.clockwise, ui.counterclockwise, press, release)
    alarmManager = alarm.Alarm(led, ui)
    
    def led_update():
        while True:
            led.update(dim_factor)
            time.sleep(.01)
    
    try:
        #ledUT = threading.Thread(target=led_update)
        #ledUT.start()
        while True:
            ky040.update()
            ui.update()
            led.update(dim_factor)
            alarmManager.update()
            time.sleep(.01)#!

    finally:
        ky040.stop()