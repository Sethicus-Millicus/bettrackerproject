import os
import streamlit as st
import pandas as pd
import psycopg2



# Fetch the DATABASE_URL from environment variables
DATABASE_URL = os.getenv('DATABASE_URL')

# Check if DATABASE_URL is available
if not DATABASE_URL:
    st.error("DATABASE_URL environment variable not set.")
    st.stop()

# Connect to PostgreSQL database (or create it)
try:
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    c = conn.cursor()
except Exception as e:
    st.error(f"Failed to connect to the database: {e}")
    st.stop()

# Title of the summary page
st.title("Bets Summary")

# Load data function
def load_data():
    # Load bets into DataFrame
    bets_df = pd.read_sql('SELECT * FROM bets', conn)
    return bets_df

# Load the bets data
bets_df = load_data()

# Calculate total bets
total_bets = len(bets_df)
st.write(f"Total Bets: {total_bets}")

# Calculate total wins and losses
won_bets = len(bets_df[bets_df["outcome"] == "Won"])
lost_bets = len(bets_df[bets_df["outcome"] == "Lost"])
st.write(f"Total Wins: {won_bets}")
st.write(f"Total Losses: {lost_bets}")

# Calculate win percentage
win_percentage = (won_bets / total_bets * 100) if total_bets > 0 else 0
st.write(f"Win Percentage: {win_percentage:.2f}%")

# Show number of pending bets
pending_bets = bets_df[bets_df["outcome"] == "Pending"]
st.write(f"Total Pending Bets: {len(pending_bets)}")

# Display summary of bets by expert
st.subheader("Bets by Expert")
expert_summary = bets_df.groupby('expert').size().reset_index(name='Total Bets')
st.write(expert_summary)