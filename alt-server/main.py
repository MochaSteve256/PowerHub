import weather
import time
import json
import schedule
import requests

def call_weather_update():
    print("Updating weather...")
    url = "http://stevepi.local:5000/weather"
    
    current_weather = weather.get_current_weather()
    morning_weather = weather.get_morning_forecast()
    
    data = dict(
        temp_current = current_weather[1], # type: ignore
        cond_current = current_weather[0], # type: ignore
        temp_tomorrow = morning_weather[1], # type: ignore
        cond_tomorrow = morning_weather[0] # type: ignore
    )
    
    r = requests.post(url, data=json.dumps(data), headers={'Content-Type': 'application/json', 'token':'br4d9c2ayqrk7iswse7v8t2x'})
    print(r.text)

if __name__ == "__main__":
    schedule.every(10).minutes.do(call_weather_update)
    
    call_weather_update()
    
    while True:
        schedule.run_pending()
        time.sleep(60)