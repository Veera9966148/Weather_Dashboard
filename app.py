#from flask import (
#    Flask,
#    render_template,
#    request,
#    redirect,
#    url_for
#)

#from config import Config
#from database import (
#    get_db,
#    init_db
#)

#from datetime import datetime
#import requests

#app = Flask(__name__)
#app.config.from_object(Config)

#init_db()


#def get_weather(city):

#    weather_url = (
#        "https://api.openweathermap.org/data/2.5/weather"
#        f"?q={city}"
#        f"&appid={app.config['API_KEY']}"
#        "&units=metric"
#    )

#    response = requests.get(
#        weather_url,
#        timeout=10
#    )

#    response.raise_for_status()

#    data = response.json()

#    if str(data["cod"]) != "200":
#        return None

#    weather = {
#        "city": data["name"],
#        "country": data["sys"]["country"],
#        "temp": round(data["main"]["temp"]),
#        "feels": round(
#            data["main"]["feels_like"]
#        ),
#        "humidity":
#            data["main"]["humidity"],
#        "pressure":
#            data["main"]["pressure"],
#        "wind":
#            data["wind"]["speed"],
#        "description":
#            data["weather"][0]["description"],
#        "icon":
#            data["weather"][0]["icon"],
#        "main":
#            data["weather"][0]["main"],
#        "sunrise":
#            datetime.fromtimestamp(
#                data["sys"]["sunrise"]
#            ).strftime("%I:%M %p"),
#        "sunset":
#            datetime.fromtimestamp(
#                data["sys"]["sunset"]
#            ).strftime("%I:%M %p")
#    }

#    return weather


#@app.route("/", methods=["GET", "POST"])
#def home():

#    weather = None
#    error = None

#    conn = get_db()
#    cursor = conn.cursor()

#    if request.method == "POST":

#        city = request.form.get(
#            "city",
#            ""
#        ).strip()

#        if not city:
#            error = "Please enter a city."

#        else:

#            try:

#                weather = get_weather(city)

#                if weather:

#                    cursor.execute(
#                        """
#                        INSERT INTO history(city)
#                        VALUES(?)
#                        """,
#                        (weather["city"],)
#                    )

#                    conn.commit()

#                else:
#                    error = "City not found."

#            except requests.exceptions.ConnectionError:
#                error = (
#                    "Internet connection error."
#                )

#            except requests.exceptions.Timeout:
#                error = (
#                    "Request timed out."
#                )

#            except Exception:
#                error = (
#                    "Something went wrong."
#                )

#    cursor.execute("""
#    SELECT city
#    FROM history
#    ORDER BY id DESC
#    LIMIT 5
#    """)

#    history = cursor.fetchall()

#    cursor.execute("""
#    SELECT city
#    FROM favorites
#    """)

#    favorites = cursor.fetchall()

#    conn.close()

#    return render_template(
#        "index.html",
#        weather=weather,
#        history=history,
#        favorites=favorites,
#        error=error
#    )


#@app.route("/favorite/<city>")
#def favorite(city):

#    conn = get_db()
#    cursor = conn.cursor()

#    cursor.execute(
#        """
#        INSERT INTO favorites(city)
#        VALUES(?)
#        """,
#        (city,)
#    )

#    conn.commit()
#    conn.close()

#    return redirect(url_for("home"))


#if __name__ == "__main__":
#    app.run(debug=True)
from flask import Flask, render_template, request
from dotenv import load_dotenv
import requests
import sqlite3
import os
from datetime import datetime

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("API_KEY")

DB_NAME = "weather.db"


# --------------------------
# Database
# --------------------------

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT UNIQUE
        )
    """)

    conn.commit()
    conn.close()


init_db()


# --------------------------
# Home Route
# --------------------------

@app.route("/", methods=["GET", "POST"])
def home():

    weather = None
    forecast = []
    error = None

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    history = cur.execute(
        "SELECT city FROM history ORDER BY id DESC LIMIT 5"
    ).fetchall()

    if request.method == "POST":

        city = request.form.get("city", "").strip()

        if city == "":
            error = "Please enter a city name."

        else:

            try:

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
                            data["weather"][0]["description"],
                        "icon":
                            data["weather"][0]["icon"]
                    }

                    sunrise = datetime.fromtimestamp(
                        data["sys"]["sunrise"]
                    )

                    sunset = datetime.fromtimestamp(
                        data["sys"]["sunset"]
                    )

                    weather["sunrise"] = sunrise.strftime(
                        "%I:%M %p"
                    )

                    weather["sunset"] = sunset.strftime(
                        "%I:%M %p"
                    )

                    cur.execute(
                        """
                        INSERT OR IGNORE
                        INTO history(city)
                        VALUES(?)
                        """,
                        (city.title(),)
                    )

                    conn.commit()

                    forecast_url = (
                        f"https://api.openweathermap.org/data/2.5/forecast"
                        f"?q={city}"
                        f"&appid={API_KEY}"
                        f"&units=metric"
                    )

                    f_response = requests.get(
                        forecast_url,
                        timeout=10
                    )

                    f_data = f_response.json()

                    if str(f_data.get("cod")) == "200":

                        for item in f_data["list"][:5]:

                            forecast.append(
                                {
                                    "temp":
                                    round(
                                        item["main"]["temp"]
                                    ),

                                    "time":
                                    item["dt_txt"],

                                    "icon":
                                    item["weather"][0]["icon"]
                                }
                            )

                else:
                    error = "City not found."

            except requests.exceptions.Timeout:
                error = "Request timed out."

            except requests.exceptions.ConnectionError:
                error = "No internet connection."

            except Exception:
                error = "Something went wrong."

    history = cur.execute(
        "SELECT city FROM history ORDER BY id DESC LIMIT 5"
    ).fetchall()

    conn.close()

    return render_template(
        "index.html",
        weather=weather,
        forecast=forecast,
        history=history,
        error=error
    )


if __name__ == "__main__":
    app.run(debug=True)