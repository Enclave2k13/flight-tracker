import logging
import socket
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import requests.packages.urllib3.util.connection as urllib3_cn
from requests import get
from requests.exceptions import HTTPError
from requests.exceptions import RequestException

from .abstract_api import BaseAPI

logger = logging.getLogger(__name__)


def allowed_gateways_family():
    """Принудительно используем IPv4 для всех соединений urllib3."""
    return socket.AF_INET


urllib3_cn.allowed_gateways_family = allowed_gateways_family


class APIAdapter(BaseAPI):
    """
    Класс для работы с API: nominatim.openstreetmap.org и opensky-network.org.
    """

    def __init__(self) -> None:
        """Инициализация адаптера с URL-ами конкретных API."""
        super().__init__()
        self.__openstreetmap_url = "https://nominatim.openstreetmap.org/search"
        self.__opensky_url = "https://opensky-network.org/api/states/all?"
        self.__aeroplanes: Optional[Dict[str, Any]] = None

    def _connect(self, url: str, params: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Базовый метод для подключения к API."""
        if headers is None:
            headers = {}

        try:
            response = get(url=url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()

        except HTTPError as e:
            logger.error(f"HTTP ошибка {e.response.status_code} при запросе к {url}")
            raise ConnectionError(f"HTTP ошибка: {e.response.status_code}") from e

        except RequestException as e:
            logger.error(f"Ошибка запроса к {url}: {str(e)}")
            raise ConnectionError(f"Не удалось подключиться к {url}: {str(e)}") from e

        except Exception as e:
            logger.error(f"Неожиданная ошибка при подключении к {url}: {str(e)}")
            raise ConnectionError(f"Критическая ошибка: {str(e)}") from e

    def get_country_coordinates(self, country: str) -> Optional[List[str]]:
        """
        Получает координаты страны через Nominatim API.

        Args:
            country: Название страны

        Returns:
            Optional[List[str]]: [юг, север, запад, восток] или None при ошибке
        """
        headers = {"User-Agent": "flight-tracker-app/1.0"}
        params = {"country": country, "format": "json", "limit": 1}

        try:
            data = self._connect(self.__openstreetmap_url, params, headers)
        except ConnectionError as e:
            logger.error(f"Ошибка получения координат для {country}: {e}")
            return None

        if not data:
            logger.warning(f"Страна '{country}' не найдена")
            return None

        raw_bbox = data[0].get("boundingbox")
        if not raw_bbox:
            logger.warning(f"Нет координат для страны '{country}'")
            return None

        if not raw_bbox or not isinstance(raw_bbox, list):
            logger.warning(f"Некорректный формат координат для страны '{country}'")
            return None

        bbox = [str(coord) for coord in raw_bbox]
        if len(bbox) < 4:
            logger.warning(f"Недостаточно координат для страны '{country}': {bbox}")
            return None

        logger.info(f"Получены координаты для {country}: {bbox}")
        return bbox

    def get_opensky_data(self, bbox: List[str]) -> Optional[Dict[str, Any]]:
        """
        Получает данные о самолётах через OpenSky API.

        Args:
            bbox: Список [юг, север, запад, восток]

        Returns:
            Optional[Dict]: Ответ от API или None при ошибке
        """
        params = {
            "lamin": bbox[0],
            "lamax": bbox[1],
            "lomin": bbox[2],
            "lomax": bbox[3],
        }

        try:
            data = self._connect(self.__opensky_url, params, None)
            logger.info(f"Получено {len(data.get('states', []))} самолётов")
            return data
        except ConnectionError as e:
            logger.error(f"Ошибка получения данных OpenSky: {e}")
            return None

    def get_aeroplanes(self, country: str) -> None:
        """
        Основной метод: получает координаты страны и затем данные о самолётах.
        """
        bbox = self.get_country_coordinates(country)
        if not bbox:
            return

        data = self.get_opensky_data(bbox)
        if not data:
            return

        self.__aeroplanes = data
        logger.info(f"Данные для {country} успешно получены и сохранены")

    @property
    def aeroplanes(self) -> Optional[Dict[str, Any]]:
        """Геттер для данных о самолетах."""
        return self.__aeroplanes
