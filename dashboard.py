"""dashboard.py

Streamlit dashboard for the Rocket Launch Weather Monitoring demo.

NOTE: SAFE / UNSAFE only means the readings satisfy example thresholds
chosen by the user. It is NOT real launch guidance.
"""

from datetime import datetime

import altair as alt
import pandas as pd
import streamlit as st

import logger
import main
import safety_rules

SOURCE_LABELS = {
    "Sample data": "sample",
    "Live API (Open-Meteo)": "live",
    "ESP32 (simulated)": "esp32",
}

SOURCE_NAMES = {"sample": "sample", "live": "live_api",
                "esp32": "esp32_simulated"}

st.set_page_config(page_title="Rocket Launch Weather Monitor", layout="wide")

st.title("Rocket Launch Weather Monitoring and Decision Support System")
st.caption(
    "Educational ECE prototype. SAFE / UNSAFE only shows whether the readings "
    "satisfy the example thresholds set in the sidebar. It is not real "
    "launch-safety guidance."
)

# ---------- Sidebar controls ----------
with st.sidebar:
    st.header("Controls")
    source_label = st.radio("Data source", list(SOURCE_LABELS))
    source_key = SOURCE_LABELS[source_label]

    st.subheader("Demonstration thresholds")
    max_wind = st.number_input("Max wind speed (km/h)", 0.0, 200.0, 30.0, 1.0)
    max_temp = st.number_input("Max temperature (C)", -50.0, 80.0, 40.0, 1.0)
    min_temp = st.number_input("Min temperature (C)", -50.0, 80.0, 0.0, 1.0)
    max_hum = st.number_input("Max humidity (%)", 0.0, 100.0, 85.0, 1.0)

    chart_filter = st.selectbox(
        "Charts show", ["Selected source only", "All sources"])

    refresh = st.button("Refresh reading", type="primary")

if min_temp >= max_temp:
    st.error("Minimum temperature must be lower than maximum temperature.")
    st.stop()

thresholds = safety_rules.Thresholds(
    max_wind_speed=max_wind,
    max_temperature=max_temp,
    min_temperature=min_temp,
    max_humidity=max_hum,
)

# ---------- Get a new reading when needed ----------
if refresh or st.session_state.get("source_key") != source_key:
    try:
        result = main.run(source_key, thresholds)
        st.session_state["reading"] = result["reading"]
        st.session_state["updated"] = datetime.now(logger.IST).strftime("%Y-%m-%d %H:%M:%S")
        st.session_state["source_key"] = source_key
        st.session_state.pop("error", None)
    except ValueError as error:
        st.session_state["error"] = str(error)
        st.session_state["source_key"] = source_key
        st.session_state.pop("reading", None)

if "error" in st.session_state:
    st.error(f"Could not get a reading: {st.session_state['error']}")

# ---------- Current reading ----------
reading = st.session_state.get("reading")
if reading:
    col1, col2, col3 = st.columns(3)
    col1.metric("Temperature", f"{reading['temperature']} C")
    col2.metric("Humidity", f"{reading['humidity']} %")
    col3.metric("Wind speed", f"{reading['wind_speed']} km/h")

    st.write(f"**Data source:** {reading['source']}")
    st.write(f"**Last updated:** {st.session_state['updated']}")

    status, reasons = safety_rules.evaluate(
        reading["temperature"], reading["humidity"],
        reading["wind_speed"], thresholds)

    if status == "SAFE":
        st.success("SAFE (demonstration only): all readings are within the example thresholds.")
    else:
        st.error("UNSAFE (demonstration only): " + " | ".join(reasons))

# ---------- History ----------
st.subheader("Weather history")
rows = logger.read_history(main.LOG_FILE)

if not rows:
    st.info("No history yet. Press 'Refresh reading' to log a reading.")
else:
    df = pd.DataFrame(rows)
    st.dataframe(df.iloc[::-1], hide_index=True)

    st.subheader("Charts")
    chart_df = df
    if chart_filter == "Selected source only":
        chart_df = df[df["source"] == SOURCE_NAMES[source_key]]
    if chart_df.empty:
        st.info("No logged readings for this source yet. Press Refresh reading.")
        st.stop()
    chart_data = chart_df.set_index("timestamp")
    for column, title in (("temperature", "Temperature (C)"),
                          ("humidity", "Humidity (%)"),
                          ("wind_speed", "Wind speed (km/h)")):
        st.write(title)
        low = float(chart_data[column].min())
        high = float(chart_data[column].max())
        pad = max((high - low) * 0.1, 1.0)
        chart = (
            alt.Chart(chart_data.reset_index())
            .mark_line(point=True)
            .encode(
                x=alt.X("timestamp:N", title="Time", axis=alt.Axis(labelAngle=-45)),
                y=alt.Y(f"{column}:Q", title=title,
                        scale=alt.Scale(domain=[low - pad, high + pad])),
                tooltip=["timestamp", column],
            )
        )
        st.altair_chart(chart, use_container_width=True)
