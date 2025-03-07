import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Configuration
WEATHER_API_KEY = '8a0599888629317497a67f540215a4fc'  # Replace with your actual API key

# Example historical order data (to be replaced or expanded with actual data)
historical_orders = [
    {'time': '2024-03-01 13:00', 'orders': 15},
    {'time': '2024-03-01 14:00', 'orders': 12},
    {'time': '2024-03-01 18:00', 'orders': 22},
    # add more data points here...
]

# Fetch weather based on zip code
def get_weather(zip_code, api_key):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?zip={zip_code},us&appid={api_key}&units=imperial"
        response = requests.get(url)
        response.raise_for_status()
        weather_condition = response.json().get('weather', [{}])[0].get('main', 'Unknown')
        return weather_condition
    except requests.RequestException as e:
        return f"Error fetching weather: {e}"

# Peak hour analysis
def analyze_peak_hours(historical_orders):
    df = pd.DataFrame(historical_orders)
    df['time'] = pd.to_datetime(df['time'])
    peak_hour = df.groupby(df['time'].dt.hour)['orders'].sum().idxmax()
    return peak_hour

# Recommend earning mode
def recommend_earning_mode(current_hour, peak_hour):
    return "Earn per Order" if abs(current_hour - peak_hour) <= 1 else "Earn by Time"

# Streamlit Dashboard
st.title("🚗 DoorDash Earnings Optimizer")

zip_code = st.text_input("Enter Zip Code", "28409")

if st.button("Analyze"):
    weather = get_weather(zip_code=zip_code)
    peak_hour = analyze_peak_hours(historical_orders)
    current_hour = datetime.now().hour
    recommendation = recommend_earning_mode(current_hour, peak_hour)

    st.subheader(f"📍 Current Weather in {zip_code}")
    st.write(weather)

    st.subheader("📈 Historical Peak Hour")
    st.write(f"{peak_hour}:00")

    st.subheader("🕑 Current Time")
    st.write(f"{current_hour}:00")

    st.subheader("💰 Recommended Earning Mode")
    st.success(recommendation)

# User input
zip_code = st.text_input("Zip Code", value="28409")

if zip_code:
    weather = get_weather(zip_code, WEATHER_API_KEY)
    peak_hour = analyze_peak_hours(historical_orders)
    current_hour = datetime.now().hour
    recommendation = recommend_earning_mode(current_hour, peak_hour)

    st.subheader(f"📍 Current Weather in {zip_code}")
    st.write(weather)

    st.subheader("📈 Historical Peak Hour")
    st.write(f"{peak_hour}:00")

    st.subheader("🕑 Current Time")
    st.write(f"{current_hour}:00")

    st.subheader("💰 Recommended Earning Mode")
    st.success(recommendation)
