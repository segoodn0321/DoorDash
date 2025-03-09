import streamlit as st
import requests
import datetime
import pandas as pd
import joblib
import pytz
import os
from sklearn.ensemble import RandomForestRegressor

# **🔑 API KEYS**
HERE_API_KEY = "your_here_api_key"  
OPENWEATHER_API_KEY = "your_openweather_api_key"

# Constants
EARNINGS_FILE = "driver_earnings.csv"

# **User enters ZIP Code**
st.title("🚗 DoorDash AI Driver Assistant")
zip_code = st.text_input("Enter your ZIP code (5 digits):", max_chars=5)

# **Validate ZIP Code Before Making API Request**
def is_valid_zip(zip_code):
    return zip_code.isdigit() and len(zip_code) == 5

# **Fetch latitude & longitude using HERE API**
def get_lat_lon(zip_code):
    if not is_valid_zip(zip_code):
        return None, None

    try:
        url = f"https://geocode.search.hereapi.com/v1/geocode?q={zip_code},US&apiKey={HERE_API_KEY}"
        response = requests.get(url).json()

        if "items" in response and response["items"]:
            location = response["items"][0]["position"]
            return location["lat"], location["lng"]
        else:
            st.error(f"⚠️ ZIP code lookup failed: {response.get('error', 'Unknown error')}")
    except Exception as e:
        st.error(f"⚠️ Error fetching ZIP location: {e}")
    return None, None

LATITUDE, LONGITUDE = None, None
if zip_code and is_valid_zip(zip_code):
    LATITUDE, LONGITUDE = get_lat_lon(zip_code)
    if LATITUDE and LONGITUDE:
        st.success(f"🌍 Location detected! Using ZIP code {zip_code}")
    else:
        st.error("⚠️ ZIP code not found. Please check and try again.")

# **Get timezone based on location using HERE API**
def get_timezone(lat, lon):
    try:
        url = f"https://time.ls.hereapi.com/v1/timezone?location={lat},{lon}&apiKey={HERE_API_KEY}"
        response = requests.get(url).json()
        return response.get("timeZone", {}).get("id", "UTC")
    except Exception as e:
        st.error(f"⚠️ Error fetching timezone: {e}")
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
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?lat={LATITUDE}&lon={LONGITUDE}&appid={OPENWEATHER_API_KEY}&units=imperial"
            response = requests.get(url).json()
            if "weather" in response:
                return response["weather"][0]["description"], response["main"]["temp"], response["wind"]["speed"]
        except Exception as e:
            st.error(f"⚠️ Weather API error: {e}")
    return "Unknown", "N/A", "N/A"

# **Fetch real-time traffic using HERE API**
def get_traffic():
    if LATITUDE and LONGITUDE:
        try:
            url = f"https://traffic.ls.hereapi.com/traffic/6.3/flow.json?prox={LATITUDE},{LONGITUDE},1000&apiKey={HERE_API_KEY}"
            response = requests.get(url).json()

            if "RWS" in response and len(response["RWS"]) > 0:
                flow_items = response["RWS"][0]["RW"]
                congestion_levels = [float(item["FIS"][0]["FI"][0]["CF"][0]["JF"]) for item in flow_items if "FIS" in item]
                avg_congestion = sum(congestion_levels) / len(congestion_levels) if congestion_levels else "Unknown"
                return avg_congestion
        except Exception as e:
            st.error(f"⚠️ Traffic API error: {e}")
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
    df["traffic_score"] = df["traffic"].apply(lambda x: 1 if x > 5 else 0)

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

    predictions = [(hour, model.predict([[hour, 1 if "rain" in weather.lower() else 0, 1 if traffic > 5 else 0]])[0]) for hour in hours]

    return max(predictions, key=lambda x: x[1])

# **Streamlit UI**
if zip_code and LATITUDE and LONGITUDE:
    st.subheader(f"📍 Location: {zip_code}, Timezone: {USER_TIMEZONE}")

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
        
