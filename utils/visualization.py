import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json

# Load JSON data
def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def plot_player_guesses_timeline(earliest_day, latest_day, average_day):
    """
    Create a Matplotlib timeline of player guesses for the first snowfall,
    with markers for the earliest, latest, and average first snowfall days.
    """
    # Load guesses from the JSON file located in the config folder
    guesses = load_json('config/guesses.json')
    
    # Convert to DataFrame
    guesses_df = pd.DataFrame(guesses)

    # Convert 'guess_date' to datetime
    guesses_df['guess_date'] = pd.to_datetime(guesses_df['guess_date'])

    # Convert earliest, latest, and average days to datetime
    earliest_day_date = pd.to_datetime(earliest_day, format='%B %d')
    latest_day_date = pd.to_datetime(latest_day, format='%B %d')
    average_day_date = pd.to_datetime(average_day, format='%B %d')

    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 5))

    # Plot player guesses
    for index, row in guesses_df.iterrows():
        ax.plot(row['guess_date'], index, 'o', label=row['player'], markersize=8)

    # Annotate player names
    for index, row in guesses_df.iterrows():
        ax.text(row['guess_date'], index, row['player'], ha='left', va='center')

    # Plot earliest, latest, and average first snowfall days
    ax.axvline(earliest_day_date, color='green', linestyle='--', label='Earliest Snowfall')
    ax.axvline(latest_day_date, color='red', linestyle='--', label='Latest Snowfall')
    ax.axvline(average_day_date, color='blue', linestyle='--', label='Average Snowfall')

    # Annotate these dates
    ax.text(earliest_day_date, -0.5, 'Earliest\nSnowfall', color='green', ha='center')
    ax.text(latest_day_date, -0.5, 'Latest\nSnowfall', color='red', ha='center')
    ax.text(average_day_date, -0.5, 'Average\nSnowfall', color='blue', ha='center')

    # Set labels and title
    ax.set_yticks([])
    ax.set_xlabel('Date')
    ax.set_title('Player Guesses Timeline and Historical Snowfall Dates')

    # Show legend
    ax.legend()

    plt.tight_layout()
    return fig

# def plot_player_guesses_timeline(guesses):
#     try:
#         # Convert guesses to DataFrame and parse dates
#         guess_df = pd.DataFrame(list(guesses.items()), columns=['Player', 'Guess'])
#         guess_df['Guess'] = pd.to_datetime(guess_df['Guess'])

#         # Get today's date
#         today = pd.to_datetime(datetime.today().date())

#         # Generate unique colors for each player
#         colors = plt.cm.get_cmap('tab10', len(guess_df))

#         # Create the figure and axis
#         fig, ax = plt.subplots(figsize=(10, 2))

#         # Plot the timeline (a single horizontal line)
#         for idx, row in guess_df.iterrows():
#             ax.plot(row['Guess'], 1, "o", color=colors(idx))
#             ax.vlines(row['Guess'], 0, 1, colors=colors(idx), linestyle='dotted')
#             ax.text(row['Guess'], 1.05, f"{row['Player']}\n{row['Guess'].strftime('%b %d')}", 
#                     ha='center', fontsize=8, rotation=45, color=colors(idx))

#         # Plot today's date in a distinct color
#         ax.plot(today, 1, "o", color="red")
#         ax.vlines(today, 0, 1, colors="red", linestyle='solid')
#         ax.text(today, 1.05, f"Today\n{today.strftime('%b %d')}", ha='center', fontsize=8, rotation=45, color="red")

#         # Format x-axis to show only months
#         ax.xaxis.set_major_locator(mdates.MonthLocator())
#         ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
#         plt.setp(ax.get_xticklabels(), rotation=0, ha="center")

#         # Adjust x-axis limits to include today
#         ax.set_xlim(min(guess_df['Guess'].min(), today) - pd.Timedelta(days=2), 
#                     max(guess_df['Guess'].max(), today) + pd.Timedelta(days=2))

#         # Remove y-axis and spines for a cleaner look
#         ax.get_yaxis().set_visible(False)
#         ax.spines[["left", "top", "right"]].set_visible(False)

#         # Adjust layout
#         plt.tight_layout()

#         return fig
#     except Exception as e:
#         st.error(f"An error occurred while creating the timeline: {e}")
#         return None



def plot_historical_snowfall(historical_df):
    """
    Create a Matplotlib bar chart showing the frequency of first snowfall dates.
    """
    # Convert to datetime if not already
    historical_df['first_snowfall_date'] = pd.to_datetime(historical_df['first_snowfall_date'])

    # Extract month and day, ignore the year
    historical_df['month_day'] = historical_df['first_snowfall_date'].apply(lambda x: x.strftime('%m-%d'))

    # Count the occurrences of each month_day
    snowfall_counts = historical_df['month_day'].value_counts().sort_index()

    # Convert month_day back to datetime for plotting, assuming a common year (e.g., 2023)
    snowfall_counts.index = pd.to_datetime(snowfall_counts.index, format='%m-%d').map(lambda x: x.replace(year=2023))

    # Determine the x-axis limits based on the data with a 2-day buffer
    start_date = snowfall_counts.index.min() - pd.DateOffset(days=2)
    end_date = snowfall_counts.index.max() + pd.DateOffset(days=2)

    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(snowfall_counts.index, snowfall_counts.values, color='skyblue', edgecolor='black')

    # Set x-axis limits to show the 2-day buffer
    ax.set_xlim(start_date, end_date)

    # Set x-axis to show only months
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%b'))
    ax.set_xticks(pd.date_range(start=start_date, end=end_date, freq='MS'))

    # Annotate each bar with the corresponding day of the month
    for bar, date in zip(bars, snowfall_counts.index):
        height = bar.get_height()
        day = date.strftime('%d')
        ax.text(bar.get_x() + bar.get_width() / 2, height, day, ha='center', va='bottom')

    # Set y-axis to only show whole numbers
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    # Set labels and title
    ax.set_xlabel('Month')
    ax.set_ylabel('Number of Occurrences')
    ax.set_title('First Snowfall Frequency by Calendar Day')

    plt.tight_layout()
    return fig