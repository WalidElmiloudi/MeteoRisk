# Weather Risk Data Engineering Pipeline

An end-to-end, automated data engineering pipeline designed to assess weather-related delivery risks for a logistics provider in Morocco.

The pipeline extracts multi-city forecasts from Open-Meteo, transforms raw data across a **Medallion Architecture (Bronze → Silver → Gold)**, computes a composite **Weather Risk Score (0–100)**, stores structured datasets in PostgreSQL, and serves interactive insights via a Streamlit dashboard—all orchestrated with Apache Airflow and fully containerized with Docker Compose.

---

## 📌 Executive Summary & Business Context

Logistics operations in Morocco face regional weather hazards—including flash floods, extreme heatwaves in inland zones, and high wind gusts along coastal routes.

This pipeline ingests daily weather forecasts across major Moroccan cities, standardizes the raw payloads, performs domain validation, and calculates a dynamic **Delivery Weather Risk Score**. Logistics managers can utilize the resulting metrics to proactively reroute drivers, adjust dispatch schedules, or issue safety warnings during high-risk weather events.

---

## 🏗️ Architecture & Data Flow

```text
                     ┌─────────────────┐
                     │   SimpleMaps    │
                     │ Morocco Cities  │
                     └────────┬────────┘
                              │ City metadata & coordinates
                              ▼
                     ┌─────────────────┐
                     │   Open-Meteo    │
                     │   Weather API   │
                     └────────┬────────┘
                              │ Daily raw forecast payloads
                              ▼
                     ┌─────────────────┐
                     │     BRONZE      │
                     │   Raw Storage   │
                     └────────┬────────┘
                              │ Deduplication, cleaning & validation
                              ▼
                     ┌─────────────────┐
                     │     SILVER      │
                     │ Standardized DB │
                     └────────┬────────┘
                              │ Feature engineering & risk scoring
                              ▼
                     ┌─────────────────┐
                     │      GOLD       │
                     │ Analytics Ready │
                     └────────┬────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │   PostgreSQL    │
                     └────────┬────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │    Streamlit    │
                     │    Dashboard    │
                     └─────────────────┘

                     Apache Airflow (DAGs)
                 orchestrates the entire flow
```

---

## 🧰 Tech Stack

* **Language & Analysis:** Python 3.10+, Pandas, SQLAlchemy
* **Data Sources:** SimpleMaps (Moroccan geolocation data), Open-Meteo REST API
* **Orchestration:** Apache Airflow
* **Storage:** PostgreSQL 15+
* **Visualization:** Streamlit
* **Infrastructure:** Docker, Docker Compose

---

## 📁 Repository Structure

```text
.
├── dags/
│   └── weather_pipeline_dag.py     # Airflow DAG defining task dependencies
├── dashboard/
│   ├── app.py                      # Streamlit dashboard application
│   ├── Dockerfile                  # Container definition for Streamlit UI
│   └── requirements.txt            # Streamlit-specific dependencies
├── data/
│   ├── bronze/                     # Raw extraction payloads (CSV, JSON, JSONL)
│   ├── silver/                     # Cleaned, structured intermediate CSVs
│   └── gold/                       # Enriched CSVs with features and risk scores
├── extraction/
│   ├── extract_weather.py          # API fetching logic with retry mechanisms
│   └── __init__.py
├── transformation/
│   ├── clean_silver.py             # Data quality control and standardization
│   ├── feature_gold.py             # Feature engineering & score calculation
│   └── __init__.py
├── load/
│   ├── load_postgres.py            # Database loading and upsert logic
│   ├── queries.sql                 # SQL analytical queries for business logic
│   └── __init__.py
├── docs/
│   └── dashboard_screenshots/      # UI previews and documentation assets
├── Dockerfile                      # Application runner image configuration
├── Dockerfile.airflow              # Custom Airflow environment image configuration
├── docker-compose.yml              # Multi-container service orchestration
├── requirements.txt                # Core Python dependencies
├── requirements-airflow.txt        # Airflow provider dependencies
└── README.md                       # Repository documentation
```

---

## 🔄 Medallion Pipeline Architecture

### 1. Data Extraction & Bronze Layer

* Retrieves geographic coordinates (latitude, longitude) for targeted Moroccan cities from `data/bronze/ma.csv`.
* Queries Open-Meteo for 7-day forecast windows containing:
  * `weather_code`
  * `temperature_2m_max`, `temperature_2m_min`
  * `precipitation_sum`, `precipitation_probability_max`
  * `wind_speed_10m_max`, `wind_gusts_10m_max`
* Stores raw payloads directly in `data/bronze/` as immutable historical records. Features error handling for API timeouts, HTTP failures, and malformed payloads.

### 2. Silver Layer (Cleaning & Quality Control)

* Standardizes column nomenclature and parses explicit ISO date formats.
* Implements rigorous data validation rules:
  * Flagging logical anomalies (e.g., $T_{\text{max}} < T_{\text{min}}$, $\text{precipitation} < 0$, $\text{probability} \notin [0, 100]$).
  * Enforces composite key uniqueness: `(city, date)`.
* Writes validated datasets to `data/silver/clean_silver.csv`.

### 3. Gold Layer & Risk Scoring Model

Enriches data with categorical bins and computes a composite **Delivery Weather Risk Score** ranging from `0` to `100`.

#### Weight Allocation

