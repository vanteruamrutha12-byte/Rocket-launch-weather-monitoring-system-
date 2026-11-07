"""data_sources.py

Gets weather readings from different sources.
Every source returns a dictionary with the same keys:
    source, temperature, humidity, wind_speed
"""

import logger

SAMPLE_FILE = "data/sample_weather.csv"


def get_sample_reading(filepath=SAMPLE_FILE, index=-1):
    """Return one reading from the sample CSV file.

    index=-1 means the latest row. Raises ValueError if the file is
    missing or empty.
    """
    rows = logger.read_history(filepath)
    if not rows:
        raise ValueError("Sample data file is missing or empty")

    try:
        row = rows[index]
    except IndexError:
        raise ValueError(f"No sample row at position {index}")

    return {
        "source": "sample",
        "temperature": row["temperature"],
        "humidity": row["humidity"],
        "wind_speed": row["wind_speed"],
    }


import json
import urllib.error
import urllib.parse
import urllib.request

API_URL = "https://api.open-meteo.com/v1/forecast"


def get_live_reading(latitude=13.72, longitude=80.23, timeout=10):
    """Fetch current weather from the Open-Meteo API.

    Returns the common reading dictionary. Raises ValueError with a
    readable message if the internet or the API fails.
    """
    params = urllib.parse.urlencode({
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
        "wind_speed_unit": "kmh",
    })

    try:
        with urllib.request.urlopen(f"{API_URL}?{params}", timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
        current = data["current"]
        return {
            "source": "live_api",
            "temperature": float(current["temperature_2m"]),
            "humidity": float(current["relative_humidity_2m"]),
            "wind_speed": float(current["wind_speed_10m"]),
        }
    except urllib.error.URLError as error:
        raise ValueError(f"Could not reach the weather API: {error}")
    except (KeyError, TypeError, json.JSONDecodeError):
        raise ValueError("Weather API returned unexpected data")
