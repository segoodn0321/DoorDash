import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- Configuration ---
WEATHER_API_KEY = '8a0599888629317497a67f540215a4fc'  # Replace with your actual API key
ZIP_CODE = '28409'

# --- Historical Data (Replace with your actual data) ---
historical_orders = [
    {'time': '2024-03-01 13:00', 'orders': 15},
    {'time': '2024-03-01 14:00', 'orders': 12},
    {'time': '2024-03-01 18:00', 'orders': 22},
    # Add more data points here
]

# --- Functions ---
def get_weather(zip_code, api_key):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?zip={zip_code},us&appid={api_key}&units=imperial"
        response = requests.get(url)
        response.raise_for_status()
        weather_data = response.json()
        weather_condition = weather_data['weather'][0]['main']
        temperature = weather_data['main']['temp']
        return f"{weather_condition}, {temperature}°F"
    except requests.RequestException as e:
        return f"Error fetching weather: {e}"

def analyze_peak_hours(historical_orders):
    df = pd.DataFrame(historical_orders)
    df['time'] = pd.to_datetime(df['time'])
    peak_hour = df.groupby(df['time'].dt.hour)['orders'].sum().idxmax()
    return peak_hour

def recommend_earning_mode(current_hour, peak_hour):
    return "Earn per Order 🟢" if abs(current_hour - peak_hour) <= 1 else "Earn by Time 🟡"

# --- Streamlit Dashboard ---
st.title("🚗 DoorDash Earnings Optimizer")

with st.spinner("Fetching weather data..."):
    weather = get_weather(ZIP_CODE, WEATHER_API_KEY)

peak_hour = analyze_peak_hours(historical_orders)
current_hour = datetime.now().hour
recommendation = recommend_earning_mode(current_hour, peak_hour)

# --- Dashboard Display ---
st.subheader(f"📍 Current Weather in {ZIP_CODE}")
st.info(weather)

st.subheader("📈 Historical Peak Hour")
st.metric(label="Peak Order Hour", value=f"{peak_hour}:00")

st.subheader("🕑 Current Local Time")
st.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

st.subheader("💰 Recommended Earning Mode")
st.success(recommendation)
