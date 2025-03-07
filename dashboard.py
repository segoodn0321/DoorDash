import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Configuration
WEATHER_API_KEY = '8a0599888629317497a67f540215a4fc'
DOORDASH_API_KEY = 'a2677a32-0908-4751-98af-cd847ab5be19'

# Fetch weather data
def get_weather(zip_code):
    url = f"http://api.openweathermap.org/data/2.5/weather?zip={zip_code},us&appid={WEATHER_API_KEY}&units=imperial"
    try:
        response = requests.get(url)
        response.raise_for_status()
        weather_data = response.json()
        condition = weather_data['weather'][0]['main']
        temperature = weather_data['main']['temp']
        return f"{condition}, {temperature}°F"
    except requests.RequestException:
        return "Weather data unavailable"

# Fetch DoorDash order volume data
def fetch_doordash_data(zip_code):
    headers = {'Authorization': f'Bearer {DOORDASH_API_KEY}'}
    url = f'https://api.doordash.com/v1/market/{zip_code}/order_volume'
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return None

# Peak hour analysis
def analyze_peak_hours(doordash_data):
    if not doordash_data or 'orders' not in doordash_data:
        return None
    df = pd.DataFrame(doordash_data['orders'])
    df['time'] = pd.to_datetime(df['time'])
    peak_hour = df.groupby(df['time'].dt.hour)['volume'].sum().idxmax()
    return peak_hour

# Recommend earning mode
def recommend_earning_mode(current_hour, peak_hour):
    return "Earn per Order" if abs(current_hour - peak_hour) <= 1 else "Earn by Time"

# Streamlit Dashboard
st.title("🚗 DoorDash Earnings Optimizer")

zip_code = st.text_input("Enter Zip Code", "28409")

if st.button("Analyze"):
    weather = get_weather(zip_code)
    doordash_data = fetch_doordash_data(zip_code)
    peak_hour = analyze_peak_hours(doordash_data)
    current_hour = datetime.now().hour
    recommendation = recommend_earning_mode(current_hour, peak_hour)

    st.subheader(f"📍 Weather in {zip_code}")
    st.write(weather)

    if peak_hour is not None:
        st.subheader("📈 Peak DoorDash Hour")
        st.write(f"{peak_hour}:00")
    else:
        st.subheader("📈 Peak DoorDash Hour")
        st.write("No DoorDash data available for this zip code.")

    st.subheader("🕑 Current Local Time")
    st.write(f"{datetime.now().strftime('%H:%M')}")

