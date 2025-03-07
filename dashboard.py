import streamlit as st
import requests
from datetime import datetime

# API Configuration (replace with your actual API key)
WEATHER_API_KEY = '28228f6dd7c6a9b575000a82351d4d0c'

# Fetch weather data
def get_weather(zip_code):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?zip={zip_code},us&appid={WEATHER_API_KEY}&units=imperial"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        weather_condition = data['weather'][0]['main']
        temperature = data['main']['temp']
        return f"{weather_condition}, {temperature}°F"
    except requests.RequestException as e:
        return f"Weather API error: {e}"

# Recommend earning mode based on current time and weather
def recommend_earning_mode(current_hour, weather):
    peak_hours = [11, 12, 13, 17, 18, 19, 20, 21]
    if current_hour in peak_hours:
        mode = "Earn per Order"
    else:
        mode = "Earn by Time"

    if "Rain" in weather or "Snow" in weather or "Storm" in weather:
        mode = "Earn per Order (High Demand due to Weather)"

    return mode

# Streamlit UI
st.title("🚗 DoorDash Earnings Optimizer")

zip_code = st.text_input("Enter Zip Code:", "28409")

if st.button("Search"):
    weather = get_weather(zip_code)
    current_hour = datetime.now().hour
    recommendation = recommend_earning_mode(current_hour, weather)

    st.subheader(f"📍 Current Weather in {zip_code}")
    st.info(weather)

    st.subheader("🕑 Current Local Time")
    st.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    st.subheader("💡 Recommended Earning Mode")
    if "error" in weather.lower():
        st.error("Unable to determine recommendation without weather information.")
    else:
        st.success(recommendation)
