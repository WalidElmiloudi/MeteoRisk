import os

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine


DATABASE_URL = os.getenv("DB_URL")

@st.cache_resource
def get_engine():
    return create_engine(DATABASE_URL)


@st.cache_data
def load_data():
    engine = get_engine()

    query = """
        SELECT
            city,
            latitude,
            longitude,
            date,
            weather_code,
            temperature_max,
            temperature_min,
            precipitation_sum,
            precipitation_probability,
            wind_speed_max,
            wind_gusts_max,
            temperature_category,
            precipitation_category,
            wind_category,
            risk_score,
            risk_level
        FROM weather_risk
        ORDER BY date, city;
    """

    df = pd.read_sql(query, engine)

    df["date"] = pd.to_datetime(df["date"])

    return df

def apply_filters(df):
    st.sidebar.header("Filters")
    cities = ["All"] + sorted(df["city"].dropna().unique().tolist())
    selected_city = st.sidebar.selectbox(
        "City",
        cities
    )
    min_date = df["date"].min().date()
    max_date = df["date"].max().date()
    selected_dates = st.sidebar.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    period = st.sidebar.selectbox(
        "Period",
        [
            "All",
            "Next 3 days",
            "Next 7 days"
        ]
    )
    risk_levels = [
        "All",
        "Low",
        "Moderate",
        "High",
        "Very High"
    ]
    selected_risk = st.sidebar.selectbox(
        "Risk level",
        risk_levels
    )
    filtered = df.copy()
    if selected_city != "All":
        filtered = filtered[
            filtered["city"] == selected_city
        ]
    if len(selected_dates) == 2:
        start_date, end_date = selected_dates

        filtered = filtered[
            (filtered["date"].dt.date >= start_date)
            & (filtered["date"].dt.date <= end_date)
        ]

    if period == "Next 3 days":
        first_date = df["date"].min()
        last_date = first_date + pd.Timedelta(days=2)

        filtered = filtered[
            (filtered["date"] >= first_date)
            & (filtered["date"] <= last_date)
        ]

    elif period == "Next 7 days":
        first_date = df["date"].min()
        last_date = first_date + pd.Timedelta(days=6)

        filtered = filtered[
            (filtered["date"] >= first_date)
            & (filtered["date"] <= last_date)
        ]
    if selected_risk != "All":
        filtered = filtered[
            filtered["risk_level"] == selected_risk
        ]

    return filtered

def display_kpis(df):

    if df.empty:
        st.warning("No data available for the selected filters.")
        return

    avg_risk = df["risk_score"].mean()
    max_risk = df["risk_score"].max()
    max_temperature = df["temperature_max"].max()
    max_precipitation = df["precipitation_sum"].max()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Average Risk",
        f"{avg_risk:.1f}"
    )

    col2.metric(
        "Maximum Risk",
        f"{max_risk:.1f}"
    )

    col3.metric(
        "Maximum Temperature",
        f"{max_temperature:.1f} °C"
    )

    col4.metric(
        "Maximum Precipitation",
        f"{max_precipitation:.1f} mm"
    )

def display_risk_charts(df):

    st.header("Weather Risk")

    if df.empty:
        return

    col1, col2 = st.columns(2)
    with col1:

        risk_by_date = (
            df.groupby("date")["risk_score"]
            .mean()
            .reset_index()
        )

        st.subheader("Risk by Date")

        st.line_chart(
            risk_by_date.set_index("date"),
            color="#c40000"
        )
    with col2:

        risk_by_city = (
            df.groupby("city")["risk_score"]
            .mean()
            .sort_values(ascending=False)
        )

        st.subheader("Average Risk by City")

        st.bar_chart(
            risk_by_city,
            color = "#c40000"
        )

def display_weather_charts(df):

    st.header("Weather Conditions")

    if df.empty:
        return

    col1, col2 = st.columns(2)
    with col1:

        temperature = (
            df.groupby("city")["temperature_max"]
            .max()
            .sort_values(ascending=False)
        )

        st.subheader("Maximum Temperature by City")

        st.bar_chart(
            temperature,
            color = "#c40000"
        )
    with col2:

        precipitation = (
            df.groupby("city")["precipitation_sum"]
            .max()
            .sort_values(ascending=False)
        )

        st.subheader("Maximum Precipitation by City")

        st.bar_chart(
            precipitation,
            color="#c40000"
        )
    wind = (
        df.groupby("city")["wind_gusts_max"]
        .max()
        .sort_values(ascending=False)
    )

    st.subheader("Maximum Wind Gust by City")

    st.bar_chart(
        wind,
        color="#c40000"
    )

def display_risk_analysis(df):

    st.header("Risk Analysis")

    if df.empty:
        return

    st.subheader("Highest Risk Periods")

    top_risks = (
        df[
            [
                "city",
                "date",
                "risk_score",
                "risk_level",
                "temperature_max",
                "precipitation_sum",
                "wind_gusts_max"
            ]
        ]
        .sort_values(
            "risk_score",
            ascending=False
        )
        .head(10)
    )

    st.dataframe(
        top_risks,
        use_container_width=True,
        hide_index=True
    )

def display_data_table(df):

    st.header("Forecast Data")

    if df.empty:
        return

    columns = [
        "city",
        "date",
        "temperature_max",
        "temperature_min",
        "precipitation_sum",
        "precipitation_probability",
        "wind_speed_max",
        "wind_gusts_max",
        "temperature_category",
        "precipitation_category",
        "wind_category",
        "risk_score",
        "risk_level"
    ]

    st.dataframe(
        df[columns],
        use_container_width=True,
        hide_index=True
    )

def main():

    st.set_page_config(
        page_title="Morocco Weather Risk",
        layout="wide"
    )

    st.title("🌦️ Morocco Weather Risk Dashboard")

    st.markdown(
        """
        Monitor weather forecasts and identify potentially
        risky conditions for delivery operations.
        """
    )

    try:
        df = load_data()

    except Exception as e:
        st.error("Unable to connect to PostgreSQL.")
        st.exception(e)
        return

    if df.empty:
        st.warning("The database contains no weather data.")
        return

    filtered_df = apply_filters(df)

    st.caption(
        f"{len(filtered_df)} forecast records selected"
    )

    display_kpis(filtered_df)

    st.divider()

    display_risk_charts(filtered_df)

    st.divider()

    display_risk_analysis(filtered_df)

    st.divider()

    display_weather_charts(filtered_df)

    st.divider()

    display_data_table(filtered_df)

    st.title("cities that their risk score >= 1")

    dangerous_cities = df[df["risk_score"] >= 2]

    st.map(dangerous_cities)


if __name__ == "__main__":
    main()