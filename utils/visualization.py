import plotly.express as px
import pandas as pd

def plot_player_guesses_timeline(guesses):
    guess_df = pd.DataFrame(list(guesses.items()), columns=['Player', 'Guess'])
    guess_df['Guess'] = pd.to_datetime(guess_df['Guess'])

    fig_timeline = px.timeline(
        guess_df, 
        x_start="Guess", 
        x_end="Guess", 
        y="Player", 
        color="Player",
        title="Player Guesses Timeline",
    )
    fig_timeline.update_yaxes(categoryorder="total ascending")
    return fig_timeline

def plot_historical_snowfall(historical_df):
    historical_df['first_snowfall_date'] = pd.to_datetime(historical_df['first_snowfall_date'])
    historical_df['first_snowfall_day_of_year'] = historical_df['first_snowfall_date'].dt.dayofyear

    fig = px.bar(historical_df, x='year', y='first_snowfall_day_of_year', 
                 labels={'first_snowfall_day_of_year': 'Day of Year', 'year': 'Year'}, 
                 title='First Snowfall Day of Year Over the Past 20 Years')
    return fig
