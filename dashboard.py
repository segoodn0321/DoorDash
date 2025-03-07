import streamlit as st
import requests
from datetime import datetime

# Secure API key from Streamlit secrets
weather_api_key = st.secrets["openweathermap"]["api_key"]

# Get weather and city data from OpenWeatherMap
def get_weather(zip_code, api_key):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?zip={zip_code},us&appid={api_key}&units=imperial"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        condition = data['weather'][0]['main']
        temp = data['main']['temp']
        city = data['name']
        lat, lon = data['coord']['lat'], data['coord']['lon']
        return condition, temp, city, lat, lon
    except requests.RequestException as e:
        st.error(f"Weather API Error: {e}")
        return None, None, None, None, None

# Recommend earning mode based on time and weather
def recommend_earning_mode(current_hour, weather_condition):
    peak_hours = [11, 12, 13, 17, 18, 19, 20, 21]
    if weather_condition in ["Rain", "Snow", "Thunderstorm"]:
        return "Earn per Order (High demand due to weather)"
    elif current_hour in peak_hours:
        return "Earn per Order (Peak hours)"
    else:
        return "Earn by Time (Moderate or low demand)"

# Streamlit Dashboard UI
st.title("🚗 DoorDash Earnings Optimizer")

zip_code = st.text_input("Enter Zip Code:", "28409")

if st.button("Search"):
    weather_condition, temp, city, lat, lon = get_weather(zip_code, weather_api_key)

    if city:
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader(f"📍 Location: {zip_code} - {city}")
            st.subheader("🌦️ Current Weather")
            st.info(f"{weather_condition}, {temp}°F")

            st.subheader("🕑 Current Local Time")
            current_hour = datetime.now().hour
            st.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            st.subheader("💡 Recommended Earning Mode")
            recommendation = recommend_earning_mode(current_hour, weather_condition)
            st.success(recommendation)

        with col2:
            st.subheader("🗺️ Map View")
            map_data = {'lat': [lat], 'lon': [lon]}
            st.map(map_data, zoom=11)

    else:
        st.error("Unable to fetch data for the provided Zip Code.")
