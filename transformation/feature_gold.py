import pandas as pd
import numpy as np

df = pd.read_csv("./data/silver/clean_silver.csv")

df["temperature_category"] = pd.cut(df["temperature_max"],bins=[-float("inf"), 5, 15, 30, 35, float("inf")],labels=["Very Cold","Cold","Normal","Hot","Extreme Heat"])
df["precipitation_category"] = pd.cut(df["precipitation_sum"],bins=[-float("inf"),0,2.5,10,20,float("inf")],labels=["None","Light","Moderate","Heavy","Very Heavy"])
df["wind_category"] = pd.cut((df["wind_speed_max"] + df["wind_gusts_max"])/2,bins=[-float("inf"),20,40,60,float("inf")],labels=["Low","Moderate","Strong","Very Strong"])

precipitation_risk = np.where(df["precipitation_sum"] >= 30,100,np.where(df["precipitation_sum"] >= 20,75,np.where(df["precipitation_sum"] >= 10,50,np.where(df["precipitation_sum"] >= 2.5,20,0))))
wind_speed_risk = np.where(df["wind_speed_max"] >= 60,100,np.where(df["wind_speed_max"] >= 40,70,np.where(df["wind_speed_max"] >= 20,30,0)))
wind_gusts_risk = np.where(df["wind_gusts_max"] >= 70,100,np.where(df["wind_gusts_max"] >= 50,70,np.where(df["wind_gusts_max"] >= 30,30,0)))
heat_risk = np.where(df["temperature_max"] >= 40,100,np.where(df["temperature_max"] >= 35,70,np.where(df["temperature_max"] >= 30,30,0)))
cold_risk = np.where(df["temperature_min"] >= 15,0,np.where(df["temperature_min"] >= 10,20,np.where(df["temperature_min"] >= 5,50,80)))
rain_risk = 0.7 * precipitation_risk + 0.3 * df["precipitation_probability"]
wind_risk = 0.4 * wind_speed_risk + 0.6 * wind_gusts_risk
temperature_risk = np.where(heat_risk >= cold_risk,heat_risk,cold_risk)

weather_risk_map = {
    0: 0,

    1: 5,
    2: 5,
    3: 5,

    45: 30,
    48: 30,

    51: 30,
    53: 40,
    55: 50,

    56: 50,
    57: 60,

    61: 50,
    63: 65,
    65: 80,

    66: 80,
    67: 90,

    71: 70,
    73: 80,
    75: 90,
    77: 80,

    80: 60,
    81: 75,
    82: 85,

    85: 80,
    86: 90,

    95: 100,
    96: 100,
    99: 100
}

weather_condition_risk = df["weather_code"].map(weather_risk_map)
df["risk_score"] =(0.35 * rain_risk + 0.30 * wind_risk + 0.15 * temperature_risk + 0.20 * weather_condition_risk)
df["risk_level"] = pd.cut(df["risk_score"],bins = [0,20,40,60,80,100],labels = ['Very Low','Low','Moderate','High','Critical'])
df["risk_level"] = df["risk_level"].fillna('Very Low')

df.to_csv("./data/gold/feature_gold.csv")
