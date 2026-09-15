import pandas as pd
import requests
import json

df = pd.read_csv("./data/bronze/ma.csv")

url = "https://api.open-meteo.com/v1/forecast"

with open("./data/bronze/raw_data.jsonl","a") as file :
    for row in df.itertuples(index=False) :
        params = {
            "latitude": row.lat,
            "longitude": row.lng,

            "daily": ",".join([
                "weather_code",
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "precipitation_probability_max",
                "wind_speed_10m_max",
                "wind_gusts_10m_max",
            ]),

            "timezone": "auto"
        }
        try :
            response = requests.get(url,params=params,timeout=5)

            response.raise_for_status()

            data = response.json()

            record = {
                "city" : row.city,
                "latitude" : row.lat,
                "longitude" : row.lng,
                "weather" : data
            }

            file.write(json.dumps(record) + "\n")

        except requests.exceptions.Timeout :
            print(f"Timeout : {row.city} ")
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error for {row.city} : {e}")
        except requests.exceptions.RequestException as e :
            print(f"Request error for {row.city} : {e}")