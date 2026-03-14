from unittest.mock import Mock
from unittest.mock import patch

import pytest

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
        mock_get.return_value = mock_response

        adapter = APIAdapter()
        with pytest.raises(ConnectionError, match="Ошибка подключения.*404"):
            adapter._connect("http://test.com", {}, {})

    @patch("src.api_adapter.get")
    def test_connect_exception(self, mock_get):
        """Негативный тест: исключение при подключении"""
        mock_get.side_effect = Exception("Network error")

        adapter = APIAdapter()
        with pytest.raises(ConnectionError, match="Network error"):
            adapter._connect("http://test.com", {}, {})

    @patch.object(APIAdapter, "_connect")
    def test_get_aeroplanes_success(self, mock_connect):
        """Тест получения самолетов по стране"""
        # Настраиваем моки
        mock_connect.side_effect = [
            # Первый вызов - nominatim
            [{"boundingbox": ["10", "20", "30", "40"]}],
            # Второй вызов - opensky
            {"states": [["abc123", "TEST", "Test", 0, 0, 10, 20, 1000, False, 250]]},
        ]

        adapter = APIAdapter()
        adapter.get_aeroplanes("Testland")

        assert adapter.aeroplanes is not None
        assert "states" in adapter.aeroplanes

    @patch.object(APIAdapter, "_connect")
    def test_get_aeroplanes_country_not_found(self, mock_connect):
        """Тест: страна не найдена"""
        mock_connect.return_value = []  # пустой ответ от nominatim

        adapter = APIAdapter()
        adapter.get_aeroplanes("Nowhere")

        assert adapter.aeroplanes is None

    @patch.object(APIAdapter, "_connect")
    def test_get_aeroplanes_no_coordinates(self, mock_connect):
        """Тест: нет координат в ответе"""
        mock_connect.return_value = [{}]  # нет boundingbox

        adapter = APIAdapter()
        adapter.get_aeroplanes("Testland")

        assert adapter.aeroplanes is None

    def test_aeroplanes_property(self):
        """Тест геттера aeroplanes"""
        adapter = APIAdapter()
        assert adapter.aeroplanes is None

        adapter._APIAdapter__aeroplanes = {"test": "data"}
        assert adapter.aeroplanes == {"test": "data"}
