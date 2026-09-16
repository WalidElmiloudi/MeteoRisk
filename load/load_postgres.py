import datetime
import pandas as pd
from sqlalchemy import create_engine,Date
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

db_url = "postgresql://postgres:Root1234@localhost:5432/weather_risk_db"

try :
    engine = create_engine(db_url)
except Exception as e:
    print(f"Database connection error : {e}")

class Base(DeclarativeBase):
    pass

class WeatherRisk(Base):
    __tablename__ = "weather_risk"

    id : Mapped[int] = mapped_column(primary_key=True)
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

Base.metadata.create_all(engine)

df = pd.read_csv("./data/gold/feature_gold.csv")

df.to_sql(
    name="weather_risk",
    con=engine,
    if_exists="append",
    index = False
)
