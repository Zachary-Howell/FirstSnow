import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import streamlit as st
from datetime import datetime

def plot_player_guesses_timeline(guesses):
    try:
        # Convert guesses to DataFrame and parse dates
        guess_df = pd.DataFrame(list(guesses.items()), columns=['Player', 'Guess'])
        guess_df['Guess'] = pd.to_datetime(guess_df['Guess'])

        # Get today's date
        today = pd.to_datetime(datetime.today().date())

        # Create the figure and axis
        fig, ax = plt.subplots(figsize=(10, 2))

        # Plot the timeline (a single horizontal line)
        ax.plot(guess_df['Guess'], [1] * len(guess_df), "o", color="C0")

        # Add vertical stems connecting points to the timeline
        ax.vlines(guess_df['Guess'], 0, 1, colors="C0", linestyle='dotted')

        # Add player names and guess dates as labels
        for idx, row in guess_df.iterrows():
            ax.text(row['Guess'], 1.05, f"{row['Player']}\n{row['Guess'].strftime('%b %d')}", 
                    ha='center', fontsize=8, rotation=45)

        # Plot today's date
        ax.plot(today, 1, "o", color="red")
        ax.vlines(today, 0, 1, colors="red", linestyle='solid')
        ax.text(today, 1.05, f"Today\n{today.strftime('%b %d')}", ha='center', fontsize=8, rotation=45, color="red")

        # Format x-axis to show only months
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
        plt.setp(ax.get_xticklabels(), rotation=0, ha="center")

        # Adjust x-axis limits to include today
        ax.set_xlim(min(guess_df['Guess'].min(), today) - pd.Timedelta(days=2), 
                    max(guess_df['Guess'].max(), today) + pd.Timedelta(days=2))

        # Remove y-axis and spines for a cleaner look
        ax.get_yaxis().set_visible(False)
        ax.spines[["left", "top", "right"]].set_visible(False)

        # Adjust layout
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
