"""Unit tests for data_sources.py (sample and simulated ESP32 sources)"""

import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import data_sources

SAMPLE = os.path.join(ROOT, "data", "sample_weather.csv")


class TestSampleSource(unittest.TestCase):

    def test_first_row(self):
        reading = data_sources.get_sample_reading(SAMPLE, index=0)
        self.assertEqual(reading["source"], "sample")
        self.assertEqual(reading["temperature"], 24.5)

    def test_latest_row(self):
        reading = data_sources.get_sample_reading(SAMPLE)
        self.assertEqual(reading["temperature"], 28.7)

    def test_bad_index_raises(self):
        with self.assertRaises(ValueError):
            data_sources.get_sample_reading(SAMPLE, index=999)

    def test_empty_file_raises(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "empty.csv")
            open(path, "w").close()
            with self.assertRaises(ValueError):
                data_sources.get_sample_reading(path)

    def test_next_sample_loops_back(self):
        data_sources._sample_position["next"] = 0
        readings = [data_sources.get_next_sample_reading(SAMPLE) for _ in range(9)]
        self.assertEqual(readings[0]["temperature"], 24.5)
        self.assertEqual(readings[7]["temperature"], 28.7)
        self.assertEqual(readings[8]["temperature"], 24.5)  # started again


class TestEsp32Simulation(unittest.TestCase):

    def test_format_and_limits(self):
        for _ in range(200):
            reading = data_sources.get_esp32_simulated_reading()
            self.assertEqual(reading["source"], "esp32_simulated")
            self.assertTrue(15.0 <= reading["temperature"] <= 45.0)
            self.assertTrue(20.0 <= reading["humidity"] <= 100.0)
            self.assertTrue(0.0 <= reading["wind_speed"] <= 60.0)


if __name__ == "__main__":
    unittest.main()
