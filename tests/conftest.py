import os
import sys

import pytest

from src.aeroplane import Aeroplane

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def sample_aeroplane():
    """Фикстура с тестовым самолетом"""
    return Aeroplane(
        icao24="abc123",
        callsign="TEST123",
        origin_country="Testland",
        longitude=10.0,
        latitude=20.0,
        altitude=10000.0,
        velocity=250.0,
        on_ground=False,
    )


@pytest.fixture
def sample_aeroplanes_list():
    """Фикстура со списком тестовых самолетов"""
    return [
        Aeroplane("abc123", "TEST123", "Testland", 10.0, 20.0, 10000.0, 250.0, False),
        Aeroplane("def456", "TEST456", "Testland", None, None, 5000.0, 200.0, False),
        Aeroplane("ghi789", "TEST789", "Otherland", 30.0, 40.0, None, None, True),
    ]


@pytest.fixture
def sample_api_response():
    """Фикстура с ответом от OpenSky API"""
    return {
        "time": 1766142246,
        "states": [
            [
                "abc123",
                "TEST123",
                "Testland",
                1766166618,
                1766166618,
                10.0,
                20.0,
                10000.0,
                False,
                250.0,
                129.39,
                14.63,
                None,
                4282.44,
                "2061",
                False,
                0,
            ],
            [
                "def456",
                "TEST456",
                "Testland",
                1766166618,
                1766166618,
                None,
                None,
                5000.0,
                False,
                200.0,
                129.39,
                14.63,
                None,
                4282.44,
                "2061",
                False,
                0,
            ],
            [
                "ghi789",
                None,
                "Otherland",
                1766166618,
                1766166618,
                30.0,
                40.0,
                None,
                True,
                None,
                129.39,
                14.63,
                None,
                4282.44,
                "2061",
                False,
                0,
            ],
        ],
    }