$$
\text{Risk Score} = 0.35(R_{\text{rain}}) + 0.30(R_{\text{wind}}) + 0.15(R_{\text{temp}}) + 0.20(R_{\text{condition}})
$$

Where each component score ($R$) is normalized to $[0, 100]$ based on operational thresholds:

* **Rain Risk ($R_{\text{rain}}$):** Evaluates precipitation volume ($\text{mm}$) and probability.
* **Wind Risk ($R_{\text{wind}}$):** Accounts for continuous wind speeds and peak gust intensity.
* **Temperature Risk ($R_{\text{temp}}$):** Penalizes extreme heat ($\ge 40^\circ\text{C}$) or severe cold ($\le 0^\circ\text{C}$).
* **Condition Risk ($R_{\text{condition}}$):** Bins specific WMO weather codes (e.g., thunderstorms, dense fog).

#### Risk Classifications

| Score Range | Risk Level | Operational Guidance |
| :--- | :--- | :--- |
| **0 – 20** | Very Low | Normal delivery operations |
| **21 – 40** | Low | Standard operational monitoring |
| **41 – 60** | Moderate | Alert drivers; minor delivery delays expected |
| **61 – 80** | High | Reroute vulnerable paths; restrict two-wheeler dispatch |
| **81 – 100** | Very Very High | Halt high-risk transit routes; emergency protocols |

---

## 🗄️ Database Schema & Load Strategy

Target table: `gold_weather_risks` in PostgreSQL.

* **Primary Composite Key:** `(city, date)`
* **Write Mode:** Upsert (`ON CONFLICT (city, date) DO UPDATE`).
* Re-running historical or updated forecasts safely refreshes metric values without generating duplicate entries.

```sql
CREATE TABLE IF NOT EXISTS gold_weather_risks (
    city VARCHAR(100),
    latitude NUMERIC(8, 5),
    longitude NUMERIC(8, 5),
    date DATE,
    weather_code INT,
    temperature_max NUMERIC(4,1),
    temperature_min NUMERIC(4,1),
    precipitation_sum NUMERIC(5,1),
    precipitation_probability INT,
    wind_speed_max NUMERIC(5,1),
    wind_gusts_max NUMERIC(5,1),
    temperature_category VARCHAR(20),
    precipitation_category VARCHAR(20),
    wind_category VARCHAR(20),
    temperature_risk NUMERIC(5,2),
    rain_risk NUMERIC(5,2),
    wind_risk NUMERIC(5,2),
    weather_condition_risk NUMERIC(5,2),
    risk_score NUMERIC(5,2),
    risk_level VARCHAR(20),
    PRIMARY KEY (city, date)
);
```

### Business Intelligence Queries (`load/queries.sql`)

The repository includes ready-to-run SQL queries for regional analytics:

* **Top Thermal Extremes:** Identifies cities exceeding high temperature thresholds.
* **Precipitation Spikes:** Pinpoints zones with high rainfall volumes affecting road safety.
* **Aggregate City Risk:** Ranks regions by average operational risk over the 7-day window.
* **Peak Hazard Windows:** Tracks specific dates presenting systemic risk spikes nationwide.

---

## ⚡ Orchestration (Apache Airflow)

The entire flow is managed by the DAG `weather_pipeline_dag`:

```text
[extract_weather] ──► [clean_weather] ──► [feature_engineering] ──► [load_postgres]
```

* **Schedule:** Daily execution
* **Retries:** Configured with exponential backoff for network-resilient extraction.
* **Monitoring:** Task status, execution logs, and dependency management accessible via the Airflow Web UI.

---

## 🚀 Getting Started

### Prerequisites

* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (with Docker Compose enabled)
* Git

### Setup & Launch

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/weather-risk-pipeline.git
   cd weather-risk-pipeline
   ```

2. **Configure environment variables:**
   Create a `.env` file in the root directory:
   ```env
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=weather_db
   POSTGRES_HOST=postgres
   POSTGRES_PORT=5432
   AIRFLOW__CORE__FERNET_KEY=
   ```

3. **Build container images:**
   ```bash
   docker compose build
   ```

4. **Spin up the stack:**
   ```bash
   docker compose up -d
   ```

5. **Verify running containers:**
   ```bash
   docker compose ps
   ```

---

## 🖥️ Application Services & Port Mapping

| Service | Port | Access URL | Description |
| :--- | :--- | :--- | :--- |
| **Streamlit Dashboard** | `8501` | `http://localhost:8501` | Interactive analytics portal |
| **Airflow Web UI** | `8080` | `http://localhost:8080` | Pipeline orchestration monitoring |
| **PostgreSQL** | `5432` | `localhost:5432` | Data warehouse database instance |

---

## 📊 Streamlit Dashboard Overview

The Streamlit UI connects directly to PostgreSQL to provide logistics operators with:

* **Interactive Filters:** Multi-select filtering by city, date ranges, and risk tiers (e.g., *High*, *Very High*).
* **Geospatial & Risk Views:** Highlighting regional risk concentrations across Morocco.
* **Alert Feed:** Listing high-risk delivery windows requiring driver mitigation.

---

## 📄 License & Acknowledgments

* **Weather Data:** Powered by [Open-Meteo API](https://open-meteo.com/).
* **Geographic Data:** Moroccan city coordinates provided by [SimpleMaps](https://simplemaps.com/).
* Open-source software released under the MIT License.
