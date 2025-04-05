from flask import Flask, render_template, request
import random
import sqlite3
import requests
from datetime import datetime
import time
import threading

app = Flask(__name__)

# ---- MOCK ATTRACTIONS DATA ----
attractions_by_city = {
    "Los Angeles": [
        {"name": "Griffith Observatory", "lat": 34.1184, "lng": -118.3004, "api_url": "", "image": "https://griffithobservatory.org/wp-content/uploads/2021/03/cameron-venti-c5GkEd-j5vI-unsplash_noCautionTape.jpg"},
        {"name": "Santa Monica Pier", "lat": 34.0092, "lng": -118.4973, "api_url": "", "image": "https://cf.bstatic.com/xdata/images/hotel/max1024x768/566352260.jpg?k=d1e0fd8df62d447efb74470c7da638c4d92cb82ace8049e44740499d3abf96d2&o=&hp=1"},
        {"name": "The Getty", "lat": 34.0780, "lng": -118.4741, "api_url": "", "image": "https://drupal-prod.visitcalifornia.com/sites/default/files/styles/fluid_1920/public/vc_spotlightthegettycenter_hero_st_ed_233927197_1280x640.jpg.webp?itok=tfJ5_6MV"}
    ],
    "New York": [
        {"name": "Central Park", "lat": 40.7851, "lng": -73.9683, "api_url": "", "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/Global_Citizen_Festival_Central_Park_New_York_City_from_NYonAir_%2815351915006%29.jpg/300px-Global_Citizen_Festival_Central_Park_New_York_City_from_NYonAir_%2815351915006%29.jpg"},
        {"name": "Times Square", "lat": 40.7580, "lng": -73.9855, "api_url": "", "image": "https://www.theknickerbocker.com/content/uploads/2024/02/knb_nyc_landmarks_times_square_1138719689.webp"},
        {"name": "The Met", "lat": 40.7794, "lng": -73.9632, "api_url": "", "image": "https://cdn.sanity.io/images/cctd4ker/production/df2942014531e122504b075c1fe6aa6f3f8a3ee5-5120x2880.jpg?w=3840&q=75&fit=clip&auto=format"}
    ],
    "Tokyo": [
        {"name": "Shibuya Crossing", "lat": 35.6681, "lng": 139.7314, "api_url": "", "image": "https://media.timeout.com/images/105946468/image.jpg"},
        {"name": "Senso-ji", "lat": 35.7149, "lng": 139.7966, "api_url": "", "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcStuk4v4XbgfT9f6EwaGeLueL779qdpDTRHPg&s"},
        {"name": "Ghibli Museum", "lat": 35.6812, "lng": 139.7671, "api_url": "", "image": "https://media.cntraveler.com/photos/5c866698ff5475304621749f/16:9/w_2560,c_limit/Ghibli%20Museum_R061NH.jpg"}
    ],
    "Istanbul": [
        {"name": "Blue Mosque", "lat": 41.0082, "lng": 28.9784, "api_url": "", "image": "https://theistanbulinsider.com/wp-content/uploads/2020/03/blue-mosque-aerial.jpg"},
        {"name": "Hagia Sophia", "lat": 41.0082, "lng": 28.9784, "api_url": "", "image": "https://cdn-imgix.headout.com/media/images/b6b2e10d9b209e2c526c2568780379a3-hagia.jpg?auto=format&w=1222.3999999999999&h=687.6&q=90&fit=crop&ar=16%3A9&crop=faces"},
        {"name": "Grand Bazaar", "lat": 41.0082, "lng": 28.9784, "api_url": "", "image": "https://cms.througheternity.com/upload/CONF83/20230906/lamps.jpg"}
    ]
}

# ---- MOCK PEOPLE COUNT ----
def get_mock_people_count():
    return random.randint(0, 100)

