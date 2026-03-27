from abc import ABC
from abc import abstractmethod
from typing import List

from .aeroplane import Aeroplane


class BaseFileSaver(ABC):
    """
    Абстрактный базовый класс для работы с файлами.
    Определяет интерфейс для сохранения, получения и удаления данных о самолетах.
    """

    @abstractmethod
    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        """
        Добавить информацию о самолете в файл.

        Args:
            aeroplane: Объект самолета для сохранения
        """
        pass

    @abstractmethod
    def add_aeroplanes(self, aeroplanes: List[Aeroplane]) -> None:
        """
        Добавить список самолетов в файл.

        Args:
            aeroplanes: Список объектов самолетов
        """
        pass

    @abstractmethod
    def get_aeroplanes(self, **criteria) -> List[Aeroplane]:
        """
        Получить самолеты из файла по критериям.

        Args:
            **criteria: Критерии фильтрации (например, country='France', min_altitude=10000)

        Returns:
            List[Aeroplane]: Список самолетов, удовлетворяющих критериям
        """
        pass

    @abstractmethod
    def delete_aeroplane(self, **criteria) -> int:
        """
        Удалить информацию о самолетах по критериям.

        Args:
            **criteria: Критерии для удаления (например, icao24='4b1812')

        Returns:
            int: Количество удаленных записей
        """
        pass
