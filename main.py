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
            status = led.effects.LedState.current
        ), 200

    # post
    elif flask.request.method == "POST":
        if flask.request.json["target"] == "SUNRISE": # type: ignore
            led.sunrise()
        elif flask.request.json["target"] == "SUNSET": # type: ignore
            led.sunset()
        elif flask.request.json["target"] == "ALARM": # type: ignore
            led.alarm()
        elif flask.request.json["target"] == "STATIC_COLOR": # type: ignore
            led.new_color(flask.request.json["color"]) # type: ignore
        elif flask.request.json["target"] == "WARM_WHITE": # type: ignore
            led.warm_white()
        elif flask.request.json["target"] == "COLD_WHITE": # type: ignore
            led.cold_white()
        elif flask.request.json["target"] == "WHITE": # type: ignore
            led.white()
        elif flask.request.json["target"] == "BLACK": # type: ignore
            led.black()
        elif flask.request.json["target"] == "RGB_CYCLE": # type: ignore
            led.rgb_cycle()
        elif flask.request.json["target"] == "ARGB_CYCLE": # type: ignore
            led.argb_cycle()
        return "OK", 200

    return "Hello World!"

@app.route('/alarm', methods=['GET', 'POST']) # type: ignore
def alarm_api():
    # check auth
    if not api_auth_check(flask.request): # type: ignore
        return "Unauthorized", 401
    # get
    if flask.request.method == "GET":
        return dict(
            sunrise = alarmManager.sunriseTime,
            alarm = alarmManager.alarmTime,
            cw = alarmManager.cwTime,
            schoolPowerOff = alarmManager.schoolPowerOffTime,
            schoolPsuOff = alarmManager.schoolPsuOffTime,
            ww = alarmManager.wwTime,
            sunset = alarmManager.sunsetTime,
            sunsetPsuOff = alarmManager.sunsetPsuOffTime
        ), 200

    # post
    elif flask.request.method == "POST":
        alarmManager.sunriseTime = flask.request.json["sunrise"] # type: ignore
        alarmManager.alarmTime = flask.request.json["alarm"] # type: ignore
        alarmManager.cwTime = flask.request.json["cw"] # type: ignore
        alarmManager.schoolPowerOffTime = flask.request.json["schoolPowerOff"] # type: ignore
        alarmManager.schoolPsuOffTime = flask.request.json["schoolPsuOff"] # type: ignore
        alarmManager.wwTime = flask.request.json["ww"] # type: ignore
        alarmManager.sunsetTime = flask.request.json["sunset"] # type: ignore
        alarmManager.sunsetPsuOffTime = flask.request.json["sunsetPsuOff"] # type: ignore

        alarmManager.update_times()
        return "OK", 200
    
    return 400

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
            led.update()
            time.sleep(.01)
    
    try:
        #ledUT = threading.Thread(target=led_update)
        #ledUT.start()
        while True:
            ky040.update()
            ui.update()
            led.update()
            alarmManager.update()
            time.sleep(.01)#!

    finally:
        ky040.stop()