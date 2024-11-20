import os
import logging
from datetime import datetime, timedelta
import traceback

class Logger:
    def __init__(self, path_to_log="logs", log_level=logging.INFO,make_log_folder=False):
        """
        Инициализация логгера.

        :param path_to_log: Путь к директории для хранения логов
        :param log_level: Уровень логирования (по умолчанию: logging.INFO)
        """
        # Убеждаемся, что директория логов существует
        self.path_to_log = path_to_log
        if make_log_folder:
            os.makedirs(self.path_to_log, exist_ok=True)

        self.log_level = log_level
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(self.log_level)

        self.current_log_file = None
        self.current_log_date = None
        self.console_handler = None
        self.chat_log_enabled = False

        # Создаем форматтер для логов
        self.formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s', 
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def get_log_filename(self, date=None):
        """
        Генерация имени файла лога на основе даты.

        :param date: Дата для файла лога (по умолчанию: текущая дата)
        :return: Полный путь к файлу лога
        """
        if date is None:
            date = datetime.now()
        filename = f"{date.strftime('%Y-%m-%d')}.log"
        return os.path.join(self.path_to_log, filename)

    def EnableChatLog(self):
        """
        Включить вывод логов в командную строку.
        """
        # Если консольный обработчик уже существует, ничего не делаем
        if not self.chat_log_enabled:
            self.console_handler = logging.StreamHandler()
            self.console_handler.setFormatter(self.formatter)
            self.logger.addHandler(self.console_handler)
            self.chat_log_enabled = True

    def DisableChatLog(self):
        """
        Отключить вывод логов в командную строку.
        """
        # Если консольный обработчик существует, удаляем его
        if self.chat_log_enabled and self.console_handler:
            self.logger.removeHandler(self.console_handler)
            self.console_handler = None
            self.chat_log_enabled = False

    def log(self, event, level=logging.INFO, source_file=None, exception=None):
        """
        Основной метод логирования.

        :param event: Сообщение события
        :param level: Уровень логирования
        :param source_file: Исходный файл лога (необязательно)
        :param exception: Объект исключения (необязательно)
        """
        # Определяем текущую дату
        current_date = datetime.now().date()

        # Проверка/создание файла лога для текущей даты
        if self.current_log_date != current_date:
            log_filename = self.get_log_filename()

            # Сбрасываем логгер
            self.logger = logging.getLogger(f'logger_{current_date}')
            self.logger.setLevel(self.log_level)
            
            # Очищаем существующие обработчики
            self.logger.handlers.clear()

            # Создаем файловый обработчик
            file_handler = logging.FileHandler(log_filename, encoding='utf-8')
            file_handler.setFormatter(self.formatter)
            self.logger.addHandler(file_handler)

            # Если был включен вывод в консоль, восстанавливаем его
            if self.chat_log_enabled:
                self.console_handler = logging.StreamHandler()
                self.console_handler.setFormatter(self.formatter)
                self.logger.addHandler(self.console_handler)

            # Обновляем текущую дату лога и файл
            self.current_log_date = current_date
            self.current_log_file = log_filename

        # Подготавливаем полное сообщение
        full_message = event
        if source_file:
            full_message = f"[{source_file}] {full_message}"

        # Логирование с обработкой исключений
        if exception:
            full_message += f"\nИсключение: {str(exception)}"
            full_message += f"\nТрассировка: {traceback.format_exc()}"
            self.logger.log(logging.ERROR, full_message)
        else:
            self.logger.log(level, full_message)

    def clean_old_logs(self, keep_days=7):
        """
        Удаление старых файлов логов.

        :param keep_days: Количество дней для хранения логов
        """
        current_date = datetime.now()
        for filename in os.listdir(self.path_to_log):
            try:
                # Пытаемся распарсить имя файла
                file_path = os.path.join(self.path_to_log, filename)
                file_date_str = filename.split('.')[0]  # Предполагаем формат YYYY-MM-DD.log
                file_date = datetime.strptime(file_date_str, '%Y-%m-%d').date()

                # Удаляем файл, если он старше указанного количества дней
                if (current_date.date() - file_date).days > keep_days:
                    os.remove(file_path)
            except (ValueError, IndexError):
                # Пропускаем файлы с неправильным форматом
                continue

def main():
    # Пример использования
    log = Logger()
    
    # Сначала логи в командную строку отключены
    log.log('Сообщение без вывода в консоль', logging.INFO, 'main.py')
    
    # Включаем вывод в консоль
    log.EnableChatLog() # По умолчанию выключенно 
    log.log('Это сообщение будет выведено в консоль', logging.INFO, 'main.py')
    
    # Пример ошибки 
    try:
        x = 1 / 0  
    except Exception as e:
        # Логирование ошибки с подробностями исключения
        log.log('Произошла ошибка', logging.ERROR, 'main.py', e)
    
    # Отключаем вывод в консоль
    log.DisableChatLog()
    log.log('Это сообщение не будет выведено в консоль', logging.INFO, 'main.py')
    

