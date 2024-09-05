import streamlit as st
import pandas as pd
import sqlite3

# Connect to SQLite database (or create it)
conn = sqlite3.connect('bets.db', check_same_thread=False)
c = conn.cursor()

# Create bets table if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS bets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        week INTEGER,
        expert TEXT,
        pick_type TEXT,
        pick_answer TEXT,
        bet_type TEXT,
        odds REAL,
        outcome TEXT
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
completed_bets = bets_df[bets_df["outcome"].isin(["Won", "Lost"])]

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
            pick_type = st.selectbox("Team/Player", ["Player", "Team", 'Special'])
            pick_answer = st.text_input("Pick")
            bet_type = st.selectbox("Bet Type", ['Player Prop', 'Spread', 'Side', 'Total', 'Special'])
            odds = st.number_input("Odds")
            outcome = st.selectbox("Outcome", ['Pending', "Won", "Lost"])
            submit = st.form_submit_button("Add Bet")

        # Add new bet to the SQLite database
        if submit:
            c.execute('''
                INSERT INTO bets (date, week, expert, pick_type, pick_answer, bet_type, odds, outcome)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (bet_date, week_no, bettor, pick_type, pick_answer, bet_type, odds, outcome))
            conn.commit()
            st.success("Bet added!")
            # Reload data after adding a new bet
            bets_df = load_data()
            pending_bets = bets_df[bets_df["outcome"] == "Pending"]

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
                c.execute('UPDATE bets SET outcome = ? WHERE id = ?', (new_outcome, bet_to_edit))
                conn.commit()
                st.success(f"Bet updated to {new_outcome}!")

                # Reload the data after updating
                bets_df = load_data()
                pending_bets = bets_df[bets_df["outcome"] == "Pending"]

    # Display Pending Bets at the top
    st.subheader("Pending Bets")
    st.write(pending_bets)

with tab2:
    # Display Completed Bets in a separate tab
    st.subheader("Completed Bets")
    st.write(completed_bets)