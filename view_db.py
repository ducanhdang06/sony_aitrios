import sqlite3

conn = sqlite3.connect("people_guide.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM people_log ORDER BY id DESC LIMIT 20")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()