import streamlit as st
import requests
import datetime
import pandas as pd
import joblib
import pytz
import os
from sklearn.ensemble import RandomForestRegressor

# Constants
EARNINGS_FILE = "driver_earnings.csv"

# **Auto-detect user’s actual location**
def get_actual_location():
    try:
        response = requests.get("https://ipinfo.io/json").json()
        city = response.get("city", "Unknown City")
        lat, lon = response["loc"].split(",")
        timezone = response.get("timezone", "UTC")
        return city, lat, lon, timezone
    except Exception:
        return "Unknown City", "0", "0", "UTC"

CITY, LATITUDE, LONGITUDE, USER_TIMEZONE = get_actual_location()
LOCAL_TZ = pytz.timezone(USER_TIMEZONE)

# API Keys (Replace with your own)
OPENWEATHER_API_KEY = "your_openweather_api_key"
GOOGLE_MAPS_API_KEY = "your_google_maps_api_key"

# **Fetch live weather for user’s actual location**
def get_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={LATITUDE}&lon={LONGITUDE}&appid={OPENWEATHER_API_KEY}&units=imperial"
    response = requests.get(url).json()
    return response["weather"][0]["description"], response["main"]["temp"], response["wind"]["speed"]

# **Fetch live traffic for user’s location**
def get_traffic():
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={LATITUDE},{LONGITUDE}&destinations={LATITUDE},{LONGITUDE}&departure_time=now&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(url).json()
    try:
        return response["rows"][0]["elements"][0]["duration_in_traffic"]["value"] / 60
    except KeyError:
        return "Unknown"

# **Load earnings data**
def load_earnings_data():
    if os.path.exists(EARNINGS_FILE):
        return pd.read_csv(EARNINGS_FILE)
    return pd.DataFrame(columns=["date", "start_hour", "end_hour", "earnings", "weather", "traffic"])

# **Save earnings data**
def save_earnings_data(start_time, end_time, earnings):
    df = load_earnings_data()
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
    df.to_csv(EARNINGS_FILE, index=False)

# **Train AI model**
def train_model():
    df = load_earnings_data()
    if len(df) < 10:
        return "❌ Not enough data to train AI model. Log more shifts first."

    df["start_hour"] = pd.to_datetime(df["start_hour"], format="%I:%M %p").dt.hour
    df["weather_score"] = df["weather"].apply(lambda x: 1 if "rain" in x.lower() else 0)
    df["traffic_score"] = df["traffic"].apply(lambda x: 1 if x > 20 else 0)

    X, y = df[["start_hour", "weather_score", "traffic_score"]], df["earnings"]
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    joblib.dump(model, "earnings_predictor.pkl")
    return "✅ AI model trained successfully!"

# **Predict best time to drive**
def predict_best_time():
    try:
        model = joblib.load("earnings_predictor.pkl")
    except FileNotFoundError:
        return "❌ AI model not trained yet. Log more shifts first."

    hours = list(range(10, 23))  # Predict from 10 AM to 11 PM
    weather, temp, wind = get_weather()
    traffic = get_traffic()

    predictions = [(hour, model.predict([[hour, 1 if "rain" in weather.lower() else 0, 1 if traffic > 20 else 0]])[0]) for hour in hours]

    return max(predictions, key=lambda x: x[1])

# **Streamlit UI**
st.title("🚗 DoorDash AI Driver Assistant")
st.subheader(f"📍 Current Location: {CITY}, Timezone: {USER_TIMEZONE}")

start_time = st.text_input("Shift Start Time (HH:MM AM/PM)")
end_time = st.text_input("Shift End Time (HH:MM AM/PM)")
earnings = st.number_input("Total Earnings ($)", min_value=0.0)

if st.button("Log Shift"):
    save_earnings_data(start_time, end_time, earnings)
    st.success("Shift logged successfully!")

if st.button("Train AI Model"):
    st.success(train_model())

if st.button("Check Best Time to Drive"):
    st.success(f"📊 Best time to drive: {predict_best_time()}")
