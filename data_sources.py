"""data_sources.py

Gets weather readings from different sources.
Every source returns a dictionary with the same keys:
    source, temperature, humidity, wind_speed
"""

import logger

SAMPLE_FILE = "data/sample_weather.csv"


_sample_position = {"next": 0}


def get_next_sample_reading(filepath=SAMPLE_FILE):
    """Return the next sample row each time it is called.

    After the last row it starts again from the first row, like a
    replayed recording. Raises ValueError if the file is missing or empty.
    """
    rows = logger.read_history(filepath)
    if not rows:
        raise ValueError("Sample data file is missing or empty")

    position = _sample_position["next"] % len(rows)
    _sample_position["next"] = position + 1
    return get_sample_reading(filepath, index=position)


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


import random

# Remembers the last simulated values, so each new reading drifts
# slowly from the previous one (same idea as the Wokwi sketch).
_esp32_state = {"temperature": 27.0, "humidity": 60.0, "wind_speed": 10.0}


def _limit(value, minimum, maximum):
    """Keep a value between a minimum and a maximum."""
    return max(minimum, min(maximum, value))


def get_esp32_simulated_reading():
    """Return one simulated ESP32 reading in the common format."""
    s = _esp32_state
    s["temperature"] = _limit(s["temperature"] + random.uniform(-0.5, 0.5), 15.0, 45.0)
    s["humidity"] = _limit(s["humidity"] + random.uniform(-2.0, 2.0), 20.0, 100.0)
    s["wind_speed"] = _limit(s["wind_speed"] + random.uniform(-3.0, 3.0), 0.0, 60.0)
    return {
        "source": "esp32_simulated",
        "temperature": round(s["temperature"], 1),
        "humidity": round(s["humidity"], 1),
        "wind_speed": round(s["wind_speed"], 1),
    }
