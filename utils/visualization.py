import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

def plot_player_guesses_timeline(guesses):
    try:
        guess_df = pd.DataFrame(list(guesses.items()), columns=['Player', 'Guess'])
        guess_df['Guess'] = pd.to_datetime(guess_df['Guess'])

        fig, ax = plt.subplots(figsize=(10, 3))

        # Create the timeline
        for index, row in guess_df.iterrows():
            ax.plot(row['Guess'], 1, 'o', label=row['Player'])

        # Customize the plot
        ax.get_yaxis().set_visible(False)  # Hide the y-axis
        ax.set_xlabel('Date')
        ax.set_xlim(guess_df['Guess'].min() - pd.Timedelta(days=2), guess_df['Guess'].max() + pd.Timedelta(days=2))
        
        # Create labels and title
        for index, row in guess_df.iterrows():
            ax.text(row['Guess'], 1.02, row['Player'], rotation=45, ha='right', fontsize=8)

        plt.title('Player Guesses Timeline')
        plt.tight_layout()

        return fig
    except Exception as e:
        st.error(f"An error occurred while creating the timeline: {e}")
        return None

def plot_historical_snowfall(historical_df):
    historical_df['first_snowfall_date'] = pd.to_datetime(historical_df['first_snowfall_date'])
    historical_df['first_snowfall_day_of_year'] = historical_df['first_snowfall_date'].dt.dayofyear

    fig, ax = plt.subplots()
    ax.bar(historical_df['year'], historical_df['first_snowfall_day_of_year'])
    ax.set_xlabel('Year')
    ax.set_ylabel('Day of Year')
    ax.set_title('First Snowfall Day of Year Over the Past 20 Years')
    
    plt.tight_layout()
    return fig
