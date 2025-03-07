import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- API KEYS ---
WEATHER_API_KEY = '8a0599888629317497a67f540215a4fc'
DOORDASH_API_KEY = 'import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- API KEYS ---
WEATHER_API_KEY = '8a0599888629317497a67f540215a4fc'
DOORDASH_API_KEY = 'import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- API KEYS ---
WEATHER_API_KEY = '8a0599888629317497a67f540215a4fc'
DOORDASH_API_KEY = 'a2677a32-0908-4751-98af-cd847ab5be19'

# --- Fetch Weather Data ---
def get_weather(zip_code):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?zip={zip_code},us&appid={WEATHER_API_KEY}&units=imperial"
        response = requests.get(url)
        response.raise_for_status()
        weather_data = response.json()
        condition = weather_data['weather'][0]['main']
        temp = weather_data['main']['temp']
        return f"{condition}, {temp}°F"
    except requests.RequestException as e:
        return f"Weather API Error: {e}"

# --- Fetch DoorDash Data ---
def fetch_doordash_data(zip_code):
    headers = {'Authorization': f'Bearer {DOORDASH_API_KEY}'}
    url = f'https://api.doordash.com/v1/market/{zip_code}/order_volume'
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get('hourly_orders', [])
    except requests.RequestException as e:
        st.error(f"DoorDash API Error: {e}")
        return []

# --- Analyze Peak Hours ---
def analyze_peak_hours(hourly_orders):
    if not hourly_orders:
        return None
    df = pd.DataFrame(hourly_orders)
    df['time'] = pd.to_datetime(df['time'])
    peak_hour = df.groupby(df['time'].dt.hour)['orders'].sum().idxmax()
    return peak_hour

# --- Recommend Earning Mode ---
def recommend_earning_mode(current_hour, peak_hour):
    if peak_hour is None:
        return "Insufficient data to recommend earning mode."
    return "Earn per Order" if abs(current_hour - peak_hour) <= 1 else "Earn by Time"

# --- Streamlit Dashboard ---
st.title("🚗 DoorDash Earnings Optimizer")

zip_code = st.text_input("Enter Zip Code:", "28409")

if st.button("Search"):
    with st.spinner("Fetching data..."):
        weather_info = get_weather(zip_code)
        hourly_orders = fetch_doordash_data(zip_code)
        peak_hour = analyze_peak_hours(hourly_orders)
        current_hour = datetime.now().hour
        recommendation = recommend_earning_mode(current_hour, peak_hour)

    # --- Results Display ---
    st.subheader(f"📍 Weather in {zip_code}")
    st.info(weather_info)

    st.subheader("📈 DoorDash Peak Hour")
    if peak_hour is not None:
        st.metric(label="Peak Order Hour", value=f"{peak_hour}:00")
    else:
        st.warning("No historical DoorDash data available for this location.")

    st.subheader("🕑 Current Time")
    st.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    st.subheader("💰 Recommended Earning Mode")
    if "Insufficient data" in recommendation:
        st.error(recommendation)
    else:
        st.success(recommendation)'

# --- Fetch Weather Data ---
def get_weather(zip_code):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?zip={zip_code},us&appid={WEATHER_API_KEY}&units=imperial"
        response = requests.get(url)
        response.raise_for_status()
        weather_data = response.json()
        condition = weather_data['weather'][0]['main']
        temp = weather_data['main']['temp']
        return f"{condition}, {temp}°F"
    except requests.RequestException as e:
        return f"Weather API Error: {e}"

# --- Fetch DoorDash Data ---
def fetch_doordash_data(zip_code):
    headers = {'Authorization': f'Bearer {DOORDASH_API_KEY}'}
    url = f'https://api.doordash.com/v1/market/{zip_code}/order_volume'
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get('hourly_orders', [])
    except requests.RequestException as e:
        st.error(f"DoorDash API Error: {e}")
        return []

