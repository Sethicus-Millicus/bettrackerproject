import streamlit as st
import pandas as pd

bet_type_list = ['Player Prop', 'Spread', 'Side', 'Total', 'Special']

# Title of the app
st.title("Best Bets Tracker")

# Sidebar input for adding new bets
st.sidebar.header("Add a New Bet")
bet_date = st.sidebar.date_input("Date")
bettor = st.sidebar.text_input("Expert")
week_no = st.sidebar.number_input("Week")
pick_type = st.sidebar.selectbox("Team/Player", ["Player", "Team", 'Special'])
pick_answer = st.sidebar.text_input("Pick")
bet_type = st.sidebar.selectbox("Bet Type", bet_type_list)
odds = st.sidebar.number_input("Odds")
outcome = st.sidebar.selectbox("Outcome", ['Pending', "Won", "Lost"])
submit = st.sidebar.button("Add Bet")

# Load or create a DataFrame to store bets
if "bets" not in st.session_state:
    st.session_state.bets = pd.DataFrame(columns=["Date", "Week", "Expert", "Team/Player", 'Pick', "Bet Type", "Odds", "Outcome"])

# Add new bet to the DataFrame
if submit:
    new_bet = pd.DataFrame([[bet_date, week_no, bettor, pick_type, pick_answer, bet_type, odds, outcome]], columns=st.session_state.bets.columns)
    st.session_state.bets = pd.concat([st.session_state.bets, new_bet], ignore_index=True)

# Filter bets into Pending and Completed (Won/Lost)
pending_bets = st.session_state.bets[st.session_state.bets["Outcome"] == "Pending"]
completed_bets = st.session_state.bets[st.session_state.bets["Outcome"].isin(["Won", "Lost"])]

# Display Pending Bets
st.subheader("Pending Bets")
st.write(pending_bets)

# Allow editing of pending bets
if not pending_bets.empty:
    st.subheader("Edit Pending Bets")
    bet_to_edit = st.selectbox("Select a Bet to Update", pending_bets.index, format_func=lambda x: f"{pending_bets.at[x, 'Pick']} ({pending_bets.at[x, 'Bet Type']})")

    # Update the selected bet's outcome
    new_outcome = st.selectbox("Update Outcome", ["Won", "Lost"])
    update = st.button("Update Bet")

    if update:
        st.session_state.bets.at[bet_to_edit, "Outcome"] = new_outcome
        st.success(f"Bet updated to {new_outcome}!")

# Display Completed Bets
st.subheader("Completed Bets")
st.write(completed_bets)

# Calculate and display statistics
st.subheader("Performance Summary")
won_bets = st.session_state.bets[st.session_state.bets["Outcome"] == "Won"]
win_percentage = len(won_bets) / len(st.session_state.bets) * 100 if len(st.session_state.bets) > 0 else 0
st.write(f"Total Bets: {len(st.session_state.bets)}")
st.write(f"Win Percentage: {win_percentage:.2f}%")

# Written Summary Section
st.subheader("Summary and Insights")
st.write("""
This section provides a brief summary of your betting performance for the week.

- **Total Bets**: Track the total number of bets placed.
- **Win Percentage**: Analyze your success rate.
- **Key Insights**:
    - Look for patterns in your betting strategy.
    - Identify areas where you can improve.
    - Consider external factors like team performance or weather that might affect outcomes.

Use this information to refine your strategy and make more informed bets in the future.
""")