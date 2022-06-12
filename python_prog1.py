import requests
import json
api_key="7106a13a8eae3fb9f9c1f9b606fc816b"
lat=33.44
lon=-94.04
base_url2=f'http://api.openweathermap.org/data/2.5/onecall?lat=33.44&lon=-94.04&exclude=hourly,daily,minutely,alerts&appid={api_key}'
#base_url = "http://api.openweathermap.org/data/3.0/onecall?"
#complete_url = base_url + "appid=" + api_key + "&q=" + city_name
#url = f'https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={api_key}&units=metric'
response=requests.get(base_url2)
x=response.json()
if response.status_code != "404":
    y=x["current"]
    for p in y:
        print(p,'----------->',y[p])
else:
    print(" Not a valid input ")
