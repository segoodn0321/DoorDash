import streamlit as st
import requests
from datetime import datetime

# Load API key securely from Streamlit secrets
weather_api_key = st.secrets["openweathermap"]["api_key"]

# Fetch weather, city, and coordinates
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
        st.error(f"Weather API error: {e}")
        return None, None, None, None, None

# Recommend earning mode based on conditions
def recommend_earning_mode(current_hour, weather_condition):
    peak_hours = [11, 12, 13, 17, 18, 19, 20, 21]
    if weather_condition in ["Rain", "Snow", "Thunderstorm"]:
        return "Earn per Order (High Demand - Weather)"
    elif current_hour in peak_hours:
        return "Earn per Order (Peak Meal Hours)"
    else:
        return "Earn by Time (Moderate/Low Demand)"

# Streamlit UI
st.title("🚗 DoorDash Earnings Optimizer")

zip_code = st.text_input("Enter Zip Code:", "28409")

if st.button("Search"):
    weather_condition, temp, city, lat, lon = get_weather(zip_code, weather_api_key)

    if city:
        st.subheader(f"📍 Location: {zip_code} - {city}")
        
        col1, col2 = st.columns([2,1])

        with col1:
            st.subheader("🌦️ Current Weather")
            st.info(f"{weather_condition}, {temp}°F")

            st.subheader("🕑 Current Local Time")
            current_hour = datetime.now().hour
            st.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            st.subheader("💡 Recommended Earning Mode")
            recommendation = recommend_earning_mode(current_hour, weather_condition)
            st.success(recommendation)

        with st.expander("🛰️ Live Weather Map (via OpenWeatherMap)"):
            map_url = f"https://openweathermap.org/weathermap?basemap=map&cities=true&layer=precipitation&lat={lat}&lon={lon}&zoom=11"
            st.markdown(f'<iframe src="{map_url}" width="100%" height="500"></iframe>', unsafe_allow_html=True)
    else:
        st.error("Could not fetch weather or location data. Please check the Zip Code.")
    
