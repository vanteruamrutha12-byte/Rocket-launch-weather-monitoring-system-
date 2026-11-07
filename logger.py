"""logger.py

Saves weather readings to a CSV file and reads them back.
"""

import csv
import os
from datetime import datetime, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30))  # India time

FIELDNAMES = ["timestamp", "source", "temperature",
              "humidity", "wind_speed", "status"]


def log_reading(filepath, source, temperature, humidity, wind_speed, status):
    """Add one reading as a new row at the end of the CSV file.

    The header row is written only if the file is new or empty.
    """
    folder = os.path.dirname(filepath)
    if folder:
        os.makedirs(folder, exist_ok=True)

    needs_header = not os.path.exists(filepath) or os.path.getsize(filepath) == 0

    with open(filepath, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if needs_header:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S"),
            "source": source,
            "temperature": temperature,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "status": status,
        })


def read_history(filepath):
    """Read all rows from a CSV file and return them as a list of dictionaries.

    Returns an empty list if the file does not exist.
    Temperature, humidity and wind speed are converted to numbers.
    """
    if not os.path.exists(filepath):
        return []

    rows = []
    with open(filepath, "r", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for key in ("temperature", "humidity", "wind_speed"):
                row[key] = float(row[key])
            rows.append(row)
    return rows
