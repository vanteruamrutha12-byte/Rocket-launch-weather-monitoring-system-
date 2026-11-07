"""Unit tests for safety_rules.py"""

import os
import sys
import unittest

# Let the tests find safety_rules.py in the project's main folder
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from safety_rules import Thresholds, evaluate


class TestEvaluate(unittest.TestCase):

    def test_safe_normal_conditions(self):
        status, reasons = evaluate(25, 60, 10)
        self.assertEqual(status, "SAFE")
        self.assertEqual(reasons, [])

    def test_unsafe_high_wind(self):
        status, reasons = evaluate(25, 60, 50)
        self.assertEqual(status, "UNSAFE")
        self.assertEqual(len(reasons), 1)

    def test_unsafe_high_temperature(self):
        status, _ = evaluate(45, 60, 10)
        self.assertEqual(status, "UNSAFE")

    def test_unsafe_low_temperature(self):
        status, _ = evaluate(-5, 60, 10)
        self.assertEqual(status, "UNSAFE")

    def test_unsafe_high_humidity(self):
        status, _ = evaluate(25, 95, 10)
        self.assertEqual(status, "UNSAFE")

    def test_multiple_reasons(self):
        status, reasons = evaluate(45, 90, 40)
        self.assertEqual(status, "UNSAFE")
        self.assertEqual(len(reasons), 3)

    def test_values_exactly_at_limits_are_safe(self):
        status, _ = evaluate(40.0, 85.0, 30.0)
        self.assertEqual(status, "SAFE")

    def test_custom_thresholds(self):
        strict = Thresholds(max_wind_speed=5.0)
        status, _ = evaluate(25, 60, 10, strict)
        self.assertEqual(status, "UNSAFE")


class TestValidation(unittest.TestCase):

    def test_humidity_out_of_range_raises(self):
        with self.assertRaises(ValueError):
            evaluate(25, 150, 10)

    def test_negative_wind_raises(self):
        with self.assertRaises(ValueError):
            evaluate(25, 60, -1)

    def test_text_value_raises(self):
        with self.assertRaises(ValueError):
            evaluate("hot", 60, 10)

    def test_boolean_value_raises(self):
        with self.assertRaises(ValueError):
            evaluate(True, 60, 10)


if __name__ == "__main__":
    unittest.main()
