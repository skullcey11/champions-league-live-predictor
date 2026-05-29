import sqlite3
import pandas as pd

# connect to the SQLite database
conn = sqlite3.connect("data/database.sqlite")

# see available tables
tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
print("Available tables in the database:")
print(tables)

# extract match data
matches = pd.read_sql_query("SELECT * FROM Match;", conn)

# save as csv 
matches.to_csv("data/matches.csv", index=False)

print ("Data extraction complete. Matches data saved to 'data/matches.csv'.")
conn.close()
