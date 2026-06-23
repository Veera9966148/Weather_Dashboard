from flask import Flask, render_template, request
from dotenv import load_dotenv
from datetime import datetime, timezone
import requests
import sqlite3
import os

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)

# API Key
API_KEY = os.getenv("API_KEY")

# Database setup
conn = sqlite3.connect("weather.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS searches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT NOT NULL
)
""")
conn.commit()


@app.route("/", methods=["GET", "POST"])
def home():

    weather = None
    forecast = []
    recent = []
    error = None

    try:
        cur.execute("""
            SELECT city
            FROM searches
            GROUP BY city
            ORDER BY id DESC
            LIMIT 5
        """)
        recent = [row[0] for row in cur.fetchall()]
    except:
        recent = []

    if request.method == "POST":

        city = request.form.get("city", "").strip()

        if not city:
            error = "❌ Please enter a city name."

        else:

            try:
                # Current weather URL
                weather_url = (
                    f"https://api.openweathermap.org/data/2.5/weather"
                    f"?q={city}"
                    f"&appid={API_KEY}"
                    f"&units=metric"
                )

                response = requests.get(
                    weather_url,
                    timeout=10
                )

                data = response.json()

                if str(data.get("cod")) == "200":

                    # Timezone correction
                    offset = data["timezone"]

                    sunrise = datetime.fromtimestamp(
                        data["sys"]["sunrise"] + offset,
                        tz=timezone.utc
                    ).strftime("%I:%M %p")

                    sunset = datetime.fromtimestamp(
                        data["sys"]["sunset"] + offset,
                        tz=timezone.utc
                    ).strftime("%I:%M %p")

                    # Weather data
                    weather = {
                        "city": data["name"],
                        "country": data["sys"]["country"],
                        "temp": round(
                            data["main"]["temp"]
                        ),
                        "feels": round(
                            data["main"]["feels_like"]
                        ),
                        "humidity":
                            data["main"]["humidity"],
                        "wind":
                            data["wind"]["speed"],
                        "pressure":
                            data["main"]["pressure"],
                        "description":
                            data["weather"][0][
                                "description"
                            ],
                        "icon":
                            data["weather"][0]["icon"],
                        "sunrise":
                            sunrise,
                        "sunset":
                            sunset
                    }

                    # Save search history
                    try:
                        cur.execute(
                            """
                            INSERT INTO searches(city)
                            VALUES(?)
                            """,
                            (weather["city"],)
                        )
                        conn.commit()
                    except:
                        pass

                    # Forecast API
                    forecast_url = (
                        f"https://api.openweathermap.org/data/2.5/forecast"
                        f"?q={city}"
                        f"&appid={API_KEY}"
                        f"&units=metric"
                    )

                    forecast_response = requests.get(
                        forecast_url,
                        timeout=10
                    )

                    forecast_data = (
                        forecast_response.json()
                    )

                    if str(
                        forecast_data.get("cod")
                    ) == "200":

                        for item in (
                            forecast_data["list"][:5]
                        ):

                            dt = datetime.strptime(
                                item["dt_txt"],
                                "%Y-%m-%d %H:%M:%S"
                            )

                            forecast.append({
                                "temp":
                                    round(
                                        item["main"][
                                            "temp"
                                        ]
                                    ),
                                "icon":
                                    item["weather"][0][
                                        "icon"
                                    ],
                                "day":
                                    dt.strftime(
                                        "%a"
                                    ),
                                "time":
                                    dt.strftime(
                                        "%I:%M %p"
                                    )
                            })

                    # Refresh recent searches
                    cur.execute("""
                        SELECT city
                        FROM searches
                        GROUP BY city
                        ORDER BY id DESC
                        LIMIT 5
                    """)

                    recent = [
                        row[0]
                        for row in cur.fetchall()
                    ]

                else:
                    error = (
                        "❌ City not found."
                    )

            except requests.exceptions.Timeout:
                error = (
                    "❌ Request timed out."
                )

            except requests.exceptions.ConnectionError:
                error = (
                    "❌ No internet connection."
                )

            except Exception:
                error = (
                    "❌ Something went wrong."
                )

    return render_template(
        "index.html",
        weather=weather,
        forecast=forecast,
        recent=recent,
        error=error
    )


@app.errorhandler(404)
def not_found(error):
    return render_template(
        "404.html"
    ), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template(
        "500.html"
    ), 500


if __name__ == "__main__":
    app.run(debug=True)
