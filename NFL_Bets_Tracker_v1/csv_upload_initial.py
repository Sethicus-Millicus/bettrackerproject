import sqlite3
import pandas as pd

def import_csv_to_db(csv_path, db_path='test_db.sqlite'):
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(db_path)

        # Load CSV data into a DataFrame
        df = pd.read_csv(csv_path)

        # Ensure the DataFrame has the correct columns
        expected_columns = {'Date', 'Week', 'Expert', 'Team_Player', 'Pick', 'Type', 'Side', 'Wager', 'Odds', 'Outcome', 'Dollars'}
        if not expected_columns.issubset(df.columns):
            print("CSV file does not have the required columns.")
            return
        
        # Insert DataFrame into the database
        df.to_sql('bets', conn, if_exists='append', index=False)

        print("CSV data has been imported successfully.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    
    finally:
        if conn:
            conn.close()

# Example usage
import_csv_to_db("C:/Users/sethmiller_ryanlawn/OneDrive - Ryan Lawn and Tree/Desktop/Home/NFL/NFL_Bets_Tracker/NFL 23 - Sheet3.csv")