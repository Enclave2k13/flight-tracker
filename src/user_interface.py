"""
Модуль для взаимодействия с пользователем через консоль.
"""

import os
from typing import List

from .aeroplane import Aeroplane
from .api_adapter import APIAdapter
from .json_saver import JSONSaver

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Включаем поддержку цветов в Windows
os.system("color")


def display_aeroplanes(aeroplanes: List[Aeroplane], limit: int = 10) -> None:
    """
    Выводит список самолетов в консоль.

    Args:
        aeroplanes: Список самолетов
        limit: Максимальное количество для вывода
    """
    if not aeroplanes:
        print(f"{YELLOW}Нет самолетов для отображения{RESET}")
        return

    print(f"\n   {CYAN}{'=' * 60}{RESET}")
    for i, plane in enumerate(aeroplanes[:limit], 1):
        callsign = plane.callsign if plane.callsign != "Unknown" else "---"
        country = plane.origin_country
        altitude = f"{plane.altitude:.1f} м" if plane.altitude else "на земле"
        velocity = f"{plane.velocity:.1f} м/с" if plane.velocity else "---"

        # Выбираем цвет в зависимости от статуса
        if plane.on_ground:
            status_color = YELLOW
            status = "на земле"
        else:
            status_color = GREEN
            status = "в воздухе"

        print(
            f"   {status_color}{i:2}. {status} | {callsign:8} | {country:15} | "
            f"высота: {altitude:10} | скорость: {velocity}{RESET}"
        )

    if len(aeroplanes) > limit:
        print(f"   {CYAN}... и еще {len(aeroplanes) - limit} самолетов{RESET}")


def get_top_by_altitude(aeroplanes: List[Aeroplane], n: int) -> List[Aeroplane]:
    """
    Возвращает топ N самолетов по высоте.

    Args:
        aeroplanes: Список самолетов
        n: Количество самолетов в топе

    Returns:
        List[Aeroplane]: Отсортированный список
    """
    sorted_planes = sorted(
        [p for p in aeroplanes if p.altitude is not None],
        key=lambda p: p.altitude,
        reverse=True,
    )
    return sorted_planes[:n]


def filter_by_country(aeroplanes: List[Aeroplane], countries: List[str]) -> List[Aeroplane]:
    """
    Фильтрует самолеты по стране регистрации.

    Args:
        aeroplanes: Список самолетов
        countries: Список стран для фильтрации

    Returns:
        List[Aeroplane]: Отфильтрованный список
    """
    if not countries:
        return aeroplanes

    countries_lower = [c.lower() for c in countries]

    return [p for p in aeroplanes if p.origin_country and p.origin_country.lower() in countries_lower]


