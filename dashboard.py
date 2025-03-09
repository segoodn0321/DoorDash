import streamlit as st
import requests
import datetime
import pandas as pd
import joblib
import bcrypt
import os
import pytz
import json
from sklearn.ensemble import RandomForestRegressor

# File to store user credentials
USER_CREDENTIALS_FILE = "user_credentials.json"

# Load or create user credentials database
def load_user_credentials():
    if os.path.exists(USER_CREDENTIALS_FILE):
        with open(USER_CREDENTIALS_FILE, "r") as file:
            return json.load(file)
    return {}

# Save user credentials
def save_user_credentials(credentials):
    with open(USER_CREDENTIALS_FILE, "w") as file:
        json.dump(credentials, file)

# Register a new user
def register_user(username, password):
    credentials = load_user_credentials()

    if username in credentials:
        return False, "Username already exists!"

    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    credentials[username] = hashed_password
    save_user_credentials(credentials)

    return True, "✅ Account created successfully! Please log in."

# Authenticate user
def login_user(username, password):
    credentials = load_user_credentials()

    if username not in credentials:
        return False, "❌ Username not found. Please register first."

    stored_hash = credentials[username].encode()

    if bcrypt.checkpw(password.encode(), stored_hash):
        return True, "✅ Login successful!"

    return False, "❌ Incorrect password."

# Auto-detect user location and timezone
@st.cache_data
def get_location():
    response = requests.get("https://ipinfo.io/json").json()
    city = response.get("city", "Unknown City")
    lat, lon = response["loc"].split(",")
    timezone = response.get("timezone", "UTC")
    return city, lat, lon, timezone

CITY, LATITUDE, LONGITUDE, USER_TIMEZONE = get_location()
LOCAL_TZ = pytz.timezone(USER_TIMEZONE)

# API Keys (Replace with your own)
OPENWEATHER_API_KEY = "your_openweather_api_key"
GOOGLE_MAPS_API_KEY = "your_google_maps_api_key"

# Fetch real-time weather data
@st.cache_data
def get_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={LATITUDE}&lon={LONGITUDE}&appid={OPENWEATHER_API_KEY}&units=imperial"
    response = requests.get(url).json()
    return response["weather"][0]["description"], response["main"]["temp"], response["wind"]["speed"]

# Fetch real-time traffic data
@st.cache_data
def get_traffic():
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={LATITUDE},{LONGITUDE}&destinations={LATITUDE},{LONGITUDE}&departure_time=now&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(url).json()
    try:
        return response["rows"][0]["elements"][0]["duration_in_traffic"]["value"] / 60
    except KeyError:
        return "Unknown"

# Load user-specific earnings data
def load_earnings_data(username):
    file_path = f"{username}_earnings.csv"
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return pd.DataFrame(columns=["date", "start_hour", "end_hour", "earnings", "weather", "traffic"])

# Save earnings data
def save_earnings_data(username, start_time, end_time, earnings):
    df = load_earnings_data(username)

    date = datetime.datetime.now(LOCAL_TZ).strftime("%Y-%m-%d")
    weather, temp, wind = get_weather()
    traffic = get_traffic()

    new_data = pd.DataFrame([{
        "date": date,
        "start_hour": start_time,
        "end_hour": end_time,
        "earnings": earnings,
        "weather": weather,
        "traffic": traffic
    }])

    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(f"{username}_earnings.csv", index=False)

# Train AI model per user
def train_model(username):
    df = load_earnings_data(username)
    if len(df) < 10:
        return "❌ Not enough data to train AI model. Log more shifts first."

    df["start_hour"] = pd.to_datetime(df["start_hour"], format="%I:%M %p").dt.hour
    df["weather_score"] = df["weather"].apply(lambda x: 1 if "rain" in x.lower() else 0)
    df["traffic_score"] = df["traffic"].apply(lambda x: 1 if x > 20 else 0)

    X, y = df[["start_hour", "weather_score", "traffic_score"]], df["earnings"]
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    joblib.dump(model, f"{username}_predictor.pkl")
    return "✅ AI model trained successfully!"

# Predict best time to drive
def predict_best_time(username):
    try:
        model = joblib.load(f"{username}_predictor.pkl")
    except FileNotFoundError:
        return "❌ AI model not trained yet. Log more shifts first."

    hours = list(range(10, 23))
    weather, temp, wind = get_weather()
    traffic = get_traffic()
    predictions = [(hour, model.predict([[hour, 1 if "rain" in weather.lower() else 0, 1 if traffic > 20 else 0]])[0]) for hour in hours]

    return max(predictions, key=lambda x: x[1])

# Streamlit UI
st.title("🚗 DoorDash AI Driver Assistant")
st.subheader(f"📍 Location: {CITY}, Timezone: {USER_TIMEZONE}")

# Login/Register System
if "username" not in st.session_state:
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            success, message = login_user(username, password)
            if success:
                st.session_state["username"] = username
                st.experimental_rerun()
            else:
                st.error(message)
    
    with tab2:
        new_username = st.text_input("New Username", key="reg_user")
        new_password = st.text_input("New Password", type="password", key="reg_pass")
        if st.button("Register"):
            success, message = register_user(new_username, new_password)
            if success:
                st.success(message)
            else:
                st.error(message)

# After login
if "username" in st.session_state:
    st.success(f"Welcome, {st.session_state['username']}!")

    start_time = st.text_input("Shift Start Time (HH:MM AM/PM)")
    end_time = st.text_input("Shift End Time (HH:MM AM/PM)")
    earnings = st.number_input("Total Earnings ($)", min_value=0.0)

    if st.button("Log Shift"):
        save_earnings_data(st.session_state["username"], start_time, end_time, earnings)
        st.success("Shift logged successfully!")

    if st.button("Train AI Model"):
        st.success(train_model(st.session_state["username"]))

    if st.button("Check Best Time to Drive"):
        st.success(f"📊 Best time to drive: {predict_best_time(st.session_state['username'])}")
