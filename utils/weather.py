import requests
from datetime import datetime

def get_openweather_forecast(lat, lon, api_key):
    url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    response = requests.get(url)
    return response.json()

def get_openmeteo_forecast(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=snowfall_sum&timezone=auto"
    response = requests.get(url)
    return response.json()

def predict_first_snowfall_openweather(weather_data):
    for forecast in weather_data['list']:
        if 'snow' in forecast and forecast['snow'].get('3h', 0) > 0:
            return forecast['dt_txt']
    return None

def predict_first_snowfall_openmeteo(weather_data):
    for day, snowfall in zip(weather_data['daily']['time'], weather_data['daily']['snowfall_sum']):
        if snowfall > 0:
            return day
    return None

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
