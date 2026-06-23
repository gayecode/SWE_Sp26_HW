import unittest
from app import create_app
from app.main.utils import build_query, parse_response, parse_satellite
import datetime


class MockResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self.json_data = json_data

    def json(self):
        return self.json_data


class UtilsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_build_query(self):
        satellite_id = "000000"
        query, headers = build_query(satellite_id)

        self.assertEqual(query, "https://tle.ivanstanojevic.me/api/tle/000000")
        self.assertIn("User-Agent", headers)

    def test_parse_response_success(self):
        response = MockResponse(200, {
            "name": "ISS (ZARYA)",
            "line1": "1 25544U 98067A   26158.90128687  .00007994  00000+0  14961-3 0  9995",
            "line2": "2 25544  51.6338 346.0598 0006926 145.2709 214.8733 15.49660544570312",
            "date": "2026-06-07T21:37:51+00:00"
        })

        result = parse_response(response)

        self.assertEqual(result["name"], "ISS (ZARYA)")
        self.assertEqual(result["tle_date_time"], "2026-06-07T21:37:51+00:00")
        self.assertIn("line1", result)
        self.assertIn("line2", result)

    def test_parse_response_failure(self):
        response = MockResponse(404, {
            "response": {
                "message": "Unable to find record"
            }
        })

        result = parse_response(response)

        self.assertIsNone(result)

    def test_parse_satellite_success(self):
        tle_dict = {
            "name": "ISS (ZARYA)",
            "line1": "1 25544U 98067A   26158.90128687  .00007994  00000+0  14961-3 0  9995",
            "line2": "2 25544  51.6338 346.0598 0006926 145.2709 214.8733 15.49660544570312",
            "tle_date_time": "2026-06-07T21:37:51+00:00"
        }

        input_date_time = datetime.datetime(2026, 6, 1, 12, 0)
        error, r, v = parse_satellite(tle_dict, input_date_time)

        self.assertEqual(error, 0)
        self.assertEqual(len(r), 3)
        self.assertEqual(len(v), 3)