import os
import requests
import datetime

from dotenv.main import load_dotenv
from flask import redirect, render_template, session
from functools import wraps

load_dotenv()


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def lookup(city):
    """Look up quote for symbol."""
    # Contact API
    try:
        load_dotenv()
        api_key = os.environ["API_KEY"]
        url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={city}&days=2&aqi=yes&alerts=yes"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        return quote
    
    except (KeyError, TypeError, ValueError):
        return None

def weather(city):
    """Look up quote for symbol."""
    quote = lookup(city)

    # Parse response
    try:
        main = quote["current"]
        place = quote["location"]["name"]
        temp = main["temp_c"]
        humidity = main["humidity"]
        windspeed = main["wind_kph"]
        desc = main["condition"]["text"]
        icon = main["condition"]["icon"]
        pressure = main["pressure_mb"]
        preci = main["precip_mm"]
        weather = {
            "name": place,
            "temp": temp,
            "humidity": humidity,
            "windspeed": windspeed,
            "desc": desc,
            "icon" : icon,
            "pressure": pressure,
            "preci": preci
        }
        now = datetime.datetime.now()
        current_hour = now.hour

        # Convert the current hour to a Unix timestamp
        current_timestamp = int(datetime.datetime.timestamp(datetime.datetime(now.year, now.month, now.day, current_hour, 0, 0)))
        forecast = quote["forecast"]["forecastday"][0]["hour"]
        hours =[]
        k = 0
        for i in range(len(forecast)):
            if forecast[i]["time_epoch"] == current_timestamp:
                if i == 23:
                    k = 1
                elif i >= 18 and i < 23:
                    k = 23 - i
                else:
                    k = 6
                for j in range(i,i+k):
                    timestamp = forecast[j]["time_epoch"] 

                    # Convert Unix timestamp to a datetime object
                    dt_object = datetime.datetime.fromtimestamp(timestamp)

                    # Extract hours and minutes from datetime object
                    hours_c = dt_object.hour
                    time = str(hours_c) +" : 00"
                    hour = {
                        "time": time,
                        "icon": forecast[j]["condition"]["icon"],
                        "text": forecast[j]["condition"]["text"],
                        "temp": forecast[j]["temp_c"],
                        "precip": forecast[j]["chance_of_rain"]
                    }
                    hours.append(hour)
                break
        forecast = quote["forecast"]["forecastday"][1]["hour"]
        if k < 6:
            for j in range(6-k):
                timestamp = forecast[j]["time_epoch"] 

                # Convert Unix timestamp to a datetime object
                dt_object = datetime.datetime.fromtimestamp(timestamp)

                # Extract hours and minutes from datetime object
                hours_c = dt_object.hour
                time = str(hours_c) +" : 00"
                hour = {
                        "time": time,
                        "icon": forecast[j]["condition"]["icon"],
                        "text": forecast[j]["condition"]["text"],
                        "temp": forecast[j]["temp_c"],
                        "precip": forecast[j]["chance_of_rain"]
                    }
                hours.append(hour)
        forecast = quote["forecast"]["forecastday"][1]["day"]
        max_temp = forecast["maxtemp_c"]
        min_temp = forecast["mintemp_c"]
        max_wind = forecast["maxwind_kph"]
        avg_humidity = forecast["avghumidity"]
        precip_chance = forecast["daily_chance_of_rain"]
        icon_mail = forecast["condition"]["icon"]
        text_mail = forecast["condition"]["text"]
        mail = {
            "icon": icon_mail,
            "desc": text_mail,
            "max_temp": max_temp,
            "min_temp": min_temp,
            "max_wind": max_wind,
            "avg_humidity": avg_humidity,
            "precip_chance": precip_chance
        }
        return [weather, hours, mail]
    except (KeyError, TypeError, ValueError):
        return None

def usd(value):
    """Format value as USD."""
    return f"{value:,.2f}"
