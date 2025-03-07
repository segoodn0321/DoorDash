import streamlit as st
import requests
from datetime import datetime

# Load API keys securely from Streamlit secrets
weather_api_key = st.secrets["openweathermap"]["api_key"]
here_api_key = st.secrets["here"]["api_key"]

# Fetch weather, city, and coordinates from OpenWeatherMap
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

# Fetch real-time traffic data from HERE API
def get_traffic_data(lat, lon, api_key):
    url = f"https://traffic.ls.hereapi.com/traffic/6.3/flow.json?prox={lat},{lon},1000&apiKey={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.RequestException as e:
        st.error(f"Traffic API error: {e}")
        return None

# Recommend earning mode based on time, weather, and traffic conditions
def recommend_earning_mode(current_hour, weather_condition, traffic_data):
    peak_hours = [11, 12, 13, 17, 18, 19, 20, 21]

    # Determine traffic congestion
    traffic_congested = False
    if traffic_data and "RWS" in traffic_data:
        for road in traffic_data["RWS"]:
            for segment in road["RW"]:
                for flow_info in segment.get("FIS", []):
                    for flow in flow_info.get("FI", []):
                        if flow["CF"][0]["SP"] < flow["CF"][0]["FF"]:
                            traffic_congested = True
                            break

    # Define earning strategy
    if weather_condition in ["Rain", "Snow", "Thunderstorm"]:
        return "Earn per Order (High Demand - Weather)"
    elif traffic_congested:
        return "Earn by Time (High Traffic Congestion)"
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
            traffic_data = get_traffic_data(lat, lon, here_api_key)
            traffic_status = "Congested" if traffic_data else "Clear"
            st.subheader("🚦 Traffic Status")
            st.write(traffic_status)

            st.subheader("💡 Recommended Earning Mode")
            recommendation = recommend_earning_mode(current_hour, weather_condition, traffic_data)
            st.success(recommendation)

        with st.expander("🛰️ Live Weather Map"):
            map_url = f"https://openweathermap.org/weathermap?basemap=map&cities=true&layer=precipitation&lat={lat}&lon={lon}&zoom=11"
            st.markdown(f'<iframe src="{map_url}" width="100%" height="500"></iframe>', unsafe_allow_html=True)

    else:
        st.error("Could not fetch weather or location data. Please check the Zip Code.")
