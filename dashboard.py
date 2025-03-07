import streamlit as st
import requests
from datetime import datetime

# --- API Keys ---
WEATHER_API_KEY = '28228f6dd7c6a9b575000a82351d4d0c'
DOORDASH_API_KEY = '9470937d-e624-4730-ab81-00cade3edbd3'

# Fetch weather and city from OpenWeatherMap
def get_weather_and_city(zip_code):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?zip={zip_code},us&appid={WEATHER_API_KEY}&units=imperial"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        condition = data['weather'][0]['main']
        temp = data['main']['temp']
        city = data['name']
        return f"{condition}, {temp}°F", city
    except requests.RequestException as e:
        return None, f"Weather API error: {e}"

# Fetch DoorDash data with proper Bearer authorization
def fetch_doordash_volume(zip_code):
    url = f"https://openapi.doordash.com/drive/v2/market/{zip_code}/delivery_stats"
    headers = {
        "Authorization": f"Bearer {DOORDASH_API_KEY}"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.RequestException as e:
        return {"error": str(e)}

# Recommend earning mode based on DoorDash and weather data
def recommend_earning_mode(dd_data, current_hour, weather_condition):
    high_volume_threshold = 50  # Set according to your experience

    current_orders = dd_data.get('active_deliveries', 0)

    peak_hours = [11, 12, 13, 17, 18, 19, 20, 21]
    if weather_condition in ["Rain", "Snow", "Thunderstorm"]:
        return "Earn per Order (High Demand - Bad Weather)"
    elif current_orders >= high_volume_threshold or current_hour in peak_hours:
        return "Earn per Order (High Order Volume)"
    else:
        return "Earn by Time (Moderate/Low Volume)"

# --- Streamlit Interface ---
st.title("🚗 DoorDash Earnings Optimizer")

zip_code = st.text_input("Enter Zip Code:", "28409")

if st.button("Search"):
    weather_info, city_or_error = get_weather_and_city(zip_code)
    dd_data = fetch_doordash_volume(zip_code)
    current_hour = datetime.now().hour

    # Display City Name
    if weather_info:
        st.subheader(f"📍 Location: {zip_code} - {city_or_error}")
    else:
        st.subheader(f"📍 Location: {zip_code} (City Unavailable)")
        st.error(city_or_error)

    # Display Weather Info
    st.subheader("🌦️ Current Weather")
    if weather_info:
        st.info(weather_info)
        weather_condition = weather_info.split(",")[0]
    else:
        weather_condition = "Unknown"
        st.error("Unable to fetch weather.")

    # DoorDash Volume Info
    st.subheader("🚗 DoorDash Current Volume")
    if "error" not in dd_data:
        active_deliveries = dd_data.get('active_deliveries', 'Data unavailable')
        st.metric("Active Deliveries Now", active_deliveries)
    else:
        active_deliveries = None
        st.error(f"DoorDash API Error: {dd_data['error']}")

    # Current Time Display
    st.subheader("🕑 Current Local Time")
    st.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Earnings Mode Recommendation
    st.subheader("💡 Recommended Earning Mode")
    if weather_info and active_deliveries is not None:
        recommendation = recommend_earning_mode(dd_data, current_hour, weather_condition)
        st.success(recommendation)
    else:
        st.warning("Insufficient data to determine earning mode.")
