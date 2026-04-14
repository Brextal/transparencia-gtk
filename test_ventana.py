import unittest
import json
import os
import sys
import tempfile

SLIDER_MIN = 0.3
SLIDER_MAX = 1.0
SLIDER_STEP = 0.05


def format_alpha_value(alpha):
    return "1.0" if alpha is None else str(alpha)


class TestFormatAlphaValue(unittest.TestCase):
    def test_none_returns_1_0(self):
        result = format_alpha_value(None)
        self.assertEqual(result, "1.0")

    def test_float_returns_string(self):
        result = format_alpha_value(0.7)
        self.assertEqual(result, "0.7")

    def test_int_returns_string(self):
        result = format_alpha_value(1)
        self.assertEqual(result, "1")


class TestSliderConstants(unittest.TestCase):
    def test_slider_min(self):
        self.assertEqual(SLIDER_MIN, 0.3)

    def test_slider_max(self):
        self.assertEqual(SLIDER_MAX, 1.0)


class TestAlphaValidation(unittest.TestCase):
    def test_valid_alpha_0_3(self):
        value = 0.3
        self.assertTrue(value is not None and isinstance(value, (int, float)) and SLIDER_MIN <= value <= SLIDER_MAX)

    def test_valid_alpha_1_0(self):
        value = 1.0
        self.assertTrue(value is not None and isinstance(value, (int, float)) and SLIDER_MIN <= value <= SLIDER_MAX)

    def test_valid_alpha_0_7(self):
        value = 0.7
        self.assertTrue(value is not None and isinstance(value, (int, float)) and SLIDER_MIN <= value <= SLIDER_MAX)

    def test_invalid_alpha_too_low(self):
        value = 0.1
        self.assertFalse(SLIDER_MIN <= value <= SLIDER_MAX)

    def test_invalid_alpha_too_high(self):
        value = 1.5
        self.assertFalse(SLIDER_MIN <= value <= SLIDER_MAX)

    def test_invalid_alpha_negative(self):
        value = -0.5
        self.assertFalse(SLIDER_MIN <= value <= SLIDER_MAX)

    def test_invalid_string(self):
        value = "0.7"
        self.assertFalse(isinstance(value, (int, float)))

    def test_invalid_none(self):
        value = None
        self.assertFalse(value is not None and isinstance(value, (int, float)) and SLIDER_MIN <= value <= SLIDER_MAX)


class TestConfigHandling(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_config_file = os.path.join(self.temp_dir, "test_config.json")

    def tearDown(self):
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_config_with_valid_values(self):
        test_data = {
            "kitty": 0.7,
            "brave-browser": 0.5
        }
        with open(self.test_config_file, "w") as f:
            json.dump(test_data, f)

        with open(self.test_config_file, "r") as f:
            data = json.load(f)
            for app_class, value in data.items():
                if value is not None and isinstance(value, (int, float)) and SLIDER_MIN <= float(value) <= SLIDER_MAX:
                    data[app_class] = float(value)
                else:
                    data[app_class] = None

        self.assertEqual(data["kitty"], 0.7)
        self.assertEqual(data["brave-browser"], 0.5)

    def test_config_with_invalid_values(self):
        test_data = {
            "kitty": 999,
            "brave-browser": "invalid"
        }
        with open(self.test_config_file, "w") as f:
            json.dump(test_data, f)

        with open(self.test_config_file, "r") as f:
            data = json.load(f)
            for app_class, value in data.items():
                if value is not None and isinstance(value, (int, float)) and SLIDER_MIN <= float(value) <= SLIDER_MAX:
                    data[app_class] = float(value)
                else:
                    data[app_class] = None

        self.assertIsNone(data["kitty"])
        self.assertIsNone(data["brave-browser"])


if __name__ == "__main__":
    unittest.main()