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

# Create bets table if it doesn't exist
c.execute('''
CREATE TABLE IF NOT EXISTS bets (
    id SERIAL PRIMARY KEY,
    date DATE,
    week INTEGER,
    expert TEXT,
    pick_type TEXT,
    pick_answer TEXT,
    bet_type TEXT,
    bet_side TEXT,
    wager NUMERIC,
    odds NUMERIC,
    outcome TEXT,
    dollars NUMERIC
)
''')
conn.commit()

# Title of the app
st.title("Bets Tracker")

# Load data function
def load_data():
    # Load bets into DataFrame
    bets_df = pd.read_sql('SELECT * FROM bets', conn)
    return bets_df

# Load the bets data initially
bets_df = load_data()

# Filter bets into Pending and Completed (Won/Lost)
pending_bets = bets_df[bets_df["outcome"] == "Pending"]

# Create tabs
tab1, tab2 = st.tabs(["Pending Bets", "Completed Bets"])

with tab1:
    # Display Pending Bets
    st.subheader("Pending Bets")
    # Add new bet section in the main body
    with st.expander("Add a New Bet"):
        with st.form(key='add_bet_form'):
            bet_date = st.date_input("Date")
            bettor = st.text_input("Expert")
            week_no = st.number_input("Week", min_value=1, step=1)
            pick_type = st.selectbox("Team/Player", ["Player", "Team"])
            pick_answer = st.text_input("Pick")
            if pick_type == "Player":
                bet_type = st.selectbox("Bet Type", ['Passing Yards', 'Rushing Yards', 'Receiving TDs', 'Passing TDs', 'Rushing And Receiving Yards', 'Special'])
            elif pick_type == "Team":
                bet_type = st.selectbox("Bet Type", ['ATS', 'MoneyLine', 'Total', 'Special'])
            bet_side = st.text_input("Side")
            wager = st.number_input("Wager", min_value=1, step=1)
            odds = st.number_input("Odds", format="%0.1f")
            outcome = st.selectbox("Outcome", ['Pending', "Won", "Lost"])
            submit = st.form_submit_button("Add Bet")

            if submit:
                # Calculate dollars based on odds
                if odds > 1:
                    dollars = (((odds / 100) + 1) * 100) * wager
                elif odds < 1:
                    dollars = (((100 / odds) + 1) * 100) * wager
                else:
                    dollars = wager

                # Add new bet to the PostgreSQL database
                try:
                    c.execute('''
                        INSERT INTO bets (date, week, expert, pick_type, pick_answer, bet_type, bet_side, wager, odds, outcome, dollars)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (bet_date, week_no, bettor, pick_type, pick_answer, bet_type, bet_side, wager, odds, outcome, dollars))
                    conn.commit()
                    st.success("Bet added!")
                    # Reload data after adding a new bet
                    bets_df = load_data()
                    pending_bets = bets_df[bets_df["outcome"] == "Pending"]
                except Exception as e:
                    st.error(f"Failed to add bet: {e}")

    # Show pending bets update section only if there are pending bets
    if not pending_bets.empty:
        with st.expander("Update Pending Bets"):
            st.subheader("Edit Pending Bets")
            bet_to_edit = st.selectbox(
                "Select a Bet to Update", 
                pending_bets['id'], 
                format_func=lambda x: f"{pending_bets.loc[pending_bets['id'] == x, 'pick_answer'].values[0]} ({pending_bets.loc[pending_bets['id'] == x, 'bet_type'].values[0]})"
            )

            # Update the selected bet's outcome
            new_outcome = st.selectbox("Update Outcome", ["Won", "Lost"])
            update = st.button("Update Bet")

            if update:
                # Determine new dollars value based on outcome
                if new_outcome == "Lost":
                    new_dollars = -pending_bets.loc[pending_bets['id'] == bet_to_edit, 'wager'].values[0]
                else:
                    new_dollars = pending_bets.loc[pending_bets['id'] == bet_to_edit, 'dollars'].values[0]

                try:
                    c.execute('UPDATE bets SET outcome = %s, dollars = %s WHERE id = %s', (new_outcome, new_dollars, bet_to_edit))
                    conn.commit()
                    st.success(f"Bet updated to {new_outcome}!")
                    # Reload the data after updating
                    bets_df = load_data()
                    pending_bets = bets_df[bets_df["outcome"] == "Pending"]
                except Exception as e:
                    st.error(f"Failed to update bet: {e}")

    # Display Pending Bets at the top
    st.subheader("Pending Bets")
    st.dataframe(pending_bets, width=1000) 

with tab2:
    completed_bets = bets_df[bets_df["outcome"].isin(["Won", "Lost"])]
    # Display Completed Bets in a separate tab
    st.subheader("Completed Bets")
    st.dataframe(completed_bets, width=1000)