import socket
from typing import Any
from typing import Dict
from typing import Optional

import requests.packages.urllib3.util.connection as urllib3_cn
from requests import get

from .abstract_api import BaseAPI


def allowed_gateways_family():
    """
    Принудительно используем IPv4 для всех соединений urllib3.
    Решает проблему с IPv6 на Windows.
    """
    return socket.AF_INET


urllib3_cn.allowed_gateways_family = allowed_gateways_family


class APIAdapter(BaseAPI):
    """
    Класс для работы с конкретными API: nominatim.openstreetmap.org и opensky-network.org.

    Наследуется от BaseAPI и реализует все его абстрактные методы.
    """

    def __init__(self) -> None:
        """Инициализация адаптера с URL-ами конкретных API."""
        super().__init__()
        self.__openstreetmap_url = "https://nominatim.openstreetmap.org/search"
        self.__opensky_url = "https://opensky-network.org/api/states/all?"
        self.__aeroplanes: Optional[Dict[str, Any]] = None

    def _connect(self, url: str, params: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Реализация подключения к API с проверкой статус-кода.

        Args:
            url: URL для запроса
            params: Параметры запроса
            headers: Заголовки запроса

        Returns:
            Dict[str, Any]: JSON-ответ от API

        Raises:
            ConnectionError: Если статус-код не 200
        """
        if headers is None:
            headers = {}

        try:
            response = get(url=url, params=params, headers=headers, timeout=10)

            if response.status_code != 200:
                raise ConnectionError(f"Ошибка подключения к API. Статус код: {response.status_code}")

            return response.json()

        except Exception as e:
            raise ConnectionError(f"Не удалось подключиться к {url}: {str(e)}")

    def get_aeroplanes(self, country: str) -> None:
        """
        Получить информацию о самолетах в указанной стране.

        Args:
            country: Название страны на английском

        Returns:
            None: Результат сохраняется в self.__aeroplanes
        """
        headers_nominatim = {
            "User-Agent": "flight-tracker-app/1.0",
        }

        params_nominatim = {
            "country": country,
            "format": "json",
            "limit": 1,
        }

        try:
            nominatim_data = self._connect(
                url=self.__openstreetmap_url,
                params=params_nominatim,
                headers=headers_nominatim,
            )
        except ConnectionError as e:
            print(f"Ошибка при получении координат страны: {e}")
            return

        if not nominatim_data or len(nominatim_data) == 0:
            print(f"Страна '{country}' не найдена")
            return

        geo_coordinates = nominatim_data[0].get("boundingbox")
        if not geo_coordinates:
            print("Не удалось получить координаты страны")
            return

        params_opensky = {
            "lamin": geo_coordinates[0],  # юг
            "lamax": geo_coordinates[1],  # север
            "lomin": geo_coordinates[2],  # запад
            "lomax": geo_coordinates[3],  # восток
        }

        try:
            opensky_data = self._connect(url=self.__opensky_url, params=params_opensky, headers=None)
        except ConnectionError as e:
            print(f"Ошибка при получении данных о самолетах: {e}")
            return

        self.__aeroplanes = opensky_data

        states = opensky_data.get("states", [])
        print(f"Найдено самолетов в воздушном пространстве {country}: {len(states)}")

    @property
    def aeroplanes(self) -> Optional[Dict[str, Any]]:
        """
        Геттер для получения данных о самолетах.

        Returns:
            Optional[Dict[str, Any]]: Данные о самолетах или None
        """
        return self.__aeroplanes
