import unittest
from app import create_app
from unittest import mock
import datetime


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, status_code, json_data):
            self.status_code = status_code
            self.json_data = json_data

        def json(self):
            return self.json_data

    if args[0] == "https://tle.ivanstanojevic.me/api/tle/25544":
        tmp_response = {
            "@context": "https:\\/\\/www.w3.org\\/ns\\/hydra\\/context.jsonld",
            "@id": "https:\\/\\/tle.ivanstanojevic.me\\/api\\/tle\\/25544",
            "@type": "Tle",
            "satelliteId": 25544,
            "name": "ISS (ZARYA)",
            "date": "2026-06-07T21:37:51+00:00",
            "line1": "1 25544U 98067A   26158.90128687  .00007994  00000+0  14961-3 0  9995",
            "line2": "2 25544  51.6338 346.0598 0006926 145.2709 214.8733 15.49660544570312"
        }
        return MockResponse(200, tmp_response)

    return MockResponse(404, None)


class MainTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        self.app_context.pop()

    def test_index_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Software Engineering", response.get_data(as_text=True))

    def test_calculate_get_page(self):
        response = self.client.get('/calculate')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Calculate", response.get_data(as_text=True))

    @mock.patch('app.main.views.requests.get', side_effect=mocked_requests_get)
    def test_calculate_success(self, mock_get):
        response = self.client.post('/calculate', data={
            'input_date_time': datetime.datetime(2026, 6, 1, 12, 0)
        })

        page = response.get_data(as_text=True)
        self.assertIn("Satellite/space object position and velocity calculated", page)
        self.assertIn("TLE DateTime:", page)
        self.assertIn("Position (X, Y, Z) in km:", page)
        self.assertIn("Velocity (dx, dy, dz) in km/s:", page)

    @mock.patch('app.main.views.parse_satellite')
    @mock.patch('app.main.views.requests.get', side_effect=mocked_requests_get)
    def test_calculate_satellite_error(self, mock_get, mock_satellite):
        mock_satellite.return_value = (1, None, None)

        response = self.client.post('/calculate', data={
            'input_date_time': datetime.datetime(2026, 6, 1, 12, 0)
        })

        self.assertIn(
            "Something went wrong. Try again.",
            response.get_data(as_text=True)
        )

    @mock.patch('app.main.views.requests.get')
    def test_calculate_api_error(self, mock_get):
        class MockResponse:
            status_code = 404

            def json(self):
                return {}

        mock_get.return_value = MockResponse()

        response = self.client.post('/calculate', data={
            'input_date_time': datetime.datetime(2026, 6, 1, 12, 0)
        })

        self.assertIn(
            "Something went wrong. Try again.",
            response.get_data(as_text=True)
        )