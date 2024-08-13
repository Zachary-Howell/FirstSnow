import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

def plot_player_guesses_timeline(guesses):
    try:
        # Convert guesses to DataFrame and parse dates
        guess_df = pd.DataFrame(list(guesses.items()), columns=['Player', 'Guess'])
        guess_df['Guess'] = pd.to_datetime(guess_df['Guess'])

        # Get today's date
        today = pd.to_datetime(datetime.today().date())

        # Generate unique colors for each player
        colors = plt.cm.get_cmap('tab10', len(guess_df))

        # Create the figure and axis
        fig, ax = plt.subplots(figsize=(10, 2))

        # Plot the timeline (a single horizontal line)
        for idx, row in guess_df.iterrows():
            ax.plot(row['Guess'], 1, "o", color=colors(idx))
            ax.vlines(row['Guess'], 0, 1, colors=colors(idx), linestyle='dotted')
            ax.text(row['Guess'], 1.05, f"{row['Player']}\n{row['Guess'].strftime('%b %d')}", 
                    ha='center', fontsize=8, rotation=45, color=colors(idx))

        # Plot today's date in a distinct color
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

# def plot_historical_snowfall(historical_df):
#     if 'first_snowfall_date' not in historical_df.columns:
#         st.error("The 'first_snowfall_date' column is missing from the historical data.")
#         return None

#     if historical_df.empty:
#         st.error("The historical data is empty.")
#         return None

#     # Convert dates to day of the year (ordinal) for histogram, considering only post-July 1st dates
#     historical_df['day_of_year'] = historical_df['first_snowfall_date'].dt.dayofyear

#     # Create the histogram
#     fig, ax = plt.subplots(figsize=(10, 5))
#     ax.hist(historical_df['day_of_year'], bins=365-182, range=(183, 365), color='skyblue', edgecolor='black')

#     # Set x-axis to show calendar days from July to December
#     ax.set_xticks([datetime(2024, month, 1).timetuple().tm_yday for month in range(7, 13)])
#     ax.set_xticklabels([datetime(2024, month, 1).strftime('%b') for month in range(7, 13)])
#     ax.set_xlim(183, 365)

#     # Set labels and title
#     ax.set_xlabel('Day of Year (Post-Summer)')
#     ax.set_ylabel('Number of Occurrences')
#     ax.set_title('First Snowfall Frequency by Calendar Day (Post-Summer)')

#     plt.tight_layout()
#     return fig

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
    ax.bar(snowfall_counts.index, snowfall_counts.values, color='skyblue', edgecolor='black')

    # Set x-axis limits to show the 2-day buffer
    ax.set_xlim(start_date, end_date)

    # Set x-axis to show labels every 5 days
    ax.set_xticks(pd.date_range(start=start_date, end=end_date, freq='5D'))

    # Set x-axis format to show month and day
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%b %d'))

    # Set labels and title
    ax.set_xlabel('Day of Year')
    ax.set_ylabel('Number of Occurrences')
    ax.set_title('First Snowfall Frequency by Calendar Day')

    plt.tight_layout()
    return fig