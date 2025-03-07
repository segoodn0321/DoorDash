import streamlit as st
import requests
from datetime import datetime

# API Configuration
WEATHER_API_KEY = '28228f6dd7c6a9b575000a82351d4d0c'

# Fetch weather and city data from OpenWeatherMap
def get_weather_and_city(zip_code):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?zip={zip_code},us&appid={WEATHER_API_KEY}&units=imperial"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        weather_condition = data['weather'][0]['main']
        temperature = data['main']['temp']
        city_name = data['name']
        return f"{weather_condition}, {temperature}°F", city_name
    except requests.RequestException as e:
        return f"Weather API error: {e}", None

# Recommend earning mode based on current time and weather
def recommend_earning_mode(current_hour, weather):
    peak_hours = [11, 12, 13, 17, 18, 19, 20, 21]
    if "Rain" in weather or "Snow" in weather or "Storm" in weather:
        return "Earn per Order (High Demand due to Weather)"
    elif current_hour in peak_hours:
        return "Earn per Order"
    else:
        return "Earn by Time"

# Streamlit Dashboard
st.title("🚗 DoorDash Earnings Optimizer")

zip_code = st.text_input("Enter Zip Code:", "28409")

if st.button("Search"):
    weather, city = get_weather_and_city(zip_code)
    current_hour = datetime.now().hour
    recommendation = recommend_earning_mode(current_hour, weather)

    # Display Results
    location_display = f"{zip_code} ({city})" if city else zip_code
    st.subheader(f"📍 Weather in {zip_code} - {city if city else 'Unknown City'}")
    st.info(weather)

    st.subheader("🕑 Current Local Time")
    st.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    st.subheader("💡 Recommended Earning Mode")
    if "error" in weather.lower():
        st.error("Cannot recommend mode without accurate weather data.")
    else:
        st.success(recommendation)
