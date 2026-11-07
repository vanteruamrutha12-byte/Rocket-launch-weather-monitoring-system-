"""Unit tests for main.py"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logger
import main


class TestRun(unittest.TestCase):

    def test_unknown_source_raises(self):
        with self.assertRaises(ValueError):
            main.run("banana")

    def test_run_logs_one_row_and_returns_status(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "log.csv")
            result = main.run("esp32", log_file=path)
            self.assertIn(result["status"], ("SAFE", "UNSAFE"))
            self.assertEqual(len(logger.read_history(path)), 1)


if __name__ == "__main__":
    unittest.main()
