"""safety_rules.py

Demonstration rules for the Rocket Launch Weather Monitoring system.

IMPORTANT: SAFE and UNSAFE here only mean "the readings satisfy the example
thresholds set by the user". They are NOT certified launch-safety limits.
"""

from dataclasses import dataclass


@dataclass
class Thresholds:
    """Example limits that the user can change."""
    max_wind_speed: float = 30.0    # km/h
    max_temperature: float = 40.0   # degrees C
    min_temperature: float = 0.0    # degrees C
    max_humidity: float = 85.0      # percent


def validate_reading(temperature, humidity, wind_speed):
    """Check that the readings are valid numbers in a sensible range.

    Raises ValueError if something is wrong.
    """
    for name, value in (("temperature", temperature),
                        ("humidity", humidity),
                        ("wind_speed", wind_speed)):
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError(f"{name} must be a number")

    if not 0 <= humidity <= 100:
        raise ValueError("humidity must be between 0 and 100")
    if wind_speed < 0:
        raise ValueError("wind_speed cannot be negative")


def evaluate(temperature, humidity, wind_speed, thresholds=None):
    """Compare readings with the thresholds.

    Returns a tuple: (status, reasons)
      status  -> "SAFE" or "UNSAFE" (demonstration only)
      reasons -> list of text messages explaining each failed rule
    """
    if thresholds is None:
        thresholds = Thresholds()

    validate_reading(temperature, humidity, wind_speed)

    reasons = []

    if wind_speed > thresholds.max_wind_speed:
        reasons.append(
            f"Wind speed {wind_speed} km/h is above {thresholds.max_wind_speed} km/h")
    if temperature > thresholds.max_temperature:
        reasons.append(
            f"Temperature {temperature} C is above {thresholds.max_temperature} C")
    if temperature < thresholds.min_temperature:
        reasons.append(
            f"Temperature {temperature} C is below {thresholds.min_temperature} C")
    if humidity > thresholds.max_humidity:
        reasons.append(
            f"Humidity {humidity}% is above {thresholds.max_humidity}%")

    status = "UNSAFE" if reasons else "SAFE"
    return status, reasons
