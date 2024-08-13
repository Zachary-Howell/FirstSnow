import streamlit as st
import json
from datetime import datetime
import pandas as pd
from utils.weather import (
    get_openweather_forecast,
    calculate_snowfall_statistics,
    get_openmeteo_forecast,
    predict_first_snowfall_openweather,
    predict_first_snowfall_openmeteo,
    get_historical_snowfall
)
from utils.visualization import plot_player_guesses_timeline, plot_historical_snowfall
from config.api_keys import OPENWEATHER_API_KEY  # Import the API key

# Load JSON data
def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

location = load_json('config/location.json')
guesses = load_json('config/guesses.json')

# Constants from location settings
latitude = location["latitude"]
longitude = location["longitude"]

def main():
    # Fetch weather forecasts
    forecast_data_openweather = get_openweather_forecast(latitude, longitude, OPENWEATHER_API_KEY)
    forecast_data_openmeteo = get_openmeteo_forecast(latitude, longitude)

    # Predict snowfall
    predicted_snowfall_date_openweather = predict_first_snowfall_openweather(forecast_data_openweather)
    predicted_snowfall_date_openmeteo = predict_first_snowfall_openmeteo(forecast_data_openmeteo)

    # Get historical snowfall data
    historical_snowfall = get_historical_snowfall(latitude, longitude, datetime.now().year - 20, datetime.now().year - 1)
    historical_df = pd.DataFrame(historical_snowfall)

    # Streamlit UI
    st.title("❄❄❄ Snowfall - The Game ❄❄❄")

    st.header("PLAYER GUESSES")
    fig_timeline = plot_player_guesses_timeline(guesses, earliest_day, latest_day, average_day)
    if fig_timeline:
        st.pyplot(fig_timeline)

    # Insert a horizontal line
    st.markdown("<hr>", unsafe_allow_html=True)

    st.header("PROJECTED WINNERS")
    
    st.subheader('If it snowed today?')
    closest_guess_today = min(guesses.items(), key=lambda x: abs(datetime.strptime(x[1], '%Y-%m-%d').date() - datetime.now().date()))
    st.write(f"{closest_guess_today[0]} would win with a guess of {closest_guess_today[1]}.")

    st.subheader("If forecasts are accurate?")
    if predicted_snowfall_date_openweather or predicted_snowfall_date_openmeteo:
        if predicted_snowfall_date_openweather:
            predicted_date = datetime.strptime(predicted_snowfall_date_openweather, '%Y-%m-%d %H:%M:%S').date()
            closest_guess_predicted = min(guesses.items(), key=lambda x: abs(datetime.strptime(x[1], '%Y-%m-%d').date() - predicted_date))
            st.write(f"If OpenWeatherMap is correct, {closest_guess_predicted[0]} would win with a guess of {closest_guess_predicted[1]}.")
        if predicted_snowfall_date_openmeteo:
            predicted_date = datetime.strptime(predicted_snowfall_date_openmeteo, '%Y-%m-%d').date()
            closest_guess_predicted = min(guesses.items(), key=lambda x: abs(datetime.strptime(x[1], '%Y-%m-%d').date() - predicted_date))
            st.write(f"If Open-Meteo is correct, {closest_guess_predicted[0]} would win with a guess of {closest_guess_predicted[1]}.")
    else:
        st.write("No snowfall is forecasted in the near future.")

    # Insert a horizontal line
    st.markdown("<hr>", unsafe_allow_html=True)

    # Combine the forecasts under a single header
    st.header("FORECASTED FIRST SNOWFALL DATE")

    st.subheader("OpenWeatherMap Forecast")
    if predicted_snowfall_date_openweather:
        st.write(f"OpenWeatherMap predicts the first snowfall on: {predicted_snowfall_date_openweather}")
    else:
        st.write("No snowfall predicted in the current 5-day forecast period.")

    st.subheader("Open-Meteo Forecast")
    if predicted_snowfall_date_openmeteo:
        st.write(f"Open-Meteo predicts the first snowfall on: {predicted_snowfall_date_openmeteo}")
    else:
        st.write("No snowfall predicted in the current 14-day forecast period.")

    # Insert a horizontal line
    st.markdown("<hr>", unsafe_allow_html=True)

    st.header("HISTORICAL DATA (20 YEARS)")
    if not historical_df.empty:
        st.pyplot(plot_historical_snowfall(historical_df))

        # Calculate and display statistics
        earliest_day, latest_day, average_day = calculate_snowfall_statistics(historical_df)
        st.markdown(f"""
        - **Earliest Day:** {earliest_day}
        - **Latest Day:** {latest_day}
        - **Median Day:** {average_day}
        """)
    else:
        st.write("No historical snowfall data available.")

if __name__ == "__main__":
    main()
