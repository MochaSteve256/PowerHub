import weather
import datetime
import time
import schedule
import requests

def call_weather_update():
    url = "http://stevepi.local:5000/weather"
    
    current_weather = weather.get_current_weather()
    morning_weather = weather.get_morning_forecast()
    
    data = dict(
        temp_current = current_weather[1], # type: ignore
        cond_current = current_weather[0], # type: ignore
        temp_tomorrow = morning_weather[1], # type: ignore
        cond_tomorrow = morning_weather[0] # type: ignore
    )
    
    requests.post(url, data=data)

if __name__ == "__main__":
    schedule.every(1).hours.do(call_weather_update)
    
    while True:
        schedule.run_pending()
        time.sleep(120)