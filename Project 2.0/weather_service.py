
import requests
from sqlalchemy.orm import Session
from models import WeatherLog

def get_weather_openmeteo(city: str):
    """
    Fetches weather data from Open-Meteo API (Free, No Key).
    """
    try:
        # 1. Geocoding
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_res = requests.get(geo_url, timeout=5)
        geo_data = geo_res.json()

        if not geo_data.get("results"):
            raise ValueError(f"City '{city}' not found.")

        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]

        # 2. Weather
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        weather_res = requests.get(weather_url, timeout=5)
        weather_data = weather_res.json()
        
        current = weather_data.get("current_weather", {})
        temp = current.get("temperature")
        code = current.get("weathercode")
        
        # Code mapping
        condition = "Unknown"
        if code == 0: condition = "Clear sky"
        elif code in [1, 2, 3]: condition = "Partly cloudy"
        elif code in [45, 48]: condition = "Fog"
        elif code in [51, 53, 55]: condition = "Drizzle"
        elif code in [61, 63, 65]: condition = "Rain"
        elif code in [71, 73, 75]: condition = "Snow"
        elif code in [95, 96, 99]: condition = "Thunderstorm"
        
        return {
            "temperature": f"{temp}°C",
            "condition": condition,
            "source": "Open-Meteo"
        }
    except Exception as e:
        raise e

def get_weather_openweathermap(city: str, api_key: str):
    """
    Fetches weather data from OpenWeatherMap API (Requires Key).
    """
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        res = requests.get(url, timeout=5)
        
        if res.status_code == 401:
            raise ValueError("Invalid API Key.")
        if res.status_code == 404:
            raise ValueError(f"City '{city}' not found.")
            
        data = res.json()
        temp = data["main"]["temp"]
        condition = data["weather"][0]["description"].capitalize()
        
        return {
            "temperature": f"{temp}°C",
            "condition": condition,
            "source": "OpenWeatherMap"
        }
    except requests.exceptions.Timeout:
        raise TimeoutError("OpenWeatherMap API timed out.")
    except Exception as e:
        raise e

def get_weather(city: str, api_key: str = None):
    """
    Facade to switch between providers.
    """
    if api_key:
        return get_weather_openweathermap(city, api_key)
    else:
        return get_weather_openmeteo(city)

def log_weather(db: Session, city: str, temperature: str, condition: str):
    """Logs the weather inquiry to the database."""
    log = WeatherLog(city=city, temperature=temperature, condition=condition)
    db.add(log)
    db.commit()
    return log

def delete_weather_log(db: Session, log_id: int):
    """Deletes a weather log by ID."""
    try:
        log = db.query(WeatherLog).filter(WeatherLog.id == log_id).first()
        if not log:
            return False, (404, "Log not found")
        db.delete(log)
        db.commit()
        return True, (200, "Log deleted")
    except Exception as e:
        return False, (500, f"Database Error: {str(e)}")
