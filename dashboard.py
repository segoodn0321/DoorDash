import streamlit as st
import requests
import jwt
import math
import time
from datetime import datetime

# Load API keys securely from Streamlit secrets
weather_api_key = st.secrets["openweathermap"]["api_key"]
doordash_credentials = {
    "developer_id": st.secrets["doordash"]["developer_id"],
    "key_id": st.secrets["doordash"]["key_id"],
    "signing_secret": st.secrets["doordash"]["signing_secret"]
}

# Function to generate JWT token for DoorDash
def generate_doordash_jwt(creds):
    payload = {
        "aud": "doordash",
        "iss": creds["developer_id"],
        "kid": creds["key_id"],
        "exp": math.floor(time.time() + 300),  # Token valid for 5 mins
        "iat": math.floor(time.time()),
    }
    token = jwt.encode(
        payload,
        jwt.utils.base64url_decode(creds["signing_secret"]),
        algorithm="HS256",
        headers={"dd-ver": "DD-JWT-V1"}
    )
    return token if isinstance(token, str) else token.decode('utf-8')

# Fetch weather and city data
def get_weather(zip_code, api_key):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?zip={zip_code},us&appid={api_key}&units=imperial"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        weather_condition = data['weather'][0]['main']
        temperature = data['main']['temp']
        city = data['name']
        return weather_condition, temperature, city
    except requests.RequestException as e:
        st.error(f"Weather API error: {e}")
        return None, None, None

# Fetch DoorDash delivery stats
def fetch_doordash_data(zip_code, token):
    url = f"https://openapi.doordash.com/drive/v2/market/{zip_code}/delivery_stats"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"DoorDash API Error: {e}")
        return None

# Recommend earning mode based on current data
def recommend_earning_mode(dd_data, current_hour, weather_condition):
    peak_hours = [11, 12, 13, 17, 18, 19, 20, 21]
    high_volume_threshold = 50
    active_orders = dd_data.get('active_deliveries', 0)

    if weather_condition in ["Rain", "Snow", "Thunderstorm"]:
        return "Earn per Order (High Weather Demand)"
    elif active_orders >= high_volume_threshold or current_hour in peak_hours:
        return "Earn per Order (High Demand)"
    else:
        return "Earn by Time (Moderate/Low Demand)"

# --- Streamlit App ---
st.title("🚗 DoorDash Earnings Optimizer")

zip_code = st.text_input("Enter Zip Code:", "28409")

if st.button("Search"):
    current_hour = datetime.now().hour

    # Generate JWT token (put this call right here)
    jwt_token = generate_doordash_jwt(doordash_credentials)

    # Fetch data
    weather_condition, temp, city = get_weather(zip_code, weather_api_key)
    dd_data = fetch_doordash_data(zip_code, jwt_token)

    # Display Results
    if city:
        st.subheader(f"📍 Location: {zip_code} - {city}")
    else:
        st.subheader(f"📍 Location: {zip_code}")

    if weather_condition:
        st.subheader("🌦️ Current Weather")
        st.info(f"{weather_condition}, {temp}°F")

    if dd_data:
        active_orders = dd_data.get('active_deliveries', 'Unavailable')
        st.subheader("🚗 Current DoorDash Volume")
        st.metric("Active Deliveries", active_orders)

        recommendation = recommend_earning_mode(dd_data, current_hour, weather_condition)
        st.subheader("💡 Recommended Earning Mode")
        st.success(recommendation)
    else:
        st.warning("DoorDash data not available. Check API credentials or endpoint.")

    st.subheader("🕑 Current Time")
    st.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
