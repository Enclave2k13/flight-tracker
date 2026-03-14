import json
import os
import tempfile

import pytest

from src.aeroplane import Aeroplane
from src.json_saver import JSONSaver


class TestJSONSaver:
    """Тесты для класса JSONSaver"""

    @pytest.fixture
    def temp_json_file(self):
        """Фикстура для временного JSON файла"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump([], f)
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)

    @pytest.fixture
    def saver(self, temp_json_file):
        """Фикстура с JSONSaver на временном файле"""
        return JSONSaver(temp_json_file)

    @pytest.fixture
    def sample_plane(self):
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

    def test_init_creates_file(self):
        """Тест: создание файла при инициализации"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.json")
            JSONSaver(file_path)

            assert os.path.exists(file_path)
            with open(file_path, "r") as f:
                data = json.load(f)
            assert data == []

    def test_add_aeroplane(self, saver, sample_plane):
        """Тест добавления одного самолета"""
        saver.add_aeroplane(sample_plane)

        assert saver.count == 1

        # Проверяем содержимое
        planes = saver.get_aeroplanes()
        assert len(planes) == 1
        assert planes[0].icao24 == "abc123"
        assert planes[0].callsign == "TEST123"

    def test_add_aeroplane_no_duplicates(self, saver, sample_plane):
        """Тест: отсутствие дубликатов"""
        saver.add_aeroplane(sample_plane)
        saver.add_aeroplane(sample_plane)  # добавляем того же

        assert saver.count == 1  # должно быть все еще 1

    def test_add_aeroplanes(self, saver, sample_aeroplanes_list):
        """Тест добавления списка самолетов"""
        saver.add_aeroplanes(sample_aeroplanes_list)

        assert saver.count == 3

        planes = saver.get_aeroplanes()
        assert len(planes) == 3

    def test_get_aeroplanes_filter_by_country(self, saver, sample_aeroplanes_list):
        """Тест фильтрации по стране"""
        saver.add_aeroplanes(sample_aeroplanes_list)

        testland_planes = saver.get_aeroplanes(origin_country="Testland")
        assert len(testland_planes) == 2

        otherland_planes = saver.get_aeroplanes(origin_country="Otherland")
        assert len(otherland_planes) == 1

    def test_get_aeroplanes_filter_by_altitude(self, saver, sample_aeroplanes_list):
        """Тест фильтрации по высоте"""
        saver.add_aeroplanes(sample_aeroplanes_list)

        high_planes = saver.get_aeroplanes(min_altitude=8000)
        assert len(high_planes) == 1
        assert high_planes[0].altitude == 10000.0

        low_planes = saver.get_aeroplanes(max_altitude=6000)
        assert len(low_planes) == 1
        assert low_planes[0].altitude == 5000.0

    def test_get_aeroplanes_filter_by_on_ground(self, saver, sample_aeroplanes_list):
        """Тест фильтрации по статусу на земле"""
        saver.add_aeroplanes(sample_aeroplanes_list)

        ground_planes = saver.get_aeroplanes(on_ground=True)
        assert len(ground_planes) == 1
        assert ground_planes[0].on_ground is True

        air_planes = saver.get_aeroplanes(on_ground=False)
        assert len(air_planes) == 2

    def test_get_aeroplanes_filter_by_callsign(self, saver, sample_aeroplanes_list):
        """Тест фильтрации по части позывного"""
        saver.add_aeroplanes(sample_aeroplanes_list)

        test_planes = saver.get_aeroplanes(callsign_contains="TEST")
        assert len(test_planes) == 3

    def test_delete_aeroplane(self, saver, sample_aeroplanes_list):
        """Тест удаления самолетов"""
        saver.add_aeroplanes(sample_aeroplanes_list)
        assert saver.count == 3

        deleted = saver.delete_aeroplane(origin_country="Testland")
        assert deleted == 2
        assert saver.count == 1

        remaining = saver.get_aeroplanes()
        assert remaining[0].origin_country == "Otherland"

    def test_clear(self, saver, sample_aeroplanes_list):
        """Тест очистки файла"""
        saver.add_aeroplanes(sample_aeroplanes_list)
        assert saver.count == 3

        saver.clear()
        assert saver.count == 0
        assert saver.get_aeroplanes() == []

    def test_count_property(self, saver, sample_aeroplanes_list):
        """Тест свойства count"""
        assert saver.count == 0

        saver.add_aeroplanes(sample_aeroplanes_list)
        assert saver.count == 3

        saver.delete_aeroplane(origin_country="Testland")
        assert saver.count == 1
