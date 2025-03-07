import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Configurations
WEATHER_API_KEY = 'your_openweathermap_api_key'
ZIP_CODE = '28409'

# Historical data (update with your real data)
historical_orders = [
    {'time': '2024-03-01 13:00', 'orders': 15},
    {'time': '2024-03-01 14:00', 'orders': 12},
    {'time': '2024-03-01 18:00', 'orders': 22},
    # add more data points here...
]

# Fetch weather
def get_weather(zip_code):
    url = f"http://api.openweathermap.org/data/2.5/weather?zip={zip_code}&appid={WEATHER_API_KEY}"
    response = requests.get(url).json()
    return response.get('weather', [{}])[0].get('main', 'Unknown')

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

weather = get_weather('28409')
peak_hour = analyze_peak_hours(historical_orders)
current_hour = datetime.now().hour
recommendation = recommend_earning_mode(current_hour, peak_hour)

st.subheader(f"📍 Current Weather in {ZIP_CODE}")
st.write(weather)

st.subheader("📈 Historical Peak Hour")
st.write(f"{peak_hour}:00")

st.subheader("🕑 Current Time")
st.write(f"{current_hour}:00")

st.subheader("💰 Recommended Earning Mode")
st.success(recommendation)