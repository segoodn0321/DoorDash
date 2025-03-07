import streamlit as st
import requests
from datetime import datetime

# Load API keys securely from Streamlit secrets
weather_api_key = st.secrets["openweathermap"]["api_key"]
here_api_key = st.secrets["here"]["api_key"]

# Fetch weather and city data
def get_weather(zip_code, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?zip={zip_code},us&appid={api_key}&units=imperial"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    condition = data['weather'][0]['main']
    temp = data['main']['temp']
    city = data['name']
    lat, lon = data['coord']['lat'], data['coord']['lon']
    return condition, temp, city, lat, lon

# Fetch traffic data from HERE API
def get_traffic_data(lat, lon, api_key):
    url = f"https://traffic.ls.hereapi.com/traffic/6.3/flow.json?prox={lat},{lon},1000&apiKey={api_key}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return data

# Recommend earning mode based on time, weather, and traffic
def recommend_earning_mode(current_hour, weather_condition, traffic_data):
    peak_hours = [11, 12, 13, 17, 18, 19, 20, 21]
    traffic_congestion = any(
        flow_segment['CURRENT_SPEED'] < flow_segment['FREE_FLOW_SPEED']
        for flow_segment in traffic_data['RWS'][0]['RW'][0]['FIS'][0]['FI']
    )
    if weather_condition in ["Rain", "Snow", "Thunderstorm"]:
        return "Earn per Order (High demand due to weather)"
    elif traffic_congestion:
        return "Earn by Time (High traffic congestion)"
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
    weather_condition, temp, city, lat, lon = get_weather(zip_code, weather_api_key)

    if weather_condition and city:
        st.subheader(f"📍 Location: {zip_code} - {city}")
        st.info(f"{weather_condition}, {temp}°F")

        # Get traffic data
        traffic_data = get_traffic_data(lat, lon, here_api_key)
        traffic_status = "Congested" if any(
            flow_segment['CURRENT_SPEED'] < flow_segment['FREE_FLOW_SPEED']
            for flow_segment in traffic_data['RWS'][0]['RW'][0]['FIS'][0]['FI']
        ) else "Clear"
        st.subheader("🚦 Traffic Status")
        st.write(traffic_status)

        st.subheader("🕑 Current Local Time")
        st.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        st.subheader("💡 Recommended Earning Mode")
        recommendation = recommend_earning_mode(current_hour, weather_condition, traffic_data)
        st.success(recommendation)
    else:
        st.warning("Unable to fetch complete data; try again later.")
