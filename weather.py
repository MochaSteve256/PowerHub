import requests
#from pprint import pprint
from datetime import datetime, timedelta

latitude=53.552671,
longitude=9.910797

def parse_data(data):
    weather_cond = str(data["condition"])
    cloud_cover = int(data["cloud_cover"])
    temp = round(int(data["temperature"]))

    if weather_cond == "rain" or weather_cond == "snow" or weather_cond == "sleet" or weather_cond == "hail" or weather_cond == "thunderstorm":
        return "rain", temp
    elif weather_cond == "dry":
        if cloud_cover < 35:
            return "sunny", temp
        else:
            return "cloudy", temp

def get_current_weather():
    url = "https://api.brightsky.dev/current_weather"

    params = dict(
        lat = latitude,
        lon = longitude
    )

    resp = requests.get(url=url, params=params)
    data = resp.json()

    return parse_data(data["weather"])

def get_morning_forecast():
    url = "https://api.brightsky.dev/weather"
    now = datetime.now().astimezone()
    next_7_am = now.replace(hour=7, minute=0, second=0, microsecond=0)
    if now >= next_7_am:
        next_7_am += timedelta(days=1)
    timestamp = next_7_am.isoformat()
    params = dict(
        date=timestamp,
        lat = latitude,
        lon = longitude
    )

    resp =  requests.get(url=url, params=params)
    data = resp.json()

    return parse_data(data["weather"][0])

print(get_current_weather())
print(get_morning_forecast())
