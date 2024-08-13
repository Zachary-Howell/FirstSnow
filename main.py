import streamlit as st
import requests
from datetime import datetime, timedelta
import plotly.express as px
from plotly.tools import FigureFactory as FF
import pandas as pd

# API keys (replace with your own keys)
openweather_api_key = st.secrets["api_key"]

# Define the location
latitude = 41.161083
longitude = -112.016310

# Function to get weather data from OpenWeatherMap (5-day forecast)
def get_openweather_forecast(lat, lon, api_key):
    url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    response = requests.get(url)
    return response.json()

# Function to get weather data from Open-Meteo (14-day forecast)
def get_openmeteo_forecast(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=snowfall_sum&timezone=auto"
    response = requests.get(url)
    return response.json()

# Function to determine the first forecasted snowfall date
def predict_first_snowfall_openweather(weather_data):
    for forecast in weather_data['list']:
        if 'snow' in forecast and forecast['snow'].get('3h', 0) > 0:
            return forecast['dt_txt']
    return None

# Function to determine the first forecasted snowfall date from Open-Meteo
def predict_first_snowfall_openmeteo(weather_data):
    for day, snowfall in zip(weather_data['daily']['time'], weather_data['daily']['snowfall_sum']):
        if snowfall > 0:
            return day
    return None

# Function to get historical data from Open-Meteo
def get_historical_snowfall(lat, lon, start_year, end_year):
    snowfall_dates = []
    for year in range(start_year, end_year + 1):
        url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={year}-01-01&end_date={year}-12-31&daily=snowfall_sum&timezone=auto"
        response = requests.get(url)
        data = response.json()
        for day, snowfall in zip(data['daily']['time'], data['daily']['snowfall_sum']):
            if snowfall > 0:
                snowfall_dates.append({'year': year, 'first_snowfall_date': day})
                break
    return snowfall_dates

# List of player guesses
guesses = {
    'Alice': '2024-11-15',
    'Bob': '2024-11-20',
    'Charlie': '2024-11-25',
    'Dana': '2024-12-01'
}

# Fetch the weather forecast
forecast_data_openweather = get_openweather_forecast(latitude, longitude, openweather_api_key)
forecast_data_openmeteo = get_openmeteo_forecast(latitude, longitude)

# Predict the first snowfall
predicted_snowfall_date_openweather = predict_first_snowfall_openweather(forecast_data_openweather)
predicted_snowfall_date_openmeteo = predict_first_snowfall_openmeteo(forecast_data_openmeteo)

# Get historical snowfall data for the past 20 years
historical_snowfall = get_historical_snowfall(latitude, longitude, datetime.now().year - 20, datetime.now().year - 1)

# Convert historical data to a DataFrame
historical_df = pd.DataFrame(historical_snowfall)

# Display the dashboard
st.title("First Snowfall Game")

st.header("Player Guesses Timeline")
if guesses:
    guess_df = pd.DataFrame(list(guesses.items()), columns=['Player', 'Guess'])
    guess_df['Guess'] = pd.to_datetime(guess_df['Guess'])

    fig_timeline = ff.create_gantt(
        guess_df.rename(columns={'Guess': 'Start'}), 
        index_col='Player', 
        show_colorbar=True, 
        group_tasks=True, 
        title="Player Guesses Timeline",
        showgrid_x=True, 
        showgrid_y=True
    )
    st.plotly_chart(fig_timeline)

st.header("Predicted First Snowfall Date (OpenWeatherMap)")
if predicted_snowfall_date_openweather:
    st.write(f"OpenWeatherMap predicts the first snowfall on: {predicted_snowfall_date_openweather}")
else:
    st.write("No snowfall predicted in the current 5-day forecast period.")

st.header("Predicted First Snowfall Date (Open-Meteo)")
if predicted_snowfall_date_openmeteo:
    st.write(f"Open-Meteo predicts the first snowfall on: {predicted_snowfall_date_openmeteo}")
else:
    st.write("No snowfall predicted in the current 14-day forecast period.")

st.header("Who Would Win If It Snowed Today?")
today = datetime.now().date()
closest_guess_today = min(guesses.items(), key=lambda x: abs(datetime.strptime(x[1], '%Y-%m-%d').date() - today))
st.write(f"{closest_guess_today[0]} would win with a guess of {closest_guess_today[1]}.")

if predicted_snowfall_date_openweather or predicted_snowfall_date_openmeteo:
    st.header("Who Would Win If the Forecast is True?")

    if predicted_snowfall_date_openweather:
        predicted_date = datetime.strptime(predicted_snowfall_date_openweather, '%Y-%m-%d %H:%M:%S').date()
        closest_guess_predicted = min(guesses.items(), key=lambda x: abs(datetime.strptime(x[1], '%Y-%m-%d').date() - predicted_date))
        st.write(f"If OpenWeatherMap is correct, {closest_guess_predicted[0]} would win with a guess of {closest_guess_predicted[1]}.")

    if predicted_snowfall_date_openmeteo:
        predicted_date = datetime.strptime(predicted_snowfall_date_openmeteo, '%Y-%m-%d').date()
        closest_guess_predicted = min(guesses.items(), key=lambda x: abs(datetime.strptime(x[1], '%Y-%m-%d').date() - predicted_date))
        st.write(f"If Open-Meteo is correct, {closest_guess_predicted[0]} would win with a guess of {closest_guess_predicted[1]}.")

# Plot the historical first snowfall dates
st.header("Historical First Snowfall Dates (Past 20 Years)")
if not historical_df.empty:
    historical_df['first_snowfall_date'] = pd.to_datetime(historical_df['first_snowfall_date'])
    historical_df['first_snowfall_day_of_year'] = historical_df['first_snowfall_date'].dt.dayofyear

    fig = px.bar(historical_df, x='year', y='first_snowfall_day_of_year', 
                 labels={'first_snowfall_day_of_year': 'Day of Year', 'year': 'Year'}, 
                 title='First Snowfall Day of Year Over the Past 20 Years')
    st.plotly_chart(fig)
else:
    st.write("No historical snowfall data available.")