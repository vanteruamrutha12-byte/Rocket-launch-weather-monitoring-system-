# System Architecture

Educational prototype. SAFE / UNSAFE only means the readings satisfy
example thresholds chosen by the user. It is not real launch guidance.

## Overview

The system gets weather readings from one of three sources, checks them
against configurable demonstration thresholds, logs every reading to a CSV
file, and shows everything on a Streamlit dashboard.

## Modules

| File | Role |
|------|------|
| `data_sources.py` | Provides readings from the sample CSV, the Open-Meteo API, or the simulated ESP32 |
| `safety_rules.py` | Validates readings and compares them with thresholds (SAFE / UNSAFE plus reasons) |
| `logger.py` | Appends readings to a CSV file and reads the history back |
| `main.py` | Command-line runner that ties source, rules and logger together (`run()` function) |
| `dashboard.py` | Streamlit web dashboard that reuses `main.run()` |
| `wokwi/sketch.ino` | ESP32 program that generates simulated readings in Wokwi |
| `wokwi/diagram.json` | Virtual circuit description for the Wokwi simulation |
| `tests/` | Unit tests for every Python module except the live API call |

## Common reading format

Every data source returns a dictionary with the same keys:

    source, temperature (C), humidity (%), wind_speed (km/h)

Because the format is identical, the rest of the system does not care where
a reading came from. Adding a new source means adding one function and one
entry in the `SOURCES` dictionary in `main.py`.

## Data flow

1. The user picks a source and thresholds in the dashboard (or a source name on the command line).
2. `main.run()` calls the chosen source function.
3. `safety_rules.evaluate()` validates the numbers and returns a status and a list of reasons.
4. `logger.log_reading()` appends the reading, status and an India-time timestamp to `data/weather_log.csv`.
5. The dashboard shows the reading, the status banner, the history table and the charts.

## ESP32 simulation

The Wokwi sketch shows how an ESP32 generates simulated readings: a small
random drift from the previous value, limited to realistic ranges, printed
over the serial port every 2 seconds. The Python function
`get_esp32_simulated_reading()` reproduces the same logic, so the dashboard
can use it without physical hardware or a live serial connection. The
dashboard labels this source "ESP32 (simulated)".

## Design decisions

- **Standard library first:** the logger, API client and tests use only built-in Python modules.
- **Clear errors:** invalid input and network failures raise `ValueError` with readable messages, and the dashboard shows them instead of crashing.
- **No credentials:** Open-Meteo needs no API key.
- **Time zone:** timestamps use India Standard Time (UTC+05:30).
