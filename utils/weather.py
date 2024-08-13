import pandas as pd
import requests
from datetime import datetime

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
    snowfall_df['date'] = pd.to_datetime(snowfall_df['date'])

    # Group by year and find the first snowfall after July 1st for each year
    first_snowfall = snowfall_df.groupby(snowfall_df['date'].dt.year)['date'].min().reset_index()
    first_snowfall.columns = ['year', 'first_snowfall_date']

    return first_snowfall.to_dict(orient='records')

def calculate_snowfall_statistics(historical_df):
    """
    Calculate the earliest, latest, and average first snowfall day after summer for the given historical data.
    """
    historical_df['first_snowfall_date'] = pd.to_datetime(historical_df['first_snowfall_date'])
    historical_df = historical_df[historical_df['first_snowfall_date'].dt.month >= 7]

    if historical_df.empty:
        return "N/A", "N/A", "N/A"

    # Calculate earliest, latest, and average first snowfall day
    earliest_day = historical_df['first_snowfall_date'].min().strftime('%B %d')
    latest_day = historical_df['first_snowfall_date'].max().strftime('%B %d')
    average_day = pd.to_datetime(historical_df['first_snowfall_date'].dt.dayofyear.mean(), format='%j').strftime('%B %d')

    return earliest_day, latest_day, average_day

def predict_first_snowfall_openweather(forecast_data):
    """
    Predict the first snowfall using OpenWeatherMap data, considering only dates after July 1st.
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

def get_openweather_forecast(latitude, longitude, api_key):
    """
    Fetch weather forecast data from the OpenWeatherMap API for the given location.
    """
    url = f"http://api.openweathermap.org/data/2.5/forecast?lat={latitude}&lon={longitude}&appid={api_key}&units=metric"

    response = requests.get(url)
    forecast_data = response.json()

    parsed_data = []
    for entry in forecast_data['list']:
        parsed_data.append({
            "date": entry['dt_txt'],
            "snow": entry.get('snow', {}).get('3h', 0)  # Example for 3-hour snowfall
        })

    return parsed_data

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
