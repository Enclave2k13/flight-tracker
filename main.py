from src.user_interface import user_interaction

# !/usr/bin/env python3
"""
Трекер самолетов - курсовая работа
Главный модуль для запуска программы
"""

import os
import sys

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    try:
        user_interaction()
    except KeyboardInterrupt:
        print(f"\n\n{GREEN}Программа завершена пользователем.{RESET}")
    except Exception as e:
        print(f"{RED}Критическая ошибка: {e}{RESET}")
        sys.exit(1)