# --- Analyze Peak Hours ---
def analyze_peak_hours(hourly_orders):
    if not hourly_orders:
        return None
    df = pd.DataFrame(hourly_orders)
    df['time'] = pd.to_datetime(df['time'])
    peak_hour = df.groupby(df['time'].dt.hour)['orders'].sum().idxmax()
    return peak_hour

# --- Recommend Earning Mode ---
def recommend_earning_mode(current_hour, peak_hour):
    if peak_hour is None:
        return "Insufficient data to recommend earning mode."
    return "Earn per Order" if abs(current_hour - peak_hour) <= 1 else "Earn by Time"

# --- Streamlit Dashboard ---
st.title("🚗 DoorDash Earnings Optimizer")

zip_code = st.text_input("Enter Zip Code:", "28409")

if st.button("Search"):
    with st.spinner("Fetching data..."):
        weather_info = get_weather(zip_code)
        hourly_orders = fetch_doordash_data(zip_code)
        peak_hour = analyze_peak_hours(hourly_orders)
        current_hour = datetime.now().hour
        recommendation = recommend_earning_mode(current_hour, peak_hour)

    # --- Results Display ---
    st.subheader(f"📍 Weather in {zip_code}")
    st.info(weather_info)

    st.subheader("📈 DoorDash Peak Hour")
    if peak_hour is not None:
        st.metric(label="Peak Order Hour", value=f"{peak_hour}:00")
    else:
        st.warning("No historical DoorDash data available for this location.")

    st.subheader("🕑 Current Time")
    st.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    st.subheader("💰 Recommended Earning Mode")
    if "Insufficient data" in recommendation:
        st.error(recommendation)
    else:
        st.success(recommendation)'

# --- Fetch Weather Data ---
def get_weather(zip_code):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?zip={zip_code},us&appid={WEATHER_API_KEY}&units=imperial"
        response = requests.get(url)
        response.raise_for_status()
        weather_data = response.json()
        condition = weather_data['weather'][0]['main']
        temp = weather_data['main']['temp']
        return f"{condition}, {temp}°F"
    except requests.RequestException as e:
        return f"Weather API Error: {e}"

# --- Fetch DoorDash Data ---
def fetch_doordash_data(zip_code):
    headers = {'Authorization': f'Bearer {DOORDASH_API_KEY}'}
    url = f'https://api.doordash.com/v1/market/{zip_code}/order_volume'
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get('hourly_orders', [])
    except requests.RequestException as e:
        st.error(f"DoorDash API Error: {e}")
        return []

# --- Analyze Peak Hours ---
def analyze_peak_hours(hourly_orders):
    if not hourly_orders:
        return None
    df = pd.DataFrame(hourly_orders)
    df['time'] = pd.to_datetime(df['time'])
    peak_hour = df.groupby(df['time'].dt.hour)['orders'].sum().idxmax()
    return peak_hour

# --- Recommend Earning Mode ---
def recommend_earning_mode(current_hour, peak_hour):
    if peak_hour is None:
        return "Insufficient data to recommend earning mode."
    return "Earn per Order" if abs(current_hour - peak_hour) <= 1 else "Earn by Time"

# --- Streamlit Dashboard ---
st.title("🚗 DoorDash Earnings Optimizer")

zip_code = st.text_input("Enter Zip Code:", "28409")

if st.button("Search"):
    with st.spinner("Fetching data..."):
        weather_info = get_weather(zip_code)
        hourly_orders = fetch_doordash_data(zip_code)
        peak_hour = analyze_peak_hours(hourly_orders)
        current_hour = datetime.now().hour
        recommendation = recommend_earning_mode(current_hour, peak_hour)

    # --- Results Display ---
    st.subheader(f"📍 Weather in {zip_code}")
    st.info(weather_info)

    st.subheader("📈 DoorDash Peak Hour")
    if peak_hour is not None:
        st.metric(label="Peak Order Hour", value=f"{peak_hour}:00")
    else:
        st.warning("No historical DoorDash data available for this location.")

    st.subheader("🕑 Current Time")
    st.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    st.subheader("💰 Recommended Earning Mode")
    if "Insufficient data" in recommendation:
        st.error(recommendation)
    else:
        st.success(recommendation)
