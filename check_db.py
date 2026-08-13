import sqlite3

conn = sqlite3.connect("bluestock_mf.db")

cursor = conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table';"
)

print("Tables in database:")
for row in cursor.fetchall():
    print(row[0])

conn.close()