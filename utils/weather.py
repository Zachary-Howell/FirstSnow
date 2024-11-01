import pandas as pd
import requests
import json
from datetime import datetime, timedelta

def get_historical_snowfall(latitude, longitude, start_year, end_year):
    """
    Fetch historical snowfall data from the Open-Meteo API for the specified location and years.
    Filters data to include only dates after July 1st and returns the first snowfall after summer each year.
    """
    all_snowfall_data = []

    for year in range(start_year, end_year + 1):
        url = (
            f"https://archive-api.open-meteo.com/v1/archive?latitude={latitude}&longitude={longitude}&"
            f"start_date={year}-07-01&end_date={year}-12-31&daily=snowfall_sum&timezone=auto"
        )

        response = requests.get(url)
        data = response.json()

        if 'daily' in data and 'snowfall_sum' in data['daily']:
            for i, date in enumerate(data['daily']['time']):
                snowfall_amount = data['daily']['snowfall_sum'][i]
                if snowfall_amount > 0:
                    all_snowfall_data.append({
                        'date': date,
                        'snowfall': snowfall_amount
                    })

    # Convert to DataFrame
    snowfall_df = pd.DataFrame(all_snowfall_data)
    if snowfall_df.empty:
        print("No snowfall data was retrieved from the API.")  # Replace st.error with print for backend debugging
        return pd.DataFrame()  # Return an empty DataFrame

    # print("Snowfall DataFrame:", snowfall_df)  # Debugging output to inspect the DataFrame

    snowfall_df['date'] = pd.to_datetime(snowfall_df['date'])

    # Extract the year from the date to avoid inserting a duplicate column
    snowfall_df['year'] = snowfall_df['date'].dt.year

    # Group by year and find the first snowfall after July 1st for each year
    first_snowfall = snowfall_df.groupby('year')['date'].min().reset_index()
    first_snowfall.columns = ['year', 'first_snowfall_date']

    # print("First Snowfall DataFrame:", first_snowfall)  # Debugging output to inspect the DataFrame

    return first_snowfall

def calculate_snowfall_statistics(historical_df):
    """
    Calculate the earliest, latest, and average first snowfall day after summer for the given historical data.
    Ensure correct handling of dates by focusing only on month and day.
    """
    # Convert to datetime if not already
    historical_df['first_snowfall_date'] = pd.to_datetime(historical_df['first_snowfall_date'])

    # Extract month and day (ignore the year)
    historical_df['month_day'] = historical_df['first_snowfall_date'].apply(lambda x: x.strftime('%m-%d'))

    # Calculate earliest and latest snowfall dates based on month and day, ignoring year
    earliest_day_date = historical_df['month_day'].min()
    latest_day_date = historical_df['month_day'].max()

    # Convert back to a readable format (just add a placeholder year for formatting)
    earliest_day = pd.to_datetime(earliest_day_date, format='%m-%d').strftime('%B %d')
    latest_day = pd.to_datetime(latest_day_date, format='%m-%d').strftime('%B %d')

    # Calculate average day of the year and convert back to a date
    average_day_of_year = historical_df['first_snowfall_date'].dt.dayofyear.mean()
    average_day = pd.to_datetime(average_day_of_year, format='%j').strftime('%B %d')

    return earliest_day, latest_day, average_day

def predict_first_snowfall_openmeteo(forecast_data):
    """
    Predict the first snowfall using Open-Meteo data, considering only dates after July 1st.
    """
    forecast_df = pd.DataFrame(forecast_data)
    forecast_df['date'] = pd.to_datetime(forecast_df['date'])

    # Filter for dates after July 1st
    forecast_df = forecast_df[forecast_df['date'].dt.month >= 7]

    snowfall_days = forecast_df[forecast_df['snow'] > 0].sort_values('date')
    if not snowfall_days.empty:
        first_snowfall = snowfall_days.iloc[0]['date']
        return first_snowfall.strftime('%Y-%m-%d')
    else:
        return None  # No snowfall predicted

