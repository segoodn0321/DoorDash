import streamlit as st
import requests
from datetime import datetime

# --- API Configuration ---
WEATHER_API_KEY = '28228f6dd7c6a9b575000a82351d4d0c'

# Fetch weather data
def get_weather(zip_code):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?zip={zip_code},us&appid={WEATHER_API_KEY}&units=imperial"
        response = requests.get(url)
        response.raise_for_status()
        weather_data = response.json()
        condition = weather_data['weather'][0]['main']
        temp = weather_data['main']['temp']
        return f"{condition}, {temp}°F"
    except Exception as e:
        return f"Unable to fetch weather ({e})"

# Recommend earning mode based on time & weather
def recommend_earning_mode(current_hour, weather_condition):
    peak_hours = [11, 12, 13, 17, 18, 19, 20, 21]  # Typical busy hours
    if current_hour in peak_hours:
        recommendation = "Earn per Order"
    else:
        recommendation = "Earn by Time"

    if weather_condition.lower() in ['Rain', 'Snow', 'Thunderstorm']:
        additional_note = "High demand expected due to weather. Consider 'Earn per Order'."
    else:
        recommendation_note = "Normal demand conditions."

    return recommendation, weather_condition

## 🛠️ **Here’s the fully corrected Streamlit Dashboard (`dashboard.py`):**

```python
import streamlit as st
import requests
from datetime import datetime

# API Key (Replace this with your actual OpenWeatherMap API key)
WEATHER_API_KEY = 'your_openweathermap_api_key'

# Fetch weather
def get_weather(zip_code):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?zip={zip_code},us&appid={WEATHER_API_KEY}&units=imperial"
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
        weather = data['weather'][0]['main']
        temperature = data['main']['temp']
        return f"{weather}, {temperature}°F"
    except requests.RequestException as e:
        return f"Weather fetch error: {e}"

# Recommend mode based on time and weather
def recommend_earning_mode(current_hour, weather):
    busy_hours = [11, 12, 13, 17, 18, 19, 20, 21]
    if "Rain" in weather or "Snow" in weather:
        return "Earn per Order (High demand due to weather)"
    elif current_hour in peak_hours:
        return "Earn per Order"
    else:
        return "Earn by Time"

# Streamlit App
st.title("🚗 DoorDash Earnings Optimizer")

zip_code = st.text_input("Enter Zip Code:", "28409")

if st.button("Search"):
    weather = get_weather(zip_code)
    current_hour = datetime.now().hour

    st.subheader(f"📍 Weather in {zip_code}")
    st.info(weather)

    st.subheader("🕑 Current Time")
    st.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    st.subheader("💡 Recommended Earning Mode")
    if "error" in weather.lower():
        st.error("Cannot give recommendation without weather data.")
    else:
        recommendation = recommend_earning_mode(current_hour=datetime.now().hour, weather=weather)
        st.success(recommendation)
