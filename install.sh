#!/bin/bash

# Установка кодировки UTF-8
export LANG=en_US.UTF-8

# Определение текущей директории
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Функция для вывода цветного текста
print_color() {
    local color=$1
    local message=$2
    case $color in
        green)  echo -e "\033[32m$message\033[0m" ;;
        yellow) echo -e "\033[33m$message\033[0m" ;;
        red)    echo -e "\033[31m$message\033[0m" ;;
        *)      echo "$message" ;;
    esac
}

# Спросить пользователя, хочет ли он установить модули
read -p "Начать установку? (y/n, нажмите Enter для \"y\"): " install

# По умолчанию - да
install=${install:-y}

# Проверка ввода
if [[ "$install" == "y" ]]; then
    print_color green "Обновление pip"
    python3 -m pip install --upgrade pip

    print_color green "Установка модулей"
    pip3 install -r "${SCRIPT_DIR}/requirements.txt"

    # Создание директории логов (если не существует)
    mkdir -p "${SCRIPT_DIR}/logs"

    # Очистка экрана
    clear

    print_color yellow "Запуск программы"
    
    # Пауза на 5 секунд
    sleep 5

    # Запуск python-скрипта
    python3 "${SCRIPT_DIR}/modules/FirstStart.py"

elif [[ "$install" == "n" ]]; then
    print_color red "Установка отменена"
    exit 0
else
    print_color red "Некорректный ввод"
    exit 1
fi

# Ожидание нажатия клавиши
read -n 1 -s -r -p "Нажмите любую клавишу, чтобы закрыть окно..."