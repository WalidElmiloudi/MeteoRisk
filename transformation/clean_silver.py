import pandas as pd
import numpy as np
import json
def clean_data():
    df = pd.read_json("/opt/airflow/data/bronze/raw_data.jsonl",lines=True)

    rows = []

    for _,row in df.iterrows() :

        daily = row["weather"]["daily"]

        for i in range(len(daily["time"])) :

            rows.append({
                "city": row["city"],
                "latitude": row["latitude"],
                "longitude": row["longitude"],
                "date": daily["time"][i],
                "weather_code": daily["weather_code"][i],
                "temperature_max": daily["temperature_2m_max"][i],
                "temperature_min": daily["temperature_2m_min"][i],
                "precipitation_sum": daily["precipitation_sum"][i],
                "precipitation_probability": daily["precipitation_probability_max"][i],
                "wind_speed_max": daily["wind_speed_10m_max"][i],
                "wind_gusts_max": daily["wind_gusts_10m_max"][i]
            })


    silver_df = pd.DataFrame(rows)

    silver_df["date"] = pd.to_datetime(silver_df["date"],format="%Y-%m-%d")

    silver_df.to_csv("/opt/airflow/data/silver/clean_silver.csv",index=False)