def get_openmeteo_forecast(latitude, longitude):
    """
    Fetch weather forecast data from the Open-Meteo API for the given location.
    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&daily=snowfall_sum&timezone=auto"

    response = requests.get(url)
    forecast_data = response.json()

    parsed_data = []
    for i, date in enumerate(forecast_data['daily']['time']):
        parsed_data.append({
            "date": date,
            "snow": forecast_data['daily']['snowfall_sum'][i]
        })

    return parsed_data

def fetch_daily_snowfall_openmeteo(latitude, longitude, date):
    """Fetches daily total snowfall in inches for a specific date from Open-Meteo."""
    formatted_date = date.strftime('%Y-%m-%d')
    response = requests.get(
        "https://archive-api.open-meteo.com/v1/archive",
        params={
            "latitude": latitude,
            "longitude": longitude,
            "start_date": formatted_date,
            "end_date": formatted_date,
            "hourly": "snowfall"
        }
    )
    if response.status_code == 200:
        data = response.json()
        hourly_snowfall = data.get("hourly", {}).get("snowfall", [])
        total_snowfall_mm = sum(val for val in hourly_snowfall if val is not None)
        # Convert from mm to inches and round to 2 decimal places
        return round(total_snowfall_mm / 25.4, 2)
    return 0.0  # Default to zero if no data

def get_snowfall_data_df(latitude, longitude, start_date, end_date):
    """
    Retrieves daily snowfall data for a specified date range and returns it as a DataFrame.
    """
    snowfall_data = []

    # Loop through each date in the range and fetch snowfall data
    for date in (start_date + timedelta(n) for n in range((end_date - start_date).days + 1)):
        daily_snowfall = fetch_daily_snowfall_openmeteo(latitude, longitude, date)
        snowfall_data.append({"Date": date.strftime('%Y-%m-%d'), "Snowfall (inches)": daily_snowfall})

    # Convert to DataFrame and ensure the Date column is in datetime format
    snowfall_df = pd.DataFrame(snowfall_data)
    snowfall_df["Date"] = pd.to_datetime(snowfall_df["Date"])
    return snowfall_df

def get_recent_snowfall_data(latitude, longitude):
    """
    Fetches recent snowfall data from September 1, 2024, to the current date.
    """
    start_date = datetime(2024, 9, 1)
    end_date = datetime.now()
    return get_snowfall_data_df(latitude, longitude, start_date, end_date)

def get_test_snowfall_data(latitude, longitude):
    """
    Fetches test snowfall data for January 2023.
    """
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 1, 31)
    return get_snowfall_data_df(latitude, longitude, start_date, end_date)

def check_for_recent_snowfall(snowfall_df, guesses_file='config\guesses.json'):
    """
    Checks if recent snowfall has occurred and determines the closest guess if snow has fallen.

    Parameters:
        snowfall_df (pd.DataFrame): DataFrame containing recent snowfall data.
        guesses_file (str): Path to the JSON file with guesses.

    Returns:
        dict: A dictionary with keys "snowfall_occurred", "first_snow_date", and "winner" (if snowfall occurred).
    """
    # Load guesses from JSON file
    with open(guesses_file) as f:
        guesses = json.load(f)

    # Check if any snowfall has been recorded
    snowfall_occurred = snowfall_df[snowfall_df["Snowfall (inches)"] > 0]
    if not snowfall_occurred.empty:
        # Find the first date it snowed
        first_snow_date = snowfall_occurred["Date"].min()

        # Determine the closest guess
        closest_guess = None
        min_diff = float('inf')
        for person, guess_date_str in guesses.items():
            guess_date = datetime.strptime(guess_date_str, '%Y-%m-%d').date()
            diff = abs((first_snow_date - guess_date).days)
            if diff < min_diff:
                min_diff = diff
                closest_guess = person

        # Return snowfall occurrence with the first snow date and winner
        return {
            "snowfall_occurred": True,
            "first_snow_date": first_snow_date,
            "winner": closest_guess
        }

    # If no snowfall occurred, return indicating that
    return {
        "snowfall_occurred": False,
        "first_snow_date": None,
        "winner": None
    }