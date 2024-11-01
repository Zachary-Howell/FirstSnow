import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

def plot_snowfall_timeline(first_snow_date=None, winner=None, predicted_snowfall_date_openmeteo=None):
    """
    Creates a Plotly timeline for snowfall guesses and the actual snowfall date if available.

    Parameters:
        guesses (dict): Dictionary of guesses with player names as keys and guess dates as values.
        first_snow_date (datetime.date, optional): The first snowfall date, if snowfall has occurred.
        winner (str, optional): The name of the person with the closest guess, if snowfall has occurred.

    Returns:
        fig (plotly.graph_objects.Figure): The Plotly figure object for the timeline.
    """
    # Prepare data for Plotly
    with open('config/guesses.json') as f:
        guesses = json.load(f)
    
    guess_data = [{"Name": name, "Date": pd.to_datetime(date)} for name, date in guesses.items()]
    df = pd.DataFrame(guess_data)

    # Group by Date and aggregate names for duplicate guesses
    df = df.groupby("Date").agg({
        "Name": lambda names: ', '.join(names)  # Combine names with the same date
    }).reset_index()

    # Set all points to the same y-axis value (e.g., "Guesses")
    df["Category"] = "Guesses"

    # Sort the data by date to connect points in chronological order
    df = df.sort_values(by="Date")

    # Add the first snowfall date as a separate entry if available, converting it to datetime
    if first_snow_date:
        df = df.append({
            "Name": "First Snowfall",
            "Date": pd.to_datetime(first_snow_date).to_pydatetime(),
            "Category": "First Snowfall"
        }, ignore_index=True)

    # Create custom hover text with full name and date/time
    df["HoverText"] = df.apply(lambda row: f"{row['Name']}<br>{row['Date'].strftime('%m/%d %H:%M')}", axis=1)

    # Create visible text with only initials
    df["Initials"] = df["Name"].apply(get_initials)

    # Create the Plotly figure with points and lines connecting them
    fig = go.Figure()

    # Add line trace connecting all points in chronological order with custom hover and initials for visible text
    fig.add_trace(go.Scatter(
        x=df["Date"],
        y=df["Category"],
        mode="lines+markers+text",
        marker=dict(size=10),
        line=dict(color="blue"),
        text=df["Initials"],             # Display initials as always-visible text
        textposition="top center",       # Position initials text above points
        hovertext=df["HoverText"],       # Full name and date/time on hover
        hoverinfo="text",
        name="Guesses"
    ))

    # Convert current date to milliseconds since epoch
    current_date = datetime.now().timestamp() * 1000
    fig.add_vline(
        x=current_date,
        line_dash="dash",
        line_color="red",
        annotation_text="Today",
        annotation_position="top"
    )

    # Highlight the winner if available by adjusting marker color and size
    if winner:
        fig.add_trace(go.Scatter(
            x=[df.loc[df["Name"].str.contains(winner), "Date"].values[0]],
            y=["Guesses"],
            mode="markers+text",
            text=["Winner"],
            textposition="top center",
            marker=dict(size=12, color="gold", symbol="star"),
            name="Winner"
        ))

    # Add Open-Meteo forecasted snowfall date vline if available
    if predicted_snowfall_date_openmeteo:
        # Parse the predicted date and convert to milliseconds since epoch
        forecast_date = datetime.strptime(predicted_snowfall_date_openmeteo, '%Y-%m-%d').timestamp() * 1000
        fig.add_vline(
            x=forecast_date,
            line_dash="dot",
            line_color="blue",
            annotation_text="Forecasted Snowfall",
            annotation_position="top"
        )

    # Customize the layout for readability
    fig.update_layout(
        yaxis=dict(showticklabels=False, showgrid=False, title=None),
        showlegend=False
    )

    return fig

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

def plot_snowfall_data(snowfall_df):
    """
    Creates a Plotly line chart of snowfall data over a specified period.
    
    Parameters:
        snowfall_df (pd.DataFrame): DataFrame containing Date and Snowfall (inches) columns.
    
    Returns:
        fig (plotly.graph_objects.Figure): The Plotly figure object for the chart.
    """
    # Create a Plotly line chart
    fig = px.line(
        snowfall_df,
        x="Date",
        y="Snowfall (inches)",
        title="Daily Snowfall (inches)",
        labels={"Snowfall (inches)": "Snowfall (inches)", "Date": "Date"}
    )

    # Customize the appearance and set y-axis minimum to 0
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Snowfall (inches)"
    )

    return fig

def get_initials(names):
    """Helper function to get initials from one or multiple names."""
    initials_list = [f"{name.split()[0][0]}{name.split()[1][0]}" if len(name.split()) > 1 else name[0]
                     for name in names.split(', ')]
    return ', '.join(initials_list)