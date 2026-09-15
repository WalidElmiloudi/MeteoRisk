import pandas as pd

df = pd.read_csv("./data/silver/clean_silver.csv")

df["temperature_category"] = pd.cut(df["temperature_max"],bins=[-float("inf"), 5, 15, 30, 35, float("inf")],labels=["Very Cold","Cold","Normal","Hot","Extreme Heat"])
df["percipitation_category"] = pd.cut(df["precipitation_sum"],bins=[-float("inf"),0,2.5,10,20,float("inf")],labels=["None","Light","Moderate","Heavy","Very Heavy"])

