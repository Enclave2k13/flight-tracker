from unittest.mock import Mock
from unittest.mock import patch

import pytest
from requests.exceptions import HTTPError

from src.api_adapter import APIAdapter


class TestAPIAdapter:
    """Тесты для класса APIAdapter"""

    @patch("src.api_adapter.get")
    def test_connect_success(self, mock_get):
        """Позитивный тест: успешное подключение к API"""
        # Настраиваем мок
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "data"}
        mock_get.return_value = mock_response

        # Вызываем метод
        adapter = APIAdapter()
        result = adapter._connect("http://test.com", {"param": "value"}, {})

        # Проверяем
        assert result == {"test": "data"}
        mock_get.assert_called_once_with(url="http://test.com", params={"param": "value"}, headers={}, timeout=10)

    @patch("src.api_adapter.get")
    def test_connect_failure_status(self, mock_get):
        """Негативный тест: ошибка статус-кода"""
        mock_response = Mock()
        mock_response.status_code = 404

        http_error = HTTPError("404 Client Error")
        http_error.response = mock_response

        mock_response.raise_for_status.side_effect = http_error
        mock_get.return_value = mock_response

        adapter = APIAdapter()
        with pytest.raises(ConnectionError, match="HTTP ошибка: 404"):
            adapter._connect("http://test.com", {}, {})

    @patch("src.api_adapter.get")
    def test_connect_exception(self, mock_get):
        """Негативный тест: исключение при подключении"""
        mock_get.side_effect = Exception("Network error")

        adapter = APIAdapter()
        with pytest.raises(ConnectionError, match="Network error"):
            adapter._connect("http://test.com", {}, {})

    # ===== НОВЫЕ ТЕСТЫ для разделённых методов =====

    @patch.object(APIAdapter, "_connect")
    def test_get_country_coordinates_success(self, mock_connect):
        """Тест успешного получения координат страны"""
        mock_connect.return_value = [{"boundingbox": ["10", "20", "30", "40"]}]

        adapter = APIAdapter()
        result = adapter.get_country_coordinates("Testland")

        assert result == ["10", "20", "30", "40"]
        mock_connect.assert_called_once()

    @patch.object(APIAdapter, "_connect")
    def test_get_country_coordinates_not_found(self, mock_connect):
        """Тест: страна не найдена"""
        mock_connect.return_value = []  # пустой ответ от nominatim

        adapter = APIAdapter()
        result = adapter.get_country_coordinates("Nowhere")

        assert result is None

    @patch.object(APIAdapter, "_connect")
    def test_get_country_coordinates_no_bbox(self, mock_connect):
        """Тест: нет boundingbox в ответе"""
        mock_connect.return_value = [{}]  # нет boundingbox

        adapter = APIAdapter()
        result = adapter.get_country_coordinates("Testland")

        assert result is None

    @patch.object(APIAdapter, "_connect")
    def test_get_country_coordinates_invalid_format(self, mock_connect):
        """Тест: некорректный формат координат"""
        mock_connect.return_value = [{"boundingbox": "not a list"}]

        adapter = APIAdapter()
        result = adapter.get_country_coordinates("Testland")

        assert result is None

    @patch.object(APIAdapter, "_connect")
    def test_get_opensky_data_success(self, mock_connect):
        """Тест успешного получения данных OpenSky"""
        expected_data = {"states": [["abc123", "TEST", "Test", 0, 0, 10, 20, 1000, False, 250]]}
        mock_connect.return_value = expected_data

        adapter = APIAdapter()
        result = adapter.get_opensky_data(["10", "20", "30", "40"])

        assert result == expected_data
        mock_connect.assert_called_once()

    @patch.object(APIAdapter, "_connect")
    def test_get_opensky_data_failure(self, mock_connect):
        """Тест: ошибка при получении данных OpenSky"""
        mock_connect.side_effect = ConnectionError("OpenSky error")

        adapter = APIAdapter()
        result = adapter.get_opensky_data(["10", "20", "30", "40"])

        assert result is None

    # ===== ОБНОВЛЁННЫЙ тест get_aeroplanes =====

    @patch.object(APIAdapter, "get_opensky_data")
    @patch.object(APIAdapter, "get_country_coordinates")
    def test_get_aeroplanes_success(self, mock_coords, mock_opensky):
        """Тест получения самолетов по стране"""
        # Настраиваем моки
        mock_coords.return_value = ["10", "20", "30", "40"]
        mock_opensky.return_value = {"states": [["abc123", "TEST", "Test", 0, 0, 10, 20, 1000, False, 250]]}

        adapter = APIAdapter()
        adapter.get_aeroplanes("Testland")

        assert adapter.aeroplanes is not None
        assert "states" in adapter.aeroplanes
        mock_coords.assert_called_once_with("Testland")
        mock_opensky.assert_called_once_with(["10", "20", "30", "40"])

    @patch.object(APIAdapter, "get_country_coordinates")
    def test_get_aeroplanes_country_not_found(self, mock_coords):
        """Тест: страна не найдена"""
        mock_coords.return_value = None

        adapter = APIAdapter()
        adapter.get_aeroplanes("Nowhere")

        assert adapter.aeroplanes is None

    @patch.object(APIAdapter, "get_country_coordinates")
    @patch.object(APIAdapter, "get_opensky_data")
    def test_get_aeroplanes_opensky_failure(self, mock_opensky, mock_coords):
        """Тест: ошибка OpenSky API"""
        mock_coords.return_value = ["10", "20", "30", "40"]
        mock_opensky.return_value = None

        adapter = APIAdapter()
        adapter.get_aeroplanes("Testland")

        assert adapter.aeroplanes is None

    def test_aeroplanes_property(self):
        """Тест геттера aeroplanes"""
        adapter = APIAdapter()
        assert adapter.aeroplanes is None

        adapter._APIAdapter__aeroplanes = {"test": "data"}
        assert adapter.aeroplanes == {"test": "data"}
