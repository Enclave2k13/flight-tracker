import pytest

from src.aeroplane import Aeroplane


class TestAeroplane:
    """Тесты для класса Aeroplane"""

    def test_aeroplane_creation(self, sample_aeroplane):
        """Позитивный тест: создание объекта самолета"""
        assert sample_aeroplane.icao24 == "abc123"
        assert sample_aeroplane.callsign == "TEST123"
        assert sample_aeroplane.origin_country == "Testland"
        assert sample_aeroplane.altitude == 10000.0
        assert sample_aeroplane.velocity == 250.0
        assert not sample_aeroplane.on_ground

    def test_aeroplane_creation_with_none(self):
        """Тест: создание самолета с None значениями"""
        plane = Aeroplane(
            icao24="xyz789",
            callsign=None,
            origin_country="Test",
            longitude=None,
            latitude=None,
            altitude=None,
            velocity=None,
            on_ground=True,
        )
        assert plane.callsign == "Unknown"
        assert plane.altitude is None
        assert plane.on_ground is True

    def test_aeroplane_validation_invalid_icao(self):
        """Негативный тест: неверный ICAO24"""
        with pytest.raises(ValueError, match="ICAO24 должен быть непустой строкой"):
            Aeroplane(
                icao24="",
                callsign="TEST",
                origin_country="Test",
                longitude=10.0,
                latitude=20.0,
                altitude=10000.0,
                velocity=250.0,
                on_ground=False,
            )

    def test_aeroplane_validation_invalid_coordinates(self):
        """Негативный тест: неверные координаты"""
        with pytest.raises(ValueError, match="Долгота должна быть в диапазоне"):
            Aeroplane(
                icao24="abc123",
                callsign="TEST",
                origin_country="Test",
                longitude=200.0,  # неверно
                latitude=20.0,
                altitude=10000.0,
                velocity=250.0,
                on_ground=False,
            )

    def test_aeroplane_comparison(self, sample_aeroplanes_list):
        """Тест методов сравнения"""
        plane1, plane2, plane3 = sample_aeroplanes_list

        assert plane1 > plane2  # 10000 > 5000
        assert plane2 < plane1  # 5000 < 10000
        assert not (plane1 == plane2)
        assert plane3 is not None

    def test_cast_to_object_list(self, sample_api_response):
        """Тест преобразования API ответа в список объектов"""
        aeroplanes = Aeroplane.cast_to_object_list(sample_api_response)

        assert len(aeroplanes) == 3
        assert aeroplanes[0].icao24 == "abc123"
        assert aeroplanes[0].callsign == "TEST123"
        assert aeroplanes[0].altitude == 10000.0

        assert aeroplanes[1].icao24 == "def456"
        assert aeroplanes[1].callsign == "TEST456"

        assert aeroplanes[2].icao24 == "ghi789"
        assert aeroplanes[2].callsign == "Unknown"
        assert aeroplanes[2].on_ground is True

    def test_cast_to_object_list_empty(self):
        """Тест преобразования пустого ответа"""
        aeroplanes = Aeroplane.cast_to_object_list({"states": []})
        assert len(aeroplanes) == 0

    def test_aeroplane_repr(self, sample_aeroplane):
        """Тест строкового представления"""
        repr_str = repr(sample_aeroplane)
        assert "abc123" in repr_str
        assert "TEST123" in repr_str
        assert "Testland" in repr_str
        assert "10000.0" in repr_str
