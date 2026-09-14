import pandas as pd
import requests

df = pd.read_csv("./data/bronze/ma.csv")
for row in df.itertuples(index=False):
    data = ""
    params ={
        "latitude" : row.lat,
        "longitude" : row.lng,
        "daily" : "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "timezone" : "auto"
    }
    url = "https://api.open-meteo.com/v1/forecast"
    try :
        response = requests.get(url,params=params,timeout=5)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.Timeout:
        print("Request took too long")
    except requests.exceptions.HTTPError as e:
        print("HTTP error:", e)
    except requests.exceptions.RequestException as e:
        print("Request error:", e)

    with open("./data/bronze/raw_data.json", "a") as file:
        file.write(data)

