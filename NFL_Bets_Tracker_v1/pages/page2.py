import os
import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go
import plotly.express as px

# Fetch the DATABASE_URL from environment variables
DATABASE_URL = os.getenv('DATABASE_URL', 'C:/Users/sethmiller_ryanlawn/OneDrive - Ryan Lawn and Tree/Desktop/Home/NFL/NFL_Bets_Tracker_v1/test_db.sqlite')

# Check if DATABASE_URL is available
if not DATABASE_URL:
    st.error("DATABASE_URL environment variable not set.")
    st.stop()

try:
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
except Exception as e:
    st.error(f"Failed to connect to the database: {e}")
    st.stop()

def load_data():
    # Load bets into DataFrame
    bets_df = pd.read_sql('SELECT * FROM bets', conn)
    return bets_df

# Load the bets data
bets_df = load_data()

if bets_df.empty:
    st.write("No bets data available.")
else:
    # Filter data for this year and last year
    this_year_bets = bets_df[bets_df['Date'] >= '2024-01-01']
    last_year_bets = bets_df[bets_df['Date'] < '2024-01-01']
    
    # Most common bet types
    bet_type_counts = last_year_bets['Type'].value_counts()
    bet_pick_counts = last_year_bets['Pick'].value_counts()
    dollars_per_pick = last_year_bets.groupby('Pick')['Dollars'].sum().sort_values(ascending=False)
    dollars_per_type = last_year_bets.groupby('Type')['Dollars'].sum().sort_values(ascending=False)
    
    # Select top 5 and bottom 5 picks
    top_5_picks = dollars_per_pick.head(5)
    bottom_5_picks = dollars_per_pick.tail(5)
    top_bottom_5_picks = pd.concat([top_5_picks, bottom_5_picks]).sort_values(ascending=False)
    # Select top 5 and bottom 5 type

    #st.write(top_bottom_5_picks)

    # Plot Most Common Bet Types
    st.subheader("Most Common Bet Types(Last Year)")
    bet_type_fig = px.bar(
        bet_type_counts.reset_index(),
        x='Type',
        y='count',
        labels={'count': 'Count', 'Type': 'Bet Type'},
        title='Most Common Bet Types',
        color_discrete_sequence=['#228B22']
    )
    st.plotly_chart(bet_type_fig)


    # Plot Sum of Dollars Per Pick (Top 5 and Bottom 5)
    st.subheader("Sum of Dollars Type (Last Year) - Top 5 and Bottom 5")
    top_bottom_5_type = dollars_per_type.reset_index()
    top_bottom_5_type.columns = ['Type', 'Total Dollars']
    top_bottom_5_type['Color'] = 0>top_bottom_5_type["Total Dollars"]
    
    dollars_per_type_fig = px.bar(
        top_bottom_5_type,
        x='Type',
        y='Total Dollars',
        color='Color',
        color_discrete_map={False: '#4682B4', True: 'lightcoral'},
        labels={'Type': 'Bet Type', 'Total Dollars': 'Total Dollars'},
        title='Sum of Dollars Wagered per Pick (Top 5 and Bottom 5)'
    )
    dollars_per_type_fig.update_layout(showlegend=False)
    st.plotly_chart(dollars_per_type_fig)


    # Plot Most Common Bet Picks
    st.subheader("Most Common Bet Picks (Last Year)")
    top_10_bet_picks = bet_pick_counts.head(10).reset_index()
    top_10_bet_picks.columns = ['Pick', 'Count']

    bet_pick_fig = px.bar(
        top_10_bet_picks,
        x='Pick',
        y='Count',
        labels={'Pick': 'Bet Pick', 'Count': 'Count'},
        title='Most Common Bet Picks',
        color_discrete_sequence=['#F4A460']
    )
    st.plotly_chart(bet_pick_fig)


    # Plot Sum of Dollars Per Pick (Top 5 and Bottom 5)
    st.subheader("Sum of Dollars Pick (Last Year) - Top 5 and Bottom 5")
    top_bottom_5_picks = top_bottom_5_picks.reset_index()
    top_bottom_5_picks.columns = ['Pick', 'Total Dollars']
    top_bottom_5_picks['Color'] = ['Top 5'] * len(top_5_picks) + ['Bottom 5'] * len(bottom_5_picks)
    
    dollars_per_pick_fig = px.bar(
        top_bottom_5_picks,
        x='Pick',
        y='Total Dollars',
        color='Color',
        color_discrete_map={'Top 5': 'skyblue', 'Bottom 5': 'lightcoral'},
        labels={'Pick': 'Bet Pick', 'Total Dollars': 'Total Dollars'},
        title='Sum of Dollars Wagered per Pick (Top 5 and Bottom 5)'
    )
    st.plotly_chart(dollars_per_pick_fig)