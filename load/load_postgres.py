import os
from dotenv import load_dotenv

import datetime
import pandas as pd
from sqlalchemy import create_engine,UniqueConstraint,text
from sqlalchemy import Column, Integer, Float, String, Date
from sqlalchemy.orm import declarative_base


def load_postgres():
    load_dotenv()

    db_url = os.getenv("DB_URL")

    engine = create_engine(db_url)

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Database connected successfully")
    except Exception as e:
        print(f"Database connection error: {e}")

    Base = declarative_base()

    class WeatherRisk(Base):
        __tablename__ = "weather_risk"

        id = Column(Integer, primary_key=True, autoincrement=True)
        city = Column(String)
        latitude = Column(Float)
        longitude = Column(Float)
        date = Column(Date)
        weather_code = Column(Integer)

        temperature_max = Column(Float)
        temperature_min = Column(Float)

        precipitation_sum = Column(Float)
        precipitation_probability = Column(Integer)

        wind_speed_max = Column(Float)
        wind_gusts_max = Column(Float)

        temperature_category = Column(String)
        precipitation_category = Column(String)
        wind_category = Column(String)

        risk_score = Column(Float)
        risk_level = Column(String)

        __table_args__ = (
            UniqueConstraint("city", "date", name="uq_city_date"),
        )

    Base.metadata.create_all(engine)

    df = pd.read_csv("/opt/airflow/data/gold/feature_gold.csv")
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
