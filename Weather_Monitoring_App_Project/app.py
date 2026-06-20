from flask import Flask, render_template, request
import requests
import sqlite3
from datetime import datetime
from sklearn.linear_model import LinearRegression
import numpy as np

app = Flask(__name__)

API_KEY = "a050a196c2e4d82580a14dc5d2d526a3"

# Create Database
conn = sqlite3.connect('weather.db')
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS history(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT,
    temperature REAL,
    humidity INTEGER,
    wind REAL,
    date_time TEXT
)
""")

conn.commit()
conn.close()


@app.route("/", methods=["GET", "POST"])
def index():

    weather = None

    if request.method == "POST":

        city = request.form["city"]

        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

        response = requests.get(url)

        data = response.json()

        if data["cod"] == 200:

            weather = {
                "city": data["name"],
                "temp": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "wind": data["wind"]["speed"],
                "description": data["weather"][0]["description"],
                "icon": data["weather"][0]["icon"]
            }

            current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

            conn = sqlite3.connect("weather.db")
            cursor = conn.cursor()

            cursor.execute("""
            INSERT INTO history
            (city,temperature,humidity,wind,date_time)
            VALUES(?,?,?,?,?)
            """,
            (
                weather["city"],
                weather["temp"],
                weather["humidity"],
                weather["wind"],
                current_time
            ))

            conn.commit()
            conn.close()

    return render_template("index.html", weather=weather)


@app.route("/history")
def history():

    conn = sqlite3.connect("weather.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM history ORDER BY id DESC")

    records = cursor.fetchall()

    conn.close()

    return render_template("history.html", records=records)

@app.route("/analytics")
def analytics():

    conn = sqlite3.connect("weather.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT city, temperature, humidity, wind, date_time
        FROM history
        ORDER BY id DESC
        LIMIT 1
    """)

    record = cursor.fetchone()

    conn.close()

    if record is None:
        return "No weather data available. Search a city first."

    city = record[0]
    temp = record[1]
    humidity = record[2]
    wind = record[3]
    date_time = record[4]

    return render_template(
        "analytics.html",
        city=city,
        temp=temp,
        humidity=humidity,
        wind=wind,
        date_time=date_time
    )   

    
@app.route("/forecast")
def forecast():

    city = "London"  # You can change this to any city you want

    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"

    response = requests.get(url)
    data = response.json()

    forecast_data = []

    if response.status_code == 200:

        for item in data["list"][::8]:

            forecast_data.append({
                "date": item["dt_txt"].split()[0],
                "temp": item["main"]["temp"],
                "description": item["weather"][0]["description"]
            })

    return render_template(
        "forecast.html",
        forecast=forecast_data
    )
@app.route("/prediction")
def prediction():

    temperatures = [28, 29, 30, 31, 30, 29]

    X = np.array(range(len(temperatures))).reshape(-1, 1)
    y = np.array(temperatures)

    model = LinearRegression()
    model.fit(X, y)

    tomorrow = model.predict([[len(temperatures)]])[0]

    return render_template(
        "prediction.html",
        prediction=round(tomorrow, 2)
    )
if __name__ == "__main__":
    app.run(debug=True)