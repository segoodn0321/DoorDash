import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Configuration
WEATHER_API_KEY = '8a0599888629317497a67f540215a4fc'

# Historical orders placeholder (Replace or extend with real data)
historical_orders = [
    {'time': '2024-03-01 13:00', 'orders': 15},
    {'time': '2024-03-01 14:00', 'orders': 12},
    {'time': '2024-03-01 18:00', 'orders': 22},
    # Add more historical data points...
]

# Fetch weather data
def get_weather(zip_code):
    url = f"http://api.openweathermap.org/data/2.5/weather?zip={zip_code},us&appid={WEATHER_API_KEY}&units=imperial"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        condition = data['weather'][0]['main']
        temp = data['main']['temp']
        return f"{condition}, {temp} °F"
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
st.title("🚗 Kyle's DoorDash Earnings Optimizer")

zip_code = st.text_input("Enter Zip Code", value="28409")

if st.button("Search"):
    weather = get_weather(zip_code)
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
