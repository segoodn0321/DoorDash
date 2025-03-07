import streamlit as st
import requests
from datetime import datetime

# API Key configuration (replace with your key)
WEATHER_API_KEY = 'your_openweathermap_api_key'

# Fetch weather information for a given zip code
def get_weather(zip_code):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?zip={zip_code},us&appid={WEATHER_API_KEY}&units=imperial"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        condition = data['weather'][0]['main']
        temperature = data['main']['temp']
        return f"{condition}, {temperature}°F"
    except Exception as e:
        return f"Unable to fetch weather ({e})"

# Simple recommendation based on common DoorDash peak hours
def recommend_earning_mode(current_hour, weather_condition):
    # Peak meal times typically good for 'Earn per Order'
    if (11 <= current_hour <= 14) or (17 <= current_hour <= 21):
        mode = "Earn per Order"
    else:
        mode = "Earn by Time"
    
    # Adjust recommendation if weather is unfavorable
    if weather_condition in ['Rain', 'Snow', 'Thunderstorm']:
        mode_note = f"High demand likely due to {weather_condition}, strongly consider 'Earn per Order'."
    else:
        mode_note = "Typical demand conditions."

    return mode_note, mode_note

# Streamlit App Interface
st.title("🚗 DoorDash Earnings Optimizer")

zip_code = st.text_input("Enter Zip Code:", value="28409")

if st.button("Search"):
    current_hour = datetime.now().hour
    weather = get_weather(zip_code)

    mode, note = recommend_earning_mode(current_hour, weather)

    st.subheader(f"📍 Current Weather in {zip_code}")
    st.info(weather)

    st.subheader("🕑 Current Local Time")
    st.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    st.subheader("💡 Earning Mode Recommendation")
    if "Unable to fetch" in weather:
        st.error("Cannot determine recommendation without weather data.")
    else:
        st.success(mode_note)

        st.write(f"**Reasoning:** {mode_note}")