# ---- OPTIONAL REAL API FUNCTION ----
def get_people_count_from_api(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        detections = data.get("detections", [])
        return sum(1 for d in detections if d.get("class_id") == 0)
    except Exception as e:
        print(f"❌ Error fetching from {url}: {e}")
        return 0

# ---- CROWD LEVEL CATEGORIZATION ----
def get_crowd_level(count):
    if count < 20:
        return ("Not at all crowded", "low")
    elif count < 50:
        return ("Slightly crowded", "medium")
    else:
        return ("Extremely crowded", "high")

# ---- DATABASE SETUP ----
def create_table():
    conn = sqlite3.connect("people_guide.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS people_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            attraction TEXT,
            date TEXT,
            time TEXT,
            people_count INTEGER
        )
    """)
    conn.commit()
    conn.close()

create_table()

# ---- ROUTES ----
@app.route("/")
def index():
    cities = list(attractions_by_city.keys())
    return render_template("city_selector.html", cities=cities)

@app.route("/city", methods=["POST"])
def show_city():
    city = request.form.get("city")
    attractions = attractions_by_city.get(city, [])

    results = []
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    for attraction in attractions:
        count = get_mock_people_count()
        level_text, level_class = get_crowd_level(count)

        conn = sqlite3.connect("people_guide.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO people_log (city, attraction, date, time, people_count)
            VALUES (?, ?, ?, ?, ?)
        """, (city, attraction["name"], date_str, time_str, count))
        conn.commit()
        conn.close()

        results.append({
            "name": attraction["name"],
            "count": count,
            "level_text": level_text,
            "level_class": level_class,
            "image": attraction.get("image", "https://via.placeholder.com/400x300?text=No+Image"),
            "lat": attraction.get("lat"),
            "lng": attraction.get("lng")
        })

    results.sort(key=lambda x: x["count"])
    return render_template(
        "city.html",
        city=city,
        results=results,
        chart_data={
            "labels": [r["name"] for r in results],
            "counts": [r["count"] for r in results],
            "colors": [
                "green" if r["level_class"] == "low"
                else "orange" if r["level_class"] == "medium"
                else "red"
                for r in results
            ]
        }
    )

@app.route("/attraction/<city>/<name>")
def get_attraction_data(city, name):
    conn = sqlite3.connect("people_guide.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT date, time, people_count FROM people_log
        WHERE city = ? AND attraction = ?
        ORDER BY id DESC LIMIT 30
    """, (city, name))
    rows = cursor.fetchall()
    conn.close()

    data = [
        {
            "datetime": f"{row[0]} {row[1]}",
            "people_count": row[2]
        }
        for row in rows[::-1]
    ]
    return {"attraction": name, "data": data}


@app.route("/city_data/<city>")
def get_city_data(city):
    attractions = attractions_by_city.get(city, [])
    response = []

    conn = sqlite3.connect("people_guide.db")
    cursor = conn.cursor()

    for attraction in attractions:
        cursor.execute("""
            SELECT people_count FROM people_log
            WHERE city = ? AND attraction = ?
            ORDER BY id DESC LIMIT 1
        """, (city, attraction["name"]))
        row = cursor.fetchone()
        count = row[0] if row else 0

        level_text, level_class = get_crowd_level(count)

        response.append({
            "name": attraction["name"],
            "count": count,
            "level_text": level_text,
            "level_class": level_class
        })

    conn.close()
    return {"city": city, "data": response}

@app.route("/logs")
def show_logs():
    conn = sqlite3.connect("people_guide.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM people_log ORDER BY id DESC LIMIT 20")
    rows = cursor.fetchall()
    conn.close()
    return "<br>".join([str(row) for row in rows])

def background_logger():
    while True:
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")

        conn = sqlite3.connect("people_guide.db")
        cursor = conn.cursor()

        for city, attractions in attractions_by_city.items():
            for attraction in attractions:
                count = get_mock_people_count()
                cursor.execute("""
                    INSERT INTO people_log (city, attraction, date, time, people_count)
                    VALUES (?, ?, ?, ?, ?)
                """, (city, attraction["name"], date_str, time_str, count))
                # print(f"[{time_str}] Logged {count} people at {attraction['name']} ({city})")

        conn.commit()
        conn.close()
        time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=background_logger, daemon=True).start()
    app.run(debug=True)



