import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Configuration
WEATHER_API_KEY = 'your_openweathermap_api_key'
EVENTS_API_KEY = 'TfBhpZCOdZPAqlLCNBZU05iDAY9dLiBh'  # Use an events API such as Ticketmaster or Eventbrite

# Historical orders database (expand with actual data per zip code)
historical_orders_db = {
    '28409': [
        {'time': '2024-03-01 13:00', 'orders': 15},
        {'time': '2024-03-01 14:00', 'orders': 12},
        {'time': '2024-03-01 18:00', 'orders': 22},
    ],
    '10001': [
        {'time': '2024-03-02 12:00', 'orders': 20},
        {'time': '2024-03-02 17:00', 'orders': 25},
        {'time': '2024-03-02 19:00', 'orders': 30},
    ],
    # Add more zip codes and their historical data here
}

# Fetch weather data
def get_weather(zip_code):
    url = f"http://api.openweathermap.org/data/2.5/weather?zip={zip_code},us&appid={WEATHER_API_KEY}&units=imperial"
    try:
        response = requests.get(url)
        response.raise_for_status()
        weather_data = response.json()
        condition = weather_data['weather'][0]['main']
        temperature = weather_data['main']['temp']
        return f"{condition}, {temperature}°F"
    except requests.RequestException:
        return "Weather data unavailable"

# Fetch local events data
def get_local_events(zip_code):
    # Placeholder for event fetching logic
    return ["Concert at 7 PM", "Local festival at noon"]

# Peak hour analysis
def analyze_peak_hours(zip_code):
    orders_data = historical_orders_db.get(zip_code, [])
    if not orders_data:
        return None
    df = pd.DataFrame(orders_data)
    df['time'] = pd.to_datetime(df['time'])
    return df.groupby(df['time'].dt.hour)['orders'].sum().idxmax()

# Recommend earning mode
def recommend_earning_mode(current_hour, peak_hour, events):
    event_impact_hours = [event for event in events if "7 PM" in event or "noon" in event]
    if peak_hour is None:
        return "Insufficient data"
    if abs(current_hour - peak_hour) <= 1 or event_impact_hours:
        return "Earn per Order"
    return "Earn by Time"

# Streamlit Dashboard
st.title("🚗 DoorDash Earnings Optimizer")

zip_code = st.text_input("Enter Zip Code", "28409")

if st.button("Analyze"):
    weather = get_weather(zip_code)
    local_events = get_local_events(zip_code)
    peak_hour = analyze_peak_hours(zip_code)
    current_hour = datetime.now().hour
    recommendation = recommend_earning_mode(current_hour, peak_hour, local_events)

    st.subheader(f"📍 Current Weather in {zip_code}")
    st.write(weather)

    st.subheader("🎟️ Local Events")
    st.write(local_events if local_events else "No significant events today.")

    if peak_hour is not None:
        st.subheader("📈 Historical Peak Hour")
        st.write(f"{peak_hour}:00")
    else:
        st.subheader("📈 Historical Peak Hour")
        st.write("No historical data available for this zip code.")

    st.subheader("🕑 Current Time")
    st.write(f"{datetime.now().strftime('%H:%M')}")

    st.subheader("💰 Recommended Earning Mode")
    st.success(recommendation)
