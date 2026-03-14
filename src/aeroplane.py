from typing import Any
from typing import Dict
from typing import List
from typing import Optional


class Aeroplane:
    """
    Класс, представляющий информацию о самолете.

    Атрибуты:
        icao24 (str): Уникальный идентификатор борта
        callsign (str): Позывной рейса
        origin_country (str): Страна регистрации
        longitude (Optional[float]): Долгота
        latitude (Optional[float]): Широта
        altitude (Optional[float]): Барометрическая высота (метры)
        velocity (Optional[float]): Горизонтальная скорость (м/с)
        on_ground (bool): Находится ли на земле
    """

    __slots__ = (
        "icao24",
        "callsign",
        "origin_country",
        "longitude",
        "latitude",
        "altitude",
        "velocity",
        "on_ground",
    )

    def __init__(
        self,
        icao24: str,
        callsign: Optional[str],
        origin_country: str,
        longitude: Optional[float],
        latitude: Optional[float],
        altitude: Optional[float],
        velocity: Optional[float],
        on_ground: bool,
    ) -> None:
        """
        Инициализация объекта самолета с валидацией данных.
        """
        self._validate_icao24(icao24)
        self._validate_callsign(callsign)
        self._validate_country(origin_country)
        self._validate_coordinates(longitude, latitude)
        self._validate_altitude(altitude)
        self._validate_velocity(velocity)
        self._validate_on_ground(on_ground)

        self.icao24 = icao24
        self.callsign = callsign.strip() if callsign else "Unknown"
        self.origin_country = origin_country
        self.longitude = longitude
        self.latitude = latitude
        self.altitude = altitude
        self.velocity = velocity
        self.on_ground = on_ground

    @staticmethod
    def _validate_icao24(icao24: str) -> None:
        """Приватный статический метод валидации ICAO24 кода."""
        if not isinstance(icao24, str) or len(icao24) < 1:
            raise ValueError("ICAO24 должен быть непустой строкой")

    @staticmethod
    def _validate_callsign(callsign: Optional[str]) -> None:
        """Приватный статический метод валидации позывного."""
        if callsign is not None and not isinstance(callsign, str):
            raise ValueError("Позывной должен быть строкой или None")

    @staticmethod
    def _validate_country(country: str) -> None:
        """Приватный статический метод валидации страны."""
        if not isinstance(country, str) or len(country) < 1:
            raise ValueError("Страна должна быть непустой строкой")

    @staticmethod
    def _validate_coordinates(lon: Optional[float], lat: Optional[float]) -> None:
        """Приватный статический метод валидации координат."""
        if lon is not None and (lon < -180 or lon > 180):
            raise ValueError(f"Долгота должна быть в диапазоне [-180, 180], получено {lon}")
        if lat is not None and (lat < -90 or lat > 90):
            raise ValueError(f"Широта должна быть в диапазоне [-90, 90], получено {lat}")

    @staticmethod
    def _validate_altitude(altitude: Optional[float]) -> None:
        """Приватный статический метод валидации высоты."""
        if altitude is not None and altitude < -1000:
            raise ValueError(f"Высота не может быть меньше -1000, получено {altitude}")

    @staticmethod
    def _validate_velocity(velocity: Optional[float]) -> None:
        """Приватный статический метод валидации скорости."""
        if velocity is not None and velocity < 0:
            raise ValueError(f"Скорость не может быть отрицательной, получено {velocity}")

    @staticmethod
    def _validate_on_ground(on_ground: bool) -> None:
        """Приватный статический метод валидации флага нахождения на земле."""
        if not isinstance(on_ground, bool):
            raise ValueError("on_ground должен быть булевым значением")

    def __eq__(self, other: object) -> bool:
        """Сравнение самолетов по высоте (равенство)."""
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self.altitude == other.altitude

    def __lt__(self, other: object) -> bool:
        """Сравнение самолетов по высоте (меньше)."""
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return (self.altitude or 0) < (other.altitude or 0)

    def __gt__(self, other: object) -> bool:
        """Сравнение самолетов по высоте (больше)."""
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return (self.altitude or 0) > (other.altitude or 0)

    def __repr__(self) -> str:
        """Строковое представление для отладки."""
        return (
            f"Aeroplane(icao24='{self.icao24}', callsign='{self.callsign}', "
            f"country='{self.origin_country}', altitude={self.altitude})"
        )

    @classmethod
    def cast_to_object_list(cls, data: Dict[str, Any], max_errors: int = 10) -> List["Aeroplane"]:
        """
        Преобразует данные из API OpenSky в список объектов Aeroplane.

        Args:
            data: Словарь с данными от API (ключ 'states' содержит список самолетов)
            max_errors: Максимальное количество выводимых ошибок (по умолчанию 10)

        Returns:
            List[Aeroplane]: Список объектов самолетов
        """
        aeroplanes = []
        states = data.get("states", [])
        error_count = 0

        if not states:
            print("Нет данных о самолетах")
            return aeroplanes

        for i, state in enumerate(states):
            try:
                # Извлекаем все поля по индексам из документации OpenSky
                icao24 = state[0] if state[0] is not None else "unknown"
                callsign = state[1]
                origin_country = state[2] if state[2] is not None else "unknown"
                longitude = state[5]
                latitude = state[6]
                altitude = state[7]
                on_ground = state[8]
                velocity = state[9]

                # Преобразуем on_ground в булево значение, если пришло что-то другое
                if not isinstance(on_ground, bool):
                    on_ground = bool(on_ground) if on_ground is not None else False

                aeroplane = cls(
                    icao24,
                    callsign,
                    origin_country,
                    longitude,
                    latitude,
                    altitude,
                    velocity,
                    on_ground,
                )
                aeroplanes.append(aeroplane)

            except (IndexError, ValueError, TypeError) as e:
                error_count += 1
                if error_count <= max_errors:
                    print(f"Ошибка при обработке самолета #{i}: {e}")
                elif error_count == max_errors + 1:
                    print(f"... и еще {len(states) - i} ошибок (дальше не показываю)")
                continue

        if error_count > 0:
            print(f"\nИтого пропущено самолетов с ошибками: {error_count}")

        return aeroplanes
