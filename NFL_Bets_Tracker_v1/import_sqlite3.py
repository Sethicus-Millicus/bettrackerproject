import sqlite3


def reset_database():
    try:
        # Connect to SQLite database
        conn = sqlite3.connect('test_db.sqlite')
        c = conn.cursor()
        
        # Drop existing table
        c.execute('DROP TABLE IF EXISTS bets')
        conn.commit()
        
        # Recreate the table with the updated schema
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
    finally:
        conn.close()

# Call this function to reset the database
reset_database()