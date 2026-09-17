import os
from dotenv import load_dotenv

import datetime
import pandas as pd
from sqlalchemy import create_engine,Date,UniqueConstraint,text
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

load_dotenv()

db_url = os.getenv("DB_URL")

engine = create_engine(db_url)

try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("Database connected successfully")
except Exception as e:
    print(f"Database connection error: {e}")

class Base(DeclarativeBase):
    pass

class WeatherRisk(Base):
    __tablename__ = "weather_risk"

    id : Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    city : Mapped[str]
    latitude : Mapped[float]
    longitude : Mapped[float]
    date : Mapped[datetime.date]
    weather_code : Mapped[int]
    temperature_max : Mapped[float]
    temperature_min : Mapped[float]
    precipitation_sum : Mapped[float]
    precipitation_probability : Mapped[int]
    wind_speed_max : Mapped[float]
    wind_gusts_max : Mapped[float]
    temperature_category : Mapped[str]
    precipitation_category : Mapped[str]
    wind_category : Mapped[str]
    risk_score : Mapped[float]
    risk_level : Mapped[str]

    __table_args__ =(
        UniqueConstraint ("city","date",name="uq_city_date"),
    )

Base.metadata.create_all(engine)

df = pd.read_csv("./data/gold/feature_gold.csv")
df["date"] = pd.to_datetime(df["date"]).dt.date
df.to_sql(
    name="temp_staging",
    con=engine,
    if_exists="replace",
    index = False
)

upsert_query = f""" INSERT INTO weather_risk (city,latitude,longitude,date,weather_code,temperature_max,temperature_min,precipitation_sum,precipitation_probability,wind_speed_max,wind_gusts_max,temperature_category,precipitation_category,wind_category,risk_score,risk_level)
                SELECT city,latitude,longitude,date,weather_code,temperature_max,temperature_min,precipitation_sum,precipitation_probability,wind_speed_max,wind_gusts_max,temperature_category,precipitation_category,wind_category,risk_score,risk_level FROM temp_staging
                ON CONFLICT (city,date)
                DO UPDATE SET
                    latitude = EXCLUDED.latitude,
                    longitude = EXCLUDED.longitude,
                    weather_code = EXCLUDED.weather_code,
                    temperature_max = EXCLUDED.temperature_max,
                    temperature_min = EXCLUDED.temperature_min,
                    precipitation_sum = EXCLUDED.precipitation_sum,
                    precipitation_probability = EXCLUDED.precipitation_probability,
                    wind_speed_max = EXCLUDED.wind_speed_max,
                    wind_gusts_max = EXCLUDED.wind_gusts_max,
                    temperature_category = EXCLUDED.temperature_category,
                    precipitation_category = EXCLUDED.precipitation_category,
                    wind_category = EXCLUDED.wind_category,
                    risk_score = EXCLUDED.risk_score,
                    risk_level = EXCLUDED.risk_level
"""

with engine.begin() as conn :
    conn.execute(text(upsert_query))
    conn.execute(text("DROP TABLE temp_staging"))
