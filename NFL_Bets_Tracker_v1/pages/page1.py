import os
import streamlit as st
import pandas as pd
import sqlite3
import io

# Fetch the DATABASE_URL from environment variables
DATABASE_URL = os.getenv('DATABASE_URL', 'C:/Users/sethmiller_ryanlawn/OneDrive - Ryan Lawn and Tree/Desktop/Home/NFL/NFL_Bets_Tracker_v1/test_db.sqlite')

# Check if DATABASE_URL is available
if not DATABASE_URL:
    st.error("DATABASE_URL environment variable not set.")
    st.stop()

# Connect to SQLite database
try:
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
except Exception as e:
    st.error(f"Failed to connect to the database: {e}")
    st.stop()

# Create bets table if it doesn't exist
c.execute('''
CREATE TABLE IF NOT EXISTS bets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Date TEXT,
    Week INTEGER,
    Expert TEXT,
    Team_Player TEXT,
    Pick TEXT,
    Type TEXT,
    Side TEXT,
    Wager REAL,
    Odds INTEGER,
    Outcome TEXT,
    Dollars REAL
)
''')
conn.commit()


#def format_currency(amount):
#    return '${:,.2f}'.format(amount)


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
pending_bets = bets_df[bets_df["Outcome"] == "Pending"]

# Create tabs
tab1, tab2 = st.tabs(["Pending Bets", "Completed Bets"])

with tab1:
    # Display Pending Bets
    st.subheader("Pending Bets")
    # Add new bet section in the main body
    with st.expander("Add a New Bet"):
        with st.form(key='add_bet_form'):
            bet_date = st.date_input("Date")
            bettor = st.selectbox("Expert", ["Seth", "DT","Cade",'Yani','Jacob','Tristen','Micah','TD Queen','Nick'])
            week_no = st.number_input("Week", min_value=1, step=1)
            pick_type = st.selectbox("Team/Player", ["Player", "Team"])
            pick_answer = st.text_input("Pick")
            bet_type = st.selectbox("Bet Type", ['Passing Yards', 'Rushing Yards', 'Receiving TDs', 'Passing TDs', 'Rushing And Receiving Yards','ATS', 'MoneyLine', 'Total', 'Special'])
            bet_side = st.text_input("Side")
            wager = st.number_input("Wager", min_value=1, step=1)
            odds = st.number_input("Odds", step=1, format="%d", value=0)
            outcome = st.selectbox("Outcome", ['Pending', "Won", "Lost"])
            submit = st.form_submit_button("Add Bet")

            if submit:
                # Calculate dollars based on odds
                if odds > 0:
                    dollars =  (odds / 100)* wager
                elif odds < 0:
                    dollars = (100 / (-odds))* wager
                else:
                    dollars = wager
                
                # Add new bet to the SQLite database
                try:
                    c.execute('''
                        INSERT INTO bets (Date, Week, Expert, Team_Player, Pick, Type, Side, Wager, Odds, Outcome, Dollars)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (bet_date, week_no, bettor, pick_type, pick_answer, bet_type, bet_side, wager, odds, outcome, dollars))
                    conn.commit()
                    st.success("Bet added!")
                    # Reload data after adding a new bet
                    bets_df = load_data()
                    pending_bets = bets_df[bets_df["Outcome"] == "Pending"]
                except Exception as e:
                    st.error(f"Failed to add bet: {e}")

    # Show pending bets update section only if there are pending bets
    if not pending_bets.empty:
        with st.expander("Update Pending Bets"):
            st.subheader("Edit Pending Bets")
            bet_to_edit = st.selectbox(
                "Select a Bet to Update", 
                pending_bets['id'], 
                format_func=lambda x: f"{pending_bets.loc[pending_bets['id'] == x, 'Pick'].values[0]} ({pending_bets.loc[pending_bets['id'] == x, 'Type'].values[0]})"
            )

            # Update the selected bet's outcome
            new_outcome = st.selectbox("Update Outcome", ["Won", "Lost"])
            update = st.button("Update Bet")

            if update:
                # Determine new dollars value based on outcome
                if new_outcome == "Lost":
                    new_dollars = -pending_bets.loc[pending_bets['id'] == bet_to_edit, 'Wager'].values[0]
                else:
                    new_dollars = pending_bets.loc[pending_bets['id'] == bet_to_edit, 'Dollars'].values[0]

                try:
                    c.execute('UPDATE bets SET Outcome = ?, Dollars = ? WHERE id = ?', (new_outcome, new_dollars, bet_to_edit))
                    conn.commit()
                    st.success(f"Bet updated to {new_outcome}!")
                    # Reload the data after updating
                    bets_df = load_data()
                    pending_bets = bets_df[bets_df["Outcome"] == "Pending"]
                except Exception as e:
                    st.error(f"Failed to update bet: {e}")

    # Display Pending Bets at the top
    st.subheader("Pending Bets")
    st.dataframe(pending_bets[['Expert','Team_Player','Pick','Side','Odds']], width=1000) 

with tab2:
    # Convert date column to datetime if it's not already
    bets_df['Date'] = pd.to_datetime(bets_df['Date'], errors='coerce')
    
    # Filter bets to include only those from the last 10 days
    today = pd.to_datetime('today')
    last_ten_days = today - pd.Timedelta(days=10)
    completed_bets = bets_df[bets_df["Outcome"].isin(["Won", "Lost"]) & (bets_df['Date'] >= last_ten_days)]
    
    # Display Completed Bets from the last 10 days
    st.subheader("Completed Bets (Last 10 Days)")
    st.dataframe(completed_bets, width=1000)

    