def user_interaction() -> None:
    """
    Главная функция взаимодействия с пользователем.
    """
    print(f"\n{BOLD}{BLUE}{'=' * 60}{RESET}")
    print(f"{BOLD}{CYAN}ДОБРО ПОЖАЛОВАТЬ В ТРЕКЕР САМОЛЕТОВ{RESET}")
    print(f"{BOLD}{BLUE}{'=' * 60}{RESET}")

    api = APIAdapter()
    saver = JSONSaver()

    while True:
        print(f"\n{MAGENTA}{'-' * 40}{RESET}")
        print(f"{BOLD}ГЛАВНОЕ МЕНЮ:{RESET}")
        print("1. Получить данные о самолетах над страной")
        print("2. Показать топ N самолетов по высоте")
        print("3. Найти самолеты по стране регистрации")
        print("4. Показать статистику по сохраненным данным")
        print("0. Выход")
        print(f"{MAGENTA}{'-' * 40}{RESET}")

        choice = input("Выберите действие (0-4): ").strip()

        if choice == "0":
            print(f"\n{GREEN}До свидания! Хорошего полета!{RESET}")
            break

        elif choice == "1":
            country = input("\nВведите название страны на английском (например, France): ").strip()
            if not country:
                print(f"{RED}Страна не может быть пустой{RESET}")
                continue

            print(f"\n{CYAN}Запрашиваю данные о самолетах над {country}...{RESET}")
            api.get_aeroplanes(country)

            if not api.aeroplanes:
                print(f"{RED}Не удалось получить данные{RESET}")
                continue

            aeroplanes = Aeroplane.cast_to_object_list(api.aeroplanes)
            print(f"\n{GREEN}Получено данных: {len(api.aeroplanes.get('states', []))}{RESET}")
            print(f"{GREEN}Создано объектов: {len(aeroplanes)}{RESET}")

            print(f"\n{CYAN}Первые 10 самолетов:{RESET}")
            display_aeroplanes(aeroplanes, 10)

            save_choice = input("\nСохранить данные в файл? (y/n): ").strip().lower()
            if save_choice == "y":
                saver.add_aeroplanes(aeroplanes)
                print(f"{GREEN}Всего в файле теперь {saver.count} записей{RESET}")

        elif choice == "2":
            try:
                n = int(input("\nСколько самолетов показать в топе? (например, 5): ").strip())
                if n <= 0:
                    print(f"{RED}Число должно быть положительным{RESET}")
                    continue
            except ValueError:
                print(f"{RED}Введите корректное число{RESET}")
                continue

            aeroplanes = saver.get_aeroplanes()
            if not aeroplanes:
                print(f"{YELLOW}Сначала получите данные (пункт 1) и сохраните их{RESET}")
                continue

            top_planes = get_top_by_altitude(aeroplanes, n)
            print(f"\n{BOLD}{CYAN}ТОП-{n} САМЫХ ВЫСОКИХ САМОЛЕТОВ:{RESET}")
            display_aeroplanes(top_planes, n)

        elif choice == "3":
            countries_input = input(
                "\nВведите страны для фильтрации (через пробел, например: France Switzerland): "
            ).strip()
            if not countries_input:
                print(f"{RED}Введите хотя бы одну страну{RESET}")
                continue

            countries = countries_input.split()
            aeroplanes = saver.get_aeroplanes()

            if not aeroplanes:
                print(f"{YELLOW}Сначала получите данные (пункт 1) и сохраните их{RESET}")
                continue

            filtered = filter_by_country(aeroplanes, countries)
            print(f"\n{GREEN}Найдено самолетов из {', '.join(countries)}: {len(filtered)}{RESET}")
            if filtered:
                display_aeroplanes(filtered, 15)

        elif choice == "4":
            count = saver.count
            if count == 0:
                print(f"{YELLOW}\nФайл пуст. Сначала получите и сохраните данные.{RESET}")
                continue

            aeroplanes = saver.get_aeroplanes()

            on_ground = sum(1 for p in aeroplanes if p.on_ground)
            in_air = count - on_ground
            with_altitude = sum(1 for p in aeroplanes if p.altitude is not None)
            avg_altitude = sum(p.altitude for p in aeroplanes if p.altitude) / with_altitude if with_altitude else 0

            countries_count = {}
            for p in aeroplanes:
                countries_count[p.origin_country] = countries_count.get(p.origin_country, 0) + 1
            top_countries = sorted(countries_count.items(), key=lambda x: x[1], reverse=True)[:5]

            print(f"\n{BOLD}{CYAN}СТАТИСТИКА ПО СОХРАНЕННЫМ ДАННЫМ:{RESET}")
            print(f"Всего записей: {count}")
            print(f"{GREEN}В воздухе: {in_air}{RESET}")
            print(f"{YELLOW}На земле: {on_ground}{RESET}")
            print(f"Средняя высота: {avg_altitude:.1f} м")
            print(f"\n{CYAN}Топ-5 стран регистрации:{RESET}")
            for country, cnt in top_countries:
                print(f"      {country}: {cnt} самолетов")

        else:
            print(f"{RED}Неверный выбор. Попробуйте снова.{RESET}")


if __name__ == "__main__":
    user_interaction()
