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
            color = flask.request.json["color"] # type: ignore
            if color and isinstance(color, list) and len(color) == 3:
                led.new_color(color)
            else:
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
            print(flask.request.json)
            return "Invalid target", 400
        return "OK", 200

    return "Hello World!"

@app.route('/alarm', methods=['GET', 'POST'])  # type: ignore
@app.route('/alarm/<schedule_id>', methods=['GET', 'DELETE', 'PATCH', 'PUT'])  # type: ignore
def alarm_api(schedule_id=None):
    # Check authentication
    if not api_auth_check(flask.request):  # type: ignore
        return "Unauthorized", 401

    # Handle GET request: List all schedules or get specific schedule
    if flask.request.method == "GET":
        if schedule_id:
            # Get specific schedule by ID
            schedule = alarmManager.get_schedule(schedule_id)
            if not schedule:
                return "Schedule not found", 404
            return {"schedule": schedule}, 200
        else:
            # Get all schedules
            return {
                "schedules": alarmManager.get_all_schedules()
            }, 200

    # Handle POST request: Add a new schedule
    elif flask.request.method == "POST":
        if schedule_id:
            return "Method not allowed for specific schedule ID", 405
            
        data = flask.request.json  # type: ignore
        if not all(key in data for key in ["name", "action", "repeat", "time"]): # type: ignore
            return "Missing required fields: name, action, repeat, time", 400

        # enabled is optional, defaults to True
        enabled = data.get("enabled", True) # type: ignore

        new_id = alarmManager.add_schedule(
            name=data["name"], # type: ignore
            action=data["action"], # type: ignore
            repeat=data["repeat"], # type: ignore
            time=data["time"], # type: ignore
            enabled=enabled,
        )
        return {"message": "Schedule added", "id": new_id}, 201

    # Handle DELETE request: Remove a schedule by ID
    elif flask.request.method == "DELETE":
        if not schedule_id:
            return "Schedule ID required for deletion", 400

        success = alarmManager.remove_schedule(schedule_id)
        if not success:
            return "Schedule not found", 404
        return "Schedule removed", 200

    # Handle PATCH request: Partially update a schedule (enable/disable or edit specific fields)
    elif flask.request.method == "PATCH":
        if not schedule_id:
            return "Schedule ID required for update", 400

        data = flask.request.json  # type: ignore
        if not data: # type: ignore
            return "Request body required", 400

        # Check if schedule exists
        if not alarmManager.get_schedule(schedule_id):
            return "Schedule not found", 404

        # Handle simple enable/disable (backward compatibility)
        if "enabled" in data and len(data) == 1: # type: ignore
            if data["enabled"]: # type: ignore
                success = alarmManager.enable_schedule(schedule_id)
            else:
                success = alarmManager.disable_schedule(schedule_id)
            
            if success:
                return "Schedule updated", 200
            else:
                return "Schedule not found", 404
        
        # Handle partial update of any fields
        success = alarmManager.edit_schedule(
            schedule_id=schedule_id,
            name=data.get("name"), # type: ignore
            action=data.get("action"), # type: ignore
            repeat=data.get("repeat"), # type: ignore
            time=data.get("time"), # type: ignore
            enabled=data.get("enabled") # type: ignore
        )
        
        if success:
            return "Schedule updated", 200
        else:
            return "Schedule not found", 404

    # Handle PUT request: Complete replacement of a schedule
    elif flask.request.method == "PUT":
        if not schedule_id:
            return "Schedule ID required for replacement", 400

        data = flask.request.json  # type: ignore
        if not all(key in data for key in ["name", "action", "repeat", "time"]): # type: ignore
            return "Missing required fields: name, action, repeat, time", 400

        # Check if schedule exists
        if not alarmManager.get_schedule(schedule_id):
            return "Schedule not found", 404

        # enabled is optional, defaults to True
        enabled = data.get("enabled", True) # type: ignore

        success = alarmManager.edit_schedule(
            schedule_id=schedule_id,
            name=data["name"], # type: ignore
            action=data["action"], # type: ignore
            repeat=data["repeat"], # type: ignore
            time=data["time"], # type: ignore
            enabled=enabled
        )
        
        if success:
            return "Schedule replaced", 200
        else:
            return "Schedule not found", 404

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
    
    target_dim = 0.0
    def led_update():
        global target_dim
        target_dim += (dim_factor - target_dim) * 0.1
        led.update(target_dim)
    
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