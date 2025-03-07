import streamlit as st
import requests
from datetime import datetime

# Load API keys securely from Streamlit secrets
weather_api_key = st.secrets["openweathermap"]["api_key"]
here_api_key = st.secrets["here"]["api_key"]

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

# Fetch real-time traffic congestion data from HERE API
def get_traffic_data(lat, lon, api_key):
    url = f"https://router.hereapi.com/v8/routes?transportMode=car&origin={lat},{lon}&destination={lat},{lon}&return=summary&apikey={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        traffic_time = data["routes"][0]["sections"][0]["summary"]["duration"]
        return traffic_time
    except requests.RequestException as e:
        st.error(f"Traffic API error: {e}")
        return None

# Recommend earning mode based on traffic, weather, and time
def recommend_earning_mode(current_hour, weather_condition, traffic_time):
    peak_hours = [11, 12, 13, 17, 18, 19, 20, 21]

    if traffic_time and traffic_time > 1200:  # If traffic time > 20 mins, assume congestion
        return "Earn by Time (High Traffic Congestion)"
    elif weather_condition in ["Rain", "Snow", "Thunderstorm"]:
        return "Earn per Order (High Demand - Bad Weather)"
    elif current_hour in peak_hours:
        return "Earn per Order (Peak Meal Hours)"
    else:
        return "Earn by Time (Moderate/Low Demand)"

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

            # Fetch traffic data
            traffic_time = get_traffic_data(lat, lon, here_api_key)
            traffic_status = "Heavy Congestion" if traffic_time and traffic_time > 1200 else "Light Traffic"
            st.subheader("🚦 Traffic Status")
            st.write(traffic_status)

            st.subheader("💡 Recommended Earning Mode")
            recommendation = recommend_earning_mode(current_hour, weather_condition, traffic_time)
            st.success(recommendation)

    else:
        st.error("Could not fetch weather or location data. Please check the Zip Code.")
