"""Unit tests for logger.py"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logger


class TestLogger(unittest.TestCase):

    def test_header_written_only_once(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "log.csv")
            logger.log_reading(path, "sample", 25.0, 60.0, 10.0, "SAFE")
            logger.log_reading(path, "sample", 26.0, 61.0, 11.0, "SAFE")
            with open(path, encoding="utf-8") as f:
                lines = f.read().strip().splitlines()
            self.assertEqual(len(lines), 3)  # 1 header + 2 rows
            self.assertTrue(lines[0].startswith("timestamp"))

    def test_history_values_are_numbers(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "log.csv")
            logger.log_reading(path, "esp32_simulated", 25.5, 60.0, 10.0, "SAFE")
            rows = logger.read_history(path)
            self.assertEqual(len(rows), 1)
            self.assertIsInstance(rows[0]["temperature"], float)
            self.assertEqual(rows[0]["temperature"], 25.5)
            self.assertEqual(rows[0]["source"], "esp32_simulated")

    def test_missing_file_gives_empty_list(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "does_not_exist.csv")
            self.assertEqual(logger.read_history(path), [])


if __name__ == "__main__":
    unittest.main()
