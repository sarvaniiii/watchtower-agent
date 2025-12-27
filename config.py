import os
from dotenv import load_dotenv

load_dotenv()

# API Keys (you can get free keys from these services)
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "your_key_here")  # From https://www.weatherapi.com/
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "your_key_here")  # From https://openweathermap.org/api

# Disaster thresholds
THRESHOLDS = {
    "wind_speed": 80,  # km/h - High risk threshold
    "precipitation": 50,  # mm - Heavy rain
    "earthquake": 6.0,  # magnitude
    "temperature": 40,  # °C - Heat wave
}

# Mock locations for demo
MOCK_LOCATIONS = [
    "Miami, Florida",
    "Los Angeles, California",
    "Tokyo, Japan",
    "Manila, Philippines",
    "Sydney, Australia"
]

# Mock disaster types
MOCK_DISASTERS = [
    "hurricane",
    "earthquake",
    "flood",
    "wildfire",
    "tsunami"
]