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


def api_auth_check(token):
    if token == "br4d9c2ayqrk7iswse7v8t2x":
        return True
    return False

app = flask.Flask(__name__)

@app.route('/')
def index_api():
    return "Hello World!"

@app.route('/psu')
def psu_api():
    # check auth

    # get
    

    # post


    return "Hello World!"

@app.route('/led')
def led_api():
    # check auth
    
    # get


    # post
    

    return "Hello World!"

@app.route('/alarm')
def alarm_api():
    # check auth
    
    # get


    # post
    

    return "Hello World!"

@app.route('/weather')
def weather_api():
    # check auth
    
    # post


    return "Hello World!"


if __name__ == "__main__":
    
    led = led_manager.LED_Stripe()
    ui = ui_manager.UI(led)
    ky040 = ky040.KY040(ui.clockwise, ui.counterclockwise, press, release)
    alarmManager = alarm.Alarm(led)
    
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

    finally:
        ky040.stop()