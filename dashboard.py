import requests
import datetime
import pandas as pd
import joblib
import sys
import subprocess
import bcrypt
import os
import json

# Auto-install missing packages
required_libs = ["requests", "pandas", "joblib", "scikit-learn", "bcrypt"]
for lib in required_libs:
    try:
        __import__(lib)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

from sklearn.ensemble import RandomForestRegressor

# File to store user credentials
USER_CREDENTIALS_FILE = "user_credentials.json"

# Load or create user credentials database
def load_user_credentials():
    if os.path.exists(USER_CREDENTIALS_FILE):
        with open(USER_CREDENTIALS_FILE, "r") as file:
            return json.load(file)
    return {}

def save_user_credentials(credentials):
    with open(USER_CREDENTIALS_FILE, "w") as file:
        json.dump(credentials, file)

# User registration
def register_user():
    credentials = load_user_credentials()
    username = input("Enter a new username: ").strip()

    if username in credentials:
        print("Username already exists. Try logging in.")
        return None

    password = input("Enter a new password: ").strip()
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    credentials[username] = hashed_password
    save_user_credentials(credentials)

    print("\n✅ Account created successfully! Please log in.")
    return None

# User login
def login_user():
    credentials = load_user_credentials()
    username = input("Enter your username: ").strip()

    if username not in credentials:
        print("❌ Username not found. Please register first.")
        return None

    password = input("Enter your password: ").strip()
    stored_hash = credentials[username].encode()

    if bcrypt.checkpw(password.encode(), stored_hash):
        print("\n✅ Login successful!")
        return username
    else:
        print("❌ Incorrect password.")
        return None

# Auto-detect user location using IP address
def get_location():
    try:
        response = requests.get("https://ipinfo.io/json").json()
        city = response.get("city", "Unknown City")
        lat, lon = response["loc"].split(",")
        return city, lat, lon
    except Exception as e:
        print("Error detecting location:", e)
        sys.exit(1)

CITY, LATITUDE, LONGITUDE = get_location()

# API Keys (Replace with your own)
OPENWEATHER_API_KEY = "your_openweather_api_key"
GOOGLE_MAPS_API_KEY = "your_google_maps_api_key"

# Fetch real-time weather data
def get_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={LATITUDE}&lon={LONGITUDE}&appid={OPENWEATHER_API_KEY}&units=imperial"
    response = requests.get(url).json()
    return {
        "description": response["weather"][0]["description"],
        "temp": response["main"]["temp"],
        "wind_speed": response["wind"]["speed"],
    }

# Fetch real-time traffic data
def get_traffic():
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={LATITUDE},{LONGITUDE}&destinations={LATITUDE},{LONGITUDE}&departure_time=now&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(url).json()
    try:
        return {"travel_time": response["rows"][0]["elements"][0]["duration_in_traffic"]["value"] / 60}
    except KeyError:
        return {"travel_time": "Unknown"}

# Load user-specific earnings data
def load_earnings_data(username):
    file_path = f"{username}_earnings.csv"
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return pd.DataFrame(columns=["date", "start_hour", "end_hour", "earnings", "weather", "traffic"])

# Save earnings data
def save_earnings_data(username):
    df = load_earnings_data(username)

    start_time = input("Enter shift start time (HH:MM AM/PM): ").strip()
    end_time = input("Enter shift end time (HH:MM AM/PM): ").strip()
    earnings = float(input("Enter total earnings for this shift ($): ").strip())

    date = datetime.datetime.today().strftime("%Y-%m-%d")
    weather = get_weather()["description"]
    traffic = get_traffic()["travel_time"]

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
    print("\n✅ Earnings data saved successfully!")

# Train AI model per user
def train_model(username):
    df = load_earnings_data(username)
    if len(df) < 20:
        print("Not enough data to train AI model yet. Keep logging shifts.")
        return None

    df["start_hour"] = pd.to_datetime(df["start_hour"], format="%I:%M %p").dt.hour
    df["weather_score"] = df["weather"].apply(lambda x: 1 if "rain" in x.lower() else 0)
    df["traffic_score"] = df["traffic"].apply(lambda x: 1 if x > 20 else 0)

    X, y = df[["start_hour", "weather_score", "traffic_score"]], df["earnings"]
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    joblib.dump(model, f"{username}_predictor.pkl")
    print("\n✅ AI model trained successfully!")

# Predict best time to drive
def predict_best_time(username):
    try:
        model = joblib.load(f"{username}_predictor.pkl")
    except FileNotFoundError:
        print("AI model not trained yet. Run train_model() after logging more shifts.")
        return None

    hours = list(range(10, 23))
    weather, traffic = get_weather(), get_traffic()
    predictions = [(hour, model.predict([[hour, 1 if "rain" in weather["description"].lower() else 0, 1 if traffic["travel_time"] > 20 else 0]])[0]) for hour in hours]

    return max(predictions, key=lambda x: x[1])

# Main menu
def main(username):
    while True:
        print("\n📊 **Driver Optimization Menu** 📊")
        print("1️⃣ Check best time to drive")
        print("2️⃣ Log earnings for a shift")
        print("3️⃣ Train AI model")
        print("4️⃣ Logout")

        choice = input("Enter your choice: ").strip()
        if choice == "1":
            print(f"\n💰 Best time to drive: {predict_best_time(username)}")
        elif choice == "2":
            save_earnings_data(username)
        elif choice == "3":
            train_model(username)
        elif choice == "4":
            break
        else:
            print("Invalid choice. Try again.")

# User authentication
while True:
    action = input("\nLogin or Register? (L/R): ").strip().upper()
    if action == "L":
        user = login_user()
        if user:
            main(user)
    elif action == "R":
        register_user()
    else:
        print("Invalid input.")
        
