from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

def fetch_logs(limit=50):
    conn = sqlite3.connect("people_counter.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM people_log ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

@app.route("/")
def index():
    logs = fetch_logs()
    return render_template("index.html", logs=logs)

if __name__ == "__main__":
    app.run(debug=True)
