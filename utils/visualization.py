import pandas as pd
import plotly.express as px
import streamlit as st

def plot_player_guesses_timeline(guesses):
    try:
        guess_df = pd.DataFrame(list(guesses.items()), columns=['Player', 'Guess'])
        guess_df['Guess'] = pd.to_datetime(guess_df['Guess'])
        guess_df['End'] = guess_df['Guess'] + pd.Timedelta(days=1)  # Add one day to make it visible

        fig_timeline = px.timeline(
            guess_df,
            x_start="Guess",
            x_end="End",
            y="Player",
            color="Player",
            title="Player Guesses Timeline"
        )
        fig_timeline.update_yaxes(categoryorder="total ascending")
        fig_timeline.update_traces(marker=dict(size=12))  # Adjust marker size for better visibility
        return fig_timeline
    except Exception as e:
        st.error(f"An error occurred while creating the timeline: {e}")
        return None
