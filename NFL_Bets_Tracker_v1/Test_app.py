import os
import streamlit as st
import pandas as pd
import sqlite3

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

def format_currency(amount):
    """Format a number as currency."""
    try:
        amount = float(amount)  # Ensure amount is numeric
        return '${:,.2f}'.format(amount)
    except ValueError:
        return '$0.00'  # Return default value if conversion fails

# Title of the summary page
st.title("Bets Summary")

# Load data function
def load_data():
    # Load bets into DataFrame
    bets_df = pd.read_sql('SELECT * FROM bets', conn)
    return bets_df

# Load the bets data
bets_df = load_data()
current_bets_df = bets_df[bets_df['Date'] >= '2024-08-01']
if current_bets_df.empty:
    st.write("No 2024 bets data available.")
else:
    # Calculate total bets
    total_bets = len(current_bets_df)
    #st.write(f"Total Bets: {total_bets}")

    # Calculate total wins and losses
    won_bets = len(current_bets_df[current_bets_df["Outcome"] == "Won"])
    lost_bets = len(current_bets_df[current_bets_df["Outcome"] == "Lost"])
    #st.write(f"Total Wins: {won_bets}")
    #st.write(f"Total Losses: {lost_bets}")

    # Calculate win percentage
    win_percentage = (won_bets / total_bets * 100) if total_bets > 0 else 0
    #st.write(f"Win Percentage: {win_percentage:.2f}%")

    
    # Calculate total dollars gained
    completed_bets = current_bets_df[current_bets_df["Outcome"].isin(["Won", "Lost"])]
    # Ensure 'dollars' and 'wager' columns are numeric
    completed_bets['Dollars'] = pd.to_numeric(completed_bets['Dollars'], errors='coerce')
    completed_bets['Wager'] = pd.to_numeric(completed_bets['Wager'], errors='coerce')

    dollars_won = completed_bets['Dollars'].sum()
    dollars_wagered = completed_bets['Wager'].sum()

    roi = (dollars_won / dollars_wagered * 100) if dollars_wagered > 0 else 0
    #st.write(f"Possible Profit Gained: {format_currency(completed_bets['dollars'].sum())}")
    #st.write(f"Possible Profit Gained: {roi:.2f}%")
    #st.write(f"Possible Profit Gained: {format_currency(dollars_wagered)}")

    

    # Display statistics in the first column

    st.subheader("Bet Counts", divider=True)
    st.write(f"Total Bets: {total_bets}")
    st.write(f"Total Wins: {won_bets}")
    st.write(f"Total Losses: {lost_bets}")
    st.write(f"Win Percentage: {win_percentage:.2f}%")

    # Display statistics in the second column

    st.subheader("Dollars and ROI", divider=True)
    st.write(f"Possible Profit Gained: {format_currency(dollars_won)}")
    st.write(f"Total Dollars Wagered: {format_currency(dollars_wagered)}")
    st.write(f"Return on Investment (ROI): {roi:.2f}%")

    st.subheader("Pending Stats", divider=True)
    # Show number of pending bets
    pending_bets = bets_df[bets_df["Outcome"] == "Pending"]
    st.write(f"Total Pending Bets: {len(pending_bets)}")
    st.write(f"Pending Units Wagered: {format_currency(pending_bets['Wager'].sum())}")
    st.write(f"Possible Profit Gained: {format_currency(pending_bets['Dollars'].sum())}")

    
st.subheader("Bets by Expert (Current NFL Season)", divider=True)

# Aggregate the bets data
expert_summary_current = current_bets_df.groupby('Expert').agg({
    'id': 'count', 
    'Dollars': 'sum', 
    'Outcome': lambda x: (x == 'Won').sum(),  # Count won bets
}).rename(columns={'id': 'Total Bets', 'Dollars': 'Dollars Gained', 'Outcome': 'Won Bets'})

# Add Lost Bets and Win Percentage to the summary
expert_summary_current['Lost Bets'] = expert_summary_current['Total Bets'] - expert_summary_current['Won Bets']
expert_summary_current['Win Percentage'] = ((expert_summary_current['Won Bets'] / expert_summary_current['Total Bets'] * 100).fillna(0)).apply(lambda x: f"{x:.2f}%")

# Reorder columns
expert_summary_current = expert_summary_current[['Total Bets', 'Won Bets', 'Lost Bets', 'Win Percentage', 'Dollars Gained']]

# Display the expert summary for current bets
st.write(expert_summary_current)

st.subheader("Bets by Expert (Last NFL Season)", divider=True)
# Filter for bets placed before 08/01/2024
prior_bets_df = bets_df[bets_df['Date'] < '2024-08-01']
# Aggregate the bets data
expert_summary_prior = prior_bets_df.groupby('Expert').agg({
    'id': 'count', 
    'Dollars': 'sum', 
    'Outcome': lambda x: (x == 'Won').sum(),  # Count won bets
}).rename(columns={'id': 'Total Bets', 'Dollars': 'Dollars Gained', 'Outcome': 'Won Bets'})

# Add Lost Bets and Win Percentage to the summary
expert_summary_prior['Lost Bets'] = expert_summary_prior['Total Bets'] - expert_summary_prior['Won Bets']
expert_summary_prior['Win Percentage'] = ((expert_summary_prior['Won Bets'] / expert_summary_prior['Total Bets'] * 100).fillna(0)).apply(lambda x: f"{x:.2f}%")

# Reorder columns
expert_summary_prior = expert_summary_prior[['Total Bets', 'Won Bets', 'Lost Bets', 'Win Percentage', 'Dollars Gained']].sort_values(by="Dollars Gained", ascending=False)

# Display the expert summary for prior bets
st.write(expert_summary_prior)

    