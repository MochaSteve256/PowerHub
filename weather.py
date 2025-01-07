import requests
from pprint import pprint

url = "https://api.brightsky.dev/current_weather"

params = dict(
    lat=53.552671,
    lon=9.910797
)

resp = requests.get(url=url, params=params)
data = resp.json()

pprint(data)
