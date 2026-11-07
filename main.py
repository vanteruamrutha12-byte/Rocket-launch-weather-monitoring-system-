"""main.py

Command-line runner for the Rocket Launch Weather Monitoring demo.

Usage:
    python3 main.py sample
    python3 main.py live
    python3 main.py esp32

NOTE: SAFE / UNSAFE only means the readings satisfy example thresholds.
It is NOT real launch guidance.
"""

import sys

import data_sources
import logger
import safety_rules

LOG_FILE = "data/weather_log.csv"

SOURCES = {
    "sample": data_sources.get_next_sample_reading,
    "live": data_sources.get_live_reading,
    "esp32": data_sources.get_esp32_simulated_reading,
}


def run(source_name, thresholds=None, log_file=LOG_FILE):
    """Get one reading, evaluate it, log it and return the result.

    Raises ValueError if the source name is unknown or the data is bad.
    """
    if source_name not in SOURCES:
        raise ValueError(
            f"Unknown source '{source_name}'. Choose from: {', '.join(SOURCES)}")

    reading = SOURCES[source_name]()
    status, reasons = safety_rules.evaluate(
        reading["temperature"], reading["humidity"],
        reading["wind_speed"], thresholds)

    logger.log_reading(
        log_file, reading["source"], reading["temperature"],
        reading["humidity"], reading["wind_speed"], status)

    return {"reading": reading, "status": status, "reasons": reasons}


def main():
    source_name = sys.argv[1] if len(sys.argv) > 1 else "sample"
    try:
        result = run(source_name)
    except ValueError as error:
        print(f"Error: {error}")
        return 1

    r = result["reading"]
    print(f"Source      : {r['source']}")
    print(f"Temperature : {r['temperature']} C")
    print(f"Humidity    : {r['humidity']} %")
    print(f"Wind speed  : {r['wind_speed']} km/h")
    print(f"Status      : {result['status']} (demonstration only)")
    for reason in result["reasons"]:
        print(f"  - {reason}")
    print(f"Logged to   : {LOG_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
