from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Dict
from typing import Optional


class BaseAPI(ABC):
    """
    Абстрактный базовый класс для работы с API.

    Определяет структуру классов-наследников, которые будут работать
    с конкретными API сервисами.
    """

    @abstractmethod
    def _connect(self, url: str, params: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Приватный метод для подключения к API и получения данных.

        Args:
            url: Полный URL для запроса
            params: Параметры запроса
            headers: Заголовки запроса (опционально)

        Returns:
            Dict[str, Any]: Ответ от API в виде словаря

        Raises:
            ConnectionError: Если не удалось подключиться к API
        """
        pass

    @abstractmethod
    def get_aeroplanes(self, country: str) -> None:
        """
        Получить информацию о самолетах в воздушном пространстве страны.

        Args:
            country: Название страны на английском языке

        Returns:
            None: Результат сохраняется в атрибут класса
        """
        pass
