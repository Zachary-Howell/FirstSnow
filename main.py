import streamlit as st
import requests
from datetime import datetime, timedelta

# API keys (replace with your own keys)
openweather_api_key = st.secrets["api_key"]

# Define the location
latitude = 41.161083  # Example latitude (Salt Lake City, UT)
longitude = -112.016310  # Example longitude (Salt Lake City, UT)

# Function to get weather data from OpenWeatherMap
def get_openweather_forecast(lat, lon, api_key):
    url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    response = requests.get(url)
    return response.json()

# Function to determine the first forecasted snowfall date
def predict_first_snowfall(weather_data):
    for forecast in weather_data['list']:
        if 'snow' in forecast and forecast['snow'].get('3h', 0) > 0:
            return forecast['dt_txt']
    return None

# List of player guesses
guesses = {
    'Alice': '2024-11-15',
    'Bob': '2024-11-20',
    'Charlie': '2024-11-25',
    'Dana': '2024-12-01'
}

# Fetch the weather forecast
forecast_data = get_openweather_forecast(latitude, longitude, openweather_api_key)

# Predict the first snowfall
predicted_snowfall_date = predict_first_snowfall(forecast_data)

# Display the dashboard
st.title("First Snowfall Game")

st.header("Player Guesses")
for player, guess in guesses.items():
    st.write(f"{player}: {guess}")

st.header("Predicted First Snowfall Date")
if predicted_snowfall_date:
    st.write(f"The forecast predicts the first snowfall on: {predicted_snowfall_date}")
else:
    st.write("No snowfall predicted in the current forecast period.")

st.header("Who Would Win If It Snowed Today?")
today = datetime.now().date()
closest_guess_today = min(guesses.items(), key=lambda x: abs(datetime.strptime(x[1], '%Y-%m-%d').date() - today))
st.write(f"{closest_guess_today[0]} would win with a guess of {closest_guess_today[1]}.")

if predicted_snowfall_date:
    st.header("Who Would Win If the Forecast is True?")
    predicted_date = datetime.strptime(predicted_snowfall_date, '%Y-%m-%d %H:%M:%S').date()
    closest_guess_predicted = min(guesses.items(), key=lambda x: abs(datetime.strptime(x[1], '%Y-%m-%d').date() - predicted_date))
    st.write(f"{closest_guess_predicted[0]} would win with a guess of {closest_guess_predicted[1]}.")

