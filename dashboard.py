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

# **Ask user for ZIP Code**
st.title("🚗 DoorDash AI Driver Assistant")
zip_code = st.text_input("Enter your ZIP code (5 digits):", max_chars=5)

# **Fetch latitude & longitude using Google Maps API (more reliable)**
def get_lat_lon(zip_code):
    try:
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={zip_code},US&key=your_google_maps_api_key"
        response = requests.get(url).json()
        if "results" in response and len(response["results"]) > 0:
            location = response["results"][0]["geometry"]["location"]
            return location["lat"], location["lng"]
    except Exception as e:
        print("Error fetching lat/lon:", e)
    return None, None

LATITUDE, LONGITUDE = None, None
if zip_code:
    LATITUDE, LONGITUDE = get_lat_lon(zip_code)
    if LATITUDE and LONGITUDE:
        st.success(f"🌍 Location detected! Using ZIP code {zip_code}")
    else:
        st.error("⚠️ Invalid ZIP code or API issue. Please try again.")

# **Get timezone based on ZIP code**
def get_timezone(lat, lon):
    try:
        url = f"https://maps.googleapis.com/maps/api/timezone/json?location={lat},{lon}&timestamp={int(datetime.datetime.utcnow().timestamp())}&key=your_google_maps_api_key"
        response = requests.get(url).json()
        return response.get("timeZoneId", "UTC")
    except:
        return "UTC"

# **Ensure ZIP is entered before fetching timezone**
USER_TIMEZONE = "UTC"
LOCAL_TZ = pytz.timezone(USER_TIMEZONE)
if LATITUDE and LONGITUDE:
    USER_TIMEZONE = get_timezone(LATITUDE, LONGITUDE)
    LOCAL_TZ = pytz.timezone(USER_TIMEZONE)

# **Fetch real-time weather for user's ZIP code**
def get_weather():
    if LATITUDE and LONGITUDE:
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={LATITUDE}&lon={LONGITUDE}&appid=your_openweather_api_key&units=imperial"
        response = requests.get(url).json()
        if "weather" in response:
            return response["weather"][0]["description"], response["main"]["temp"], response["wind"]["speed"]
    return "Unknown", "N/A", "N/A"

# **Fetch real-time traffic for user's ZIP code**
def get_traffic():
    if LATITUDE and LONGITUDE:
        url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={LATITUDE},{LONGITUDE}&destinations={LATITUDE},{LONGITUDE}&departure_time=now&key=your_google_maps_api_key"
        response = requests.get(url).json()
        try:
            return response["rows"][0]["elements"][0]["duration_in_traffic"]["value"] / 60
        except KeyError:
            return "Unknown"
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
if zip_code and LATITUDE and LONGITUDE:
    st.subheader(f"📍 Location based on ZIP code: {zip_code}, Timezone: {USER_TIMEZONE}")

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
