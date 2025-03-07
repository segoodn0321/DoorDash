import streamlit as st
import requests
import jwt
import math
import time
from datetime import datetime

# Securely load API keys
weather_api_key = st.secrets["openweathermap"]["api_key"]
doordash_creds = st.secrets["doordash"]

# JWT Token Generation for DoorDash
def generate_doordash_jwt(creds):
    payload = {
        "aud": "doordash",
        "iss": creds["developer_id"],
        "kid": creds["key_id"],
        "exp": math.floor(time.time() + 300),
        "iat": math.floor(time.time()),
    }
    token = jwt.encode(
        payload,
        jwt.utils.base64url_decode(creds["signing_secret"]),
        algorithm="HS256",
        headers={"dd-ver": "DD-JWT-V1"}
    )
    return token if isinstance(token, str) else token.decode('utf-8')

# Fetch weather and city information
def get_weather(zip_code, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?zip={zip_code},us&appid={api_key}&units=imperial"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    condition = data['weather'][0]['main']
    temp = data['main']['temp']
    city = data['name']
    return condition, temp, city

# Fetch DoorDash market data
def fetch_doordash_data(zip_code, token):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://openapi.doordash.com/drive/v2/market/{zip_code}/delivery_stats"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

# Earning mode recommendation logic
def recommend_earning_mode(dd_data, current_hour, weather_condition):
    peak_hours = [11, 12, 13, 17, 18, 19, 20, 21]
    high_volume_threshold = 50
    active_orders = dd_data.get('active_deliveries', 0)

    if weather_condition in ["Rain", "Snow", "Thunderstorm"]:
        return "Earn per Order (High Demand: Weather)"
    elif active_orders >= high_volume_threshold or current_hour in peak_hours:
        return "Earn per Order (Peak Demand)"
    else:
        return "Earn by Time (Normal/Low Demand)"

# Streamlit App UI
st.title("🚗 DoorDash Earnings Optimizer")

zip_code = st.text_input("Enter Zip Code:", "28409")

if st.button("Search"):
    current_hour = datetime.now().hour

    try:
        weather_condition, temp, city = get_weather(zip_code, weather_api_key)
        st.subheader(f"📍 Location: {zip_code} - {city}")
        st.info(f"{weather_condition}, {temp}°F")
    except Exception as e:
        st.error(f"Weather API error: {e}")
        weather_condition = None

    # Generate JWT token and fetch DoorDash data
    token = generate_doordash_jwt(doordash_creds)
    try:
        dd_data = fetch_doordash_data(zip_code, token)
        active_orders = dd_data.get('active_deliveries', 'Unavailable')
        st.subheader("🚗 DoorDash Current Volume")
        st.metric("Active Deliveries", active_orders)
    except Exception as e:
        dd_data = None
        st.error(f"DoorDash API error: {e}")

    # Current time display
    st.subheader("🕑 Current Local Time")
    st.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Earnings Recommendation
    st.subheader("💡 Recommended Earning Mode")
    if dd_data and weather_condition:
        recommendation = recommend_earning_mode(dd_data, current_hour, weather_condition)
        st.success(recommendation)
    else:
        st.warning("Insufficient data to make a recommendation.")
