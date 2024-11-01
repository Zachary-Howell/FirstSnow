import streamlit as st
import json
from datetime import datetime
import pandas as pd
from utils.weather import *
from utils.visualization import *

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
    forecast_data_openmeteo = get_openmeteo_forecast(latitude, longitude)

    # Predict snowfall
    predicted_snowfall_date_openmeteo = predict_first_snowfall_openmeteo(forecast_data_openmeteo)

    # Get historical snowfall data
    historical_snowfall = get_historical_snowfall(latitude, longitude, datetime.now().year - 20, datetime.now().year - 1)
    historical_df = pd.DataFrame(historical_snowfall)

    # Retrieve recent snowfall data
    snowfall_df = get_recent_snowfall_data(latitude, longitude)

    # Check for snowfall and identify the closest guess
    result = check_for_recent_snowfall(snowfall_df)

    # Streamlit UI
    st.title("❄❄❄ Snowfall - The Game ❄❄❄")

    st.header("PLAYER GUESSES")

    # Display the timeline of guesses and actual snowfall
    timeline_fig = plot_snowfall_timeline(result["first_snow_date"], result["winner"], predicted_snowfall_date_openmeteo)
    st.plotly_chart(timeline_fig)

    # Insert a horizontal line
    st.markdown("<hr>", unsafe_allow_html=True)

    # Display results based on snowfall occurrence
    if result["snowfall_occurred"]:
        st.success(f"Snow has fallen on {result['first_snow_date'].strftime('%Y-%m-%d')}! "
                   f"The winner is {result['winner']} with the closest guess.")
    else:
        st.info("No snowfall recorded yet. Stay tuned!")

    st.header("PROJECTED WINNERS")
    
    # Function to find closest guessers to a target date, allowing for ties
    def find_closest_guessers(guesses, target_date, use_full_datetime=False):
        """
        Finds the closest guessers to a target date.
        
        Parameters:
            guesses (dict): Dictionary of guesses with player names as keys and guess dates as values.
            target_date (datetime): The date to compare guesses against.
            use_full_datetime (bool): If True, compare full datetime; if False, use only date.

        Returns:
            list: Names of the closest guessers.
        """
        # Convert guesses to datetime for accurate comparison
        if use_full_datetime:
            guess_dates = {name: datetime.strptime(date, '%Y-%m-%d %H:%M') for name, date in guesses.items()}
        else:
            guess_dates = {name: datetime.strptime(date, '%Y-%m-%d %H:%M').date() for name, date in guesses.items()}
            target_date = target_date.date()  # Compare only by date if `use_full_datetime` is False

        # Calculate absolute differences for each guess
        differences = {name: abs((guess_date - target_date).total_seconds()) if use_full_datetime
                    else abs((guess_date - target_date).days)
                    for name, guess_date in guess_dates.items()}
        min_difference = min(differences.values())
        
        # Return all names with the minimum difference to allow ties
        return [name for name, diff in differences.items() if diff == min_difference]

    st.subheader('If it snowed today?')
    today = datetime.now()
    closest_guessers_today = find_closest_guessers(guesses, today)

    # Display result for closest guessers to today
    if len(closest_guessers_today) == 1:
        st.write(f"{closest_guessers_today[0]} would win with a guess of {guesses[closest_guessers_today[0]]}.")
    else:
        winners_text = " & ".join(closest_guessers_today)
        st.write(f"Tie between {winners_text}, each with guesses of {guesses[closest_guessers_today[0]]}.")

    st.subheader("If Open-Meteo forecast is accurate?")
    if predicted_snowfall_date_openmeteo:
        # Parse the predicted snowfall date from Open-Meteo, assuming it’s day-based
        predicted_date = datetime.strptime(predicted_snowfall_date_openmeteo, '%Y-%m-%d')
        closest_guessers_predicted = find_closest_guessers(guesses, predicted_date, use_full_datetime=False)

        # Display result for closest guessers to predicted snowfall date
        if len(closest_guessers_predicted) == 1:
            st.write(f"{closest_guessers_predicted[0]} would win with a guess of {guesses[closest_guessers_predicted[0]]}.")
        else:
            winners_text = " & ".join(closest_guessers_predicted)
            st.write(f"Tie between {winners_text}, each with guesses of {guesses[closest_guessers_predicted[0]]}.")
    else:
        st.write("No snowfall is forecasted in the near future.")

    # Insert a horizontal line
    st.markdown("<hr>", unsafe_allow_html=True)

    # Combine the forecasts under a single header
    st.header("FORECASTED FIRST SNOWFALL DATE")

    if predicted_snowfall_date_openmeteo:
        st.write(f"Open-Meteo predicts the first snowfall on: {predicted_snowfall_date_openmeteo}")
    else:
        st.write("No snowfall predicted in the current 14-day forecast period.")

    # # Insert a horizontal line
    st.markdown("<hr>", unsafe_allow_html=True)

    st.header("Recent Snowfall Data")
    snowfall_df = get_recent_snowfall_data(latitude, longitude)

    # Generate the Plotly chart using the visualization function
    fig = plot_snowfall_data(snowfall_df)

    # Display the Plotly chart in Streamlit
    st.plotly_chart(fig)

    # Insert a horizontal line
    st.markdown("<hr>", unsafe_allow_html=True)

    st.header("Test Snowfall Data for January 2023")
    snowfall_df = get_test_snowfall_data(latitude, longitude)

    # Generate the Plotly chart using the visualization function
    fig = plot_snowfall_data(snowfall_df)

    # Display the Plotly chart in Streamlit
    st.plotly_chart(fig)

    # Insert a horizontal line
    st.markdown("<hr>", unsafe_allow_html=True)

    st.header("HISTORICAL DATA (20 YEARS)")
    if not historical_df.empty:
        st.pyplot(plot_historical_snowfall(historical_df))

        # Display statistics
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

