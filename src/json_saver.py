import json
import os
from typing import Any
from typing import Dict
from typing import List

from .aeroplane import Aeroplane
from .file_saver import BaseFileSaver


class JSONSaver(BaseFileSaver):
    """
    Класс для сохранения информации о самолетах в JSON-файл.

    Атрибуты:
        __file_path (str): Путь к JSON-файлу
    """

    __slots__ = ("__file_path",)

    def __init__(self, file_path: str = "data/aeroplanes.json") -> None:
        """
        Инициализация JSON-сохранения.

        Args:
            file_path: Путь к JSON-файлу (по умолчанию "data/aeroplanes.json")
        """
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.__file_path = os.path.join(project_root, file_path)
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Приватный метод для создания файла и директории, если их нет."""
        directory = os.path.dirname(self.__file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        if not os.path.exists(self.__file_path):
            with open(self.__file_path, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)

    def _read_file(self) -> List[Dict[str, Any]]:
        """
        Приватный метод для чтения данных из файла.

        Returns:
            List[Dict[str, Any]]: Список словарей с данными о самолетах
        """
        try:
            with open(self.__file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _write_file(self, data: List[Dict[str, Any]]) -> None:
        """
        Приватный метод для записи данных в файл.

        Args:
            data: Список словарей для записи
        """
        with open(self.__file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def _aeroplane_to_dict(aeroplane: Aeroplane) -> Dict[str, Any]:
        """
        Преобразует объект Aeroplane в словарь для сохранения.

        Args:
            aeroplane: Объект самолета

        Returns:
            Dict[str, Any]: Словарь с данными самолета
        """
        return {
            "icao24": aeroplane.icao24,
            "callsign": aeroplane.callsign,
            "origin_country": aeroplane.origin_country,
            "longitude": aeroplane.longitude,
            "latitude": aeroplane.latitude,
            "altitude": aeroplane.altitude,
            "velocity": aeroplane.velocity,
            "on_ground": aeroplane.on_ground,
        }

    @staticmethod
    def _dict_to_aeroplane(data: Dict[str, Any]) -> Aeroplane:
        """
        Преобразует словарь в объект Aeroplane.

        Args:
            data: Словарь с данными самолета

        Returns:
            Aeroplane: Объект самолета
        """
        return Aeroplane(
            icao24=data["icao24"],
            callsign=data["callsign"],
            origin_country=data["origin_country"],
            longitude=data["longitude"],
            latitude=data["latitude"],
            altitude=data["altitude"],
            velocity=data["velocity"],
            on_ground=data["on_ground"],
        )

    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        """
        Добавить информацию о самолете в JSON-файл (без дубликатов).

        Args:
            aeroplane: Объект самолета для сохранения
        """
        data = self._read_file()

        aeroplane_dict = self._aeroplane_to_dict(aeroplane)

        data = [item for item in data if item["icao24"] != aeroplane.icao24]

        data.append(aeroplane_dict)

        self._write_file(data)
        print(f"Самолет {aeroplane.callsign} сохранен в {self.__file_path}")

    def add_aeroplanes(self, aeroplanes: List[Aeroplane]) -> None:
        """
        Добавить список самолетов в JSON-файл.

        Args:
            aeroplanes: Список объектов самолетов
        """
        data = self._read_file()

        existing_icaos = {item["icao24"] for item in data}

        new_count = 0
        updated_count = 0

        for aeroplane in aeroplanes:
            aeroplane_dict = self._aeroplane_to_dict(aeroplane)

            if aeroplane.icao24 in existing_icaos:
                data = [item for item in data if item["icao24"] != aeroplane.icao24]
                data.append(aeroplane_dict)
                updated_count += 1
            else:
                data.append(aeroplane_dict)
                existing_icaos.add(aeroplane.icao24)
                new_count += 1

        self._write_file(data)
        print(f"Добавлено: {new_count} новых, обновлено: {updated_count} самолетов")

    def get_aeroplanes(self, **criteria) -> List[Aeroplane]:
        """
        Получить самолеты из файла по критериям.

        Примеры:
            get_aeroplanes(origin_country='France')
            get_aeroplanes(min_altitude=10000, on_ground=False)
            get_aeroplanes(callsign='SWR')

        Args:
            **criteria: Критерии фильтрации

        Returns:
            List[Aeroplane]: Список самолетов
        """
        data = self._read_file()
        result = []

        for item in data:
            match = True

            for key, value in criteria.items():
                if key == "min_altitude":
                    if item["altitude"] is None or item["altitude"] < value:
                        match = False
                        break
                elif key == "max_altitude":
                    if item["altitude"] is None or item["altitude"] > value:
                        match = False
                        break
                elif key == "min_velocity":
                    if item["velocity"] is None or item["velocity"] < value:
                        match = False
                        break
                elif key == "on_ground":
                    if item["on_ground"] != value:
                        match = False
                        break
                elif key == "callsign_contains":
                    if value not in item["callsign"].upper():
                        match = False
                        break
                else:
                    if item.get(key) != value:
                        match = False
                        break

            if match:
                result.append(self._dict_to_aeroplane(item))

        return result

    def delete_aeroplane(self, **criteria) -> int:
        """
        Удалить информацию о самолетах по критериям.

        Args:
            **criteria: Критерии для удаления

        Returns:
            int: Количество удаленных записей
        """
        data = self._read_file()
        initial_count = len(data)

        new_data = []
        for item in data:
            keep = True
            for key, value in criteria.items():
                if item.get(key) == value:
                    keep = False
                    break
            if keep:
                new_data.append(item)

        deleted_count = initial_count - len(new_data)

        if deleted_count > 0:
            self._write_file(new_data)
            print(f"Удалено записей: {deleted_count}")

        return deleted_count

    @property
    def count(self) -> int:
        """Количество самолетов в файле."""
        return len(self._read_file())
