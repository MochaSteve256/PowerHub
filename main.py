import threading
import time


import flask

from helpers import ky040
import ui_manager
import led_manager
import alarm


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

def api_auth_check(token):
    print("Unauthorized request, token: ", token)
    if token == "br4d9c2ayqrk7iswse7v8t2x":
        return True
    return False

app = flask.Flask(__name__)

@app.route('/')
def index_api():
    return "Hello World!"

@app.route('/psu', methods=['GET', 'POST'])
def psu_api():
    # check auth
    if not api_auth_check(flask.request.json["token"]):
        return "Unauthorized", 401
    # get
    

    # post


    return "Hello World!"

@app.route('/led', methods=['GET', 'POST'])
def led_api():
    # check auth
    if not api_auth_check(flask.request.json["token"]):
        return "Unauthorized", 401
    # get


    # post
    

    return "Hello World!"

@app.route('/alarm', methods=['GET', 'POST'])
def alarm_api():
    # check auth
    if not api_auth_check(flask.request.json["token"]):
        return "Unauthorized", 401
    # get


    # post
    

    return "Hello World!"

@app.route('/weather', methods=['POST'])
def weather_api():
    # check auth
    if not api_auth_check(flask.request.json["token"]):
        return "Unauthorized", 401

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