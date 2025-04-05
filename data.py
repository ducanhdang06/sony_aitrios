import time
import requests
import sqlite3
from datetime import datetime
import random


# Create the SQLite table (runs only once if table doesn't exist)
def create_table():
    conn = sqlite3.connect("people_counter.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS people_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            time TEXT,
            people_count INTEGER
        )
    """)
    conn.commit()
    conn.close()

# Insert a new log entry
def insert_log(people_count):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    conn = sqlite3.connect("people_counter.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO people_log (date, time, people_count) VALUES (?, ?, ?)",
                   (date_str, time_str, people_count))
    conn.commit()
    conn.close()

# Count how many 'people' were detected (class_id == 0)
def count_people(detections):
    return sum(1 for d in detections if d.get('class_id') == 0)

# Replace this with your actual API endpoint
def get_api_result():
    print("📡 Attempting API call...")
    try:
        response = requests.get(
            "https://0myrzet12k.execute-api.us-east-1.amazonaws.com/prod/devices/Aid-80070001-0000-2000-9002-000000000f25/data?key=202504ut&pj=kyoro"
        )
        response.raise_for_status()  # raise an error for bad status codes
        data = response.json()
        print("✅ API call successful!")
        print(data)
        return data
    except requests.exceptions.RequestException as e:
        print("❌ API call failed:", e)
        return {}

    

def get_api_result_test():
    num_people = random.randint(0, 5)  # simulate 0 to 5 people
    other_classes = [16, 17, 64, 66]   # simulate some other detections

    detections = []

    # Add "people" (class_id = 0)
    for _ in range(num_people):
        detections.append({
            "class_id": 0,
            "confidence": round(random.uniform(0.4, 0.9), 3),
            "bbox": {
                "left": random.randint(0, 100),
                "top": random.randint(0, 100),
                "right": random.randint(100, 300),
                "bottom": random.randint(100, 300)
            }
        })

    # Add 0–2 random other detections
    for _ in range(random.randint(0, 2)):
        detections.append({
            "class_id": random.choice(other_classes),
            "confidence": round(random.uniform(0.3, 0.7), 3),
            "bbox": {
                "left": random.randint(0, 100),
                "top": random.randint(0, 100),
                "right": random.randint(100, 300),
                "bottom": random.randint(100, 300)
            }
        })

    return {"detections": detections}

# Main loop - logs every 30 seconds
def main():
    create_table()
    print("👋 Script started")
    print("Starting people tracker...")
    while True:
        data = get_api_result()
        detections = data.get("detections", [])
        people_count = count_people(detections)
        insert_log(people_count)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] People detected: {people_count}")
        time.sleep(5)

if __name__ == "__main__":
    main()
