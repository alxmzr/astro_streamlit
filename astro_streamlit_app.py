import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib import const
import matplotlib.pyplot as plt

# ------------------- UI -------------------

st.set_page_config(layout="wide")
st.title("🔮 Astro Finance Dashboard")

tab1, tab2 = st.tabs(["📈 Price Chart", "🌌 Planetary Longitude & Aspects"])

with tab1:
    st.subheader("Financial Chart (Yahoo Finance)")
    symbol = st.text_input("Ticker", "BTC-USD")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=pd.to_datetime("2022-01-01"))
    with col2:
        end_date = st.date_input("End Date", value=pd.to_datetime("2023-01-01"))

    if st.button("📥 Load Price Chart"):
        data = yf.download(symbol, start=start_date, end=end_date)
        st.line_chart(data['Close'])

with tab2:
    st.subheader("Planetary Longitude Chart")

    planet = st.selectbox("Planet", ['MOON', 'SUN', 'MERCURY', 'VENUS', 'MARS', 'JUPITER', 'SATURN'])
    system = st.selectbox("Coordinate System", ['geo', 'helio'])
    orbis = st.slider("Aspect Orbis", 0.5, 5.0, 2.0, step=0.1)
    selected_angles = st.multiselect("Aspect Angles", [0, 60, 90, 120, 180], default=[0, 90, 180])
    compare_planets = st.multiselect("Compare With", ['SUN', 'MERCURY', 'VENUS', 'MARS', 'JUPITER', 'SATURN'], default=['SUN', 'MARS'])

    astro_start = st.date_input("Astro Start", value=pd.to_datetime("2022-01-01"), key="astro_start")
    astro_end = st.date_input("Astro End", value=pd.to_datetime("2023-01-01"), key="astro_end")

    if st.button("🔭 Calculate Planetary Longitude & Aspects"):
        pos = GeoPos("0", "51")  # London
        current = datetime.combine(astro_start, datetime.min.time())
        end_dt = datetime.combine(astro_end, datetime.min.time())
        delta = timedelta(days=1)

        timestamps = []
        degrees = []
        aspect_marks = []

        with st.spinner("Calculating..."):
            while current <= end_dt:
                dt = Datetime(current.strftime("%Y-%m-%d"), "00:00", "+00:00")
                chart = Chart(dt, pos, ID=system.upper())
                try:
                    p = chart.get(planet)
                    timestamps.append(current)
                    degrees.append(p.lon)

                    for other in compare_planets:
                        if other != planet:
                            try:
                                o = chart.get(other)
                                diff = abs(p.lon - o.lon) % 360
                                for angle in selected_angles:
                                    if abs(diff - angle) <= orbis:
                                        aspect_marks.append({
                                            "date": current,
                                            "angle": angle,
                                            "with": other,
                                            "exact": round(diff, 2)
                                        })
                            except:
                                continue
                except:
                    timestamps.append(current)
                    degrees.append(None)

                current += delta

        df = pd.DataFrame({
            "Date": timestamps,
            f"{planet}_longitude": degrees
        }).dropna()

        st.line_chart(df.set_index("Date"))

        if aspect_marks:
            st.success(f"Found {len(aspect_marks)} aspects 👇")
            st.dataframe(pd.DataFrame(aspect_marks))

        else:
            st.info("No aspects found.")
