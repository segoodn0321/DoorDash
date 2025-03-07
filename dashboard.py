import streamlit as st
import requests
from datetime import datetime

# --- API Configuration ---
WEATHER_API_KEY = '28228f6dd7c6a9b575000a82351d4d0c'
DOORDASH_API_KEY = '9470937d-e624-4730-ab81-00cade3edbd3'

# Fetch weather and city name from OpenWeatherMap
def get_weather_and_city(zip_code):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?zip={zip_code},us&appid={WEATHER_API_KEY}&units=imperial"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        condition = data['weather'][0]['main']
        temperature = data['main']['temp']
        city = data['name']
        return f"{condition}, {temperature}°F", city
    except requests.RequestException as e:
        return None, f"Weather API Error: {e}"

# Fetch real-time DoorDash data
def get_doordash_data(zip_code):
    headers = {'Authorization': f'Bearer {DOORDASH_API_KEY}'}
    url = f"https://openapi.doordash.com/drive/v2/market/{zip_code}/delivery_stats"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}

# Recommend earning mode based on current DoorDash volume
def recommend_earning_mode(doordash_data, current_hour, weather_condition):
    high_volume_threshold = 50  # Example threshold; adjust based on your observations

    current_orders = doordash_data.get('active_deliveries', 0)

    peak_hours = [11, 12, 13, 17, 18, 19, 20, 21]
    if weather_condition in ["Rain", "Snow", "Thunderstorm"]:
        return "Earn per Order (High demand due to weather conditions)"
    elif current_orders >= high_volume_threshold or current_hour in peak_hours:
        return "Earn per Order (High order volume)"
    else:
        return "Earn by Time (Moderate or low order volume)"

# --- Streamlit UI ---
st.title("🚗 DoorDash Earnings Optimizer")

zip_code = st.text_input("Enter Zip Code:", "28409")

if st.button("Search"):
    weather_info, city_or_error = get_weather_and_city(zip_code)
    current_hour = datetime.now().hour

    st.subheader("📍 Location")
    if weather_info:
        st.info(f"{zip_code} - {city_or_error}")
    else:
        st.error(city_or_error)

    # Fetch DoorDash data
    doordash_data = get_doordash_data(zip_code)

    st.subheader("🌦️ Current Weather")
    if weather_info:
        st.success(weather_info)
    else:
        st.error("Weather data unavailable.")

    st.subheader("🚗 DoorDash Current Order Volume")
    if "error" not in doordash_data:
        current_orders = doordash_data.get('active_deliveries', 'Unavailable')
        st.metric(label="Active Deliveries Right Now", value=current_orders)
    else:
        st.error(f"DoorDash API Error: {doordash_data['error']}")

    st.subheader("🕑 Current Local Time")
    st.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    st.subheader("💡 Recommended Earning Mode")
    if weather_info and "error" not in doordash_data:
        weather_condition = weather_info.split(",")[0]
        recommendation = recommend_earning_mode(doordash_data, current_hour, weather_condition)
        st.success(recommendation)
    else:
        st.warning("Insufficient data to provide recommendation.")
