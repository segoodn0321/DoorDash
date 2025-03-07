import streamlit as st
import requests
from datetime import datetime

# Load API key securely from Streamlit secrets
weather_api_key = st.secrets["openweathermap"]["api_key"]

# Fetch weather and city data
def get_weather(zip_code, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?zip={zip_code},us&appid={api_key}&units=imperial"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        condition = data['weather'][0]['main']
        temp = data['main']['temp']
        city = data['name']
        return condition, temp, city
    except requests.RequestException as e:
        st.error(f"Weather API error: {e}")
        return None, None, None

# Recommend earning mode based on time and weather
def recommend_earning_mode(current_hour, weather_condition):
    peak_hours = [11, 12, 13, 17, 18, 19, 20, 21]

    if weather_condition in ["Rain", "Snow", "Thunderstorm"]:
        return "Earn per Order (High demand due to weather)"
    elif current_hour in peak_hours:
        return "Earn per Order (Peak meal hours)"
    else:
        return "Earn by Time (Moderate or low demand)"

# Streamlit Dashboard
st.title("🚗 DoorDash Earnings Optimizer")

zip_code = st.text_input("Enter Zip Code:", "28409")

if st.button("Search"):
    current_hour = datetime.now().hour

    # Get weather data
    weather_condition, temp, city = get_weather(zip_code, weather_api_key)

    if weather_condition and city:
        st.subheader(f"📍 Location: {zip_code} - {city}")
        st.info(f"{weather_condition}, {temp}°F")

        st.subheader("🕑 Current Local Time")
        st.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        st.subheader("💡 Recommended Earning Mode")
        recommendation = recommend_earning_mode(current_hour, weather_condition)
        st.success(recommendation)
    else:
        st.warning("Unable to fetch complete data; try again later.")
