import json
import unittest

from backend.channel_model import predict_channel


class ChannelModelTests(unittest.TestCase):
    def test_predict_channel_returns_core_metrics(self):
        result = predict_channel(
            {
                "airTemp": 26.5,
                "seaTemp": 28.0,
                "rh": 75,
                "windSpeed": 5,
                "pressure": 1013.25,
                "frequency": 2600,
                "txHeight": 25,
                "rxHeight": 3,
                "basePosition": {"x": -210.5, "y": 1.35, "z": -58},
                "boatPosition": {"x": 25, "y": 1.2, "z": 20},
                "ductHeight": 35,
            }
        )
        self.assertGreater(result["distanceM"], 200)
        self.assertGreater(result["pathLossDb"], 0)
        self.assertGreater(result["delayUs"], 0)
        self.assertGreaterEqual(result["inferenceMs"], 0)

    def test_predict_channel_accepts_missing_payload_fields(self):
        result = predict_channel({})
        self.assertIn("pathLossDb", result)
        self.assertIn("ductHeightM", result)


class JsonShapeTests(unittest.TestCase):
    def test_payload_is_json_serializable(self):
        result = predict_channel({})
        encoded = json.dumps(result)
        self.assertIsInstance(encoded, str)


if __name__ == "__main__":
    unittest.main()
