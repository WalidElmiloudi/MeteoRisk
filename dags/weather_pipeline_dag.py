from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
import sys

sys.path.append("/opt/airflow")

from extraction.extract_weather import extract_data
from transformation.clean_silver import clean_data
from transformation.feature_gold import feature_gold
from load.load_postgres import load_postgres as load_postgres_data



def extract_weather():
    print("Extracting weather data...")
    extract_data()


def clean_weather():
    print("Cleaning weather data...")
    clean_data()


def feature_engineering():
    print("Creating features and calculating risk score...")
    feature_gold()


def load_postgres():
    print("Loading data into PostgreSQL...")
    load_postgres_data()


default_args = {
    "owner": "weather-project",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}


with DAG(
    dag_id="weather_risk_pipeline",
    default_args=default_args,
    description="Weather risk ETL pipeline for Moroccan cities",
    schedule="0 6 * * *",
    start_date=datetime(2026, 9, 18),
    catchup=False,
    tags=["weather", "etl", "postgres"],
) as dag:

    extract = PythonOperator(
        task_id="extract_weather",
        python_callable=extract_weather,
    )

    clean = PythonOperator(
        task_id="clean_weather",
        python_callable=clean_weather,
    )

    features = PythonOperator(
        task_id="feature_engineering",
        python_callable=feature_engineering,
    )

    load = PythonOperator(
        task_id="load_postgres",
        python_callable=load_postgres,
    )

    extract >> clean >> features >> load