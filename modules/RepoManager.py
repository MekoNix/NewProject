import git
import os
from Logger import Logger
from datetime import datetime, timedelta
import traceback
import os
import logging
import requests
import zipfile
import shutil
from datetime import datetime
from platform import platform


#Класс с базовыми функциями. 

class Base():

    def __init__(self, projectpath=None):
        self.projectpath = self.FindProjectPath()   

    def FindProjectPath(self):
        # Get the directory of the current file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to get the project directory
        project_dir = os.path.dirname(current_dir)
        return project_dir
    def ClearChat(self):
        if 'Windows' in str(platform()): # Проверка платформы и отчистка
            os.system("cls")
        else:
            os.system("clear")


class GitHubUpdater(Logger):
    def __init__(self, repo_url, branch='main', projectpath=None):
        """
        Инициализация менеджера репозитория
        :param repo_url: URL репозитория GitHub (например, 'owner/repo')
        :param branch: Ветка для загрузки (по умолчанию 'main')
        :param projectpath: Путь к проекту (если None, будет определен автоматически)
        """
        self.repo_url = repo_url
        self.branch = branch
        self.projectpath = self.find_project_path()
        self.temp_dir = os.path.join(self.projectpath, 'temp_update')
        self.log = Logger()

    def find_project_path(self):
        """Определение директории проекта"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(current_dir)
        return project_dir

    def download_latest_commit(self):
        """Загрузка последнего коммита с GitHub"""
        try:
            # Формируем URL для загрузки ZIP архива
            download_url = f"https://github.com/{self.repo_url}/archive/{self.branch}.zip"
            
            # Загружаем архив
            self.log.log('Начало загрузки архива...', logging.INFO, 'main.py')
            response = requests.get(download_url, stream=True)
            response.raise_for_status()

            # Создаем временную директорию, если её нет
            os.makedirs(self.temp_dir, exist_ok=True)
            zip_path = os.path.join(self.temp_dir, 'update.zip')

            # Сохраняем архив
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            self.log.log('Архив успешно загружен', logging.INFO, 'main.py')
            return zip_path

        except requests.exceptions.RequestException as e:
            self.log.log(f'Ошибка при загрузке архива: {str(e)}', logging.ERROR, 'main.py')
            raise

    def backup_current_version(self):
        """Создание резервной копии текущей версии"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = os.path.join(self.projectpath, f'backup_{timestamp}')
            
            self.log.log('Создание резервной копии...', logging.INFO, 'main.py')
            shutil.copytree(self.projectpath, backup_dir, ignore=shutil.ignore_patterns('backup_*', 'temp_update'))
            
            self.log.log(f'Резервная копия создана в {backup_dir}', logging.INFO, 'main.py')
            return backup_dir

        except Exception as e:
            self.log.log(f'Ошибка при создании резервной копии: {str(e)}', logging.ERROR, 'main.py')
            raise

    def update_project(self):
        """Обновление проекта до последней версии"""
        try:
            # Загружаем последний коммит
            zip_path = self.download_latest_commit()

            # Создаем резервную копию
            backup_path = self.backup_current_version()

            # Распаковываем архив
            self.log.log('Распаковка архива...', logging.INFO, 'main.py')
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir)

            # Находим распакованную директорию
            extracted_dir = None
            for item in os.listdir(self.temp_dir):
                if os.path.isdir(os.path.join(self.temp_dir, item)) and item != '__MACOSX':
                    extracted_dir = os.path.join(self.temp_dir, item)
                    break

            if not extracted_dir:
                raise Exception("Не удалось найти распакованную директорию")

            # Копируем новые файлы в директорию проекта
            self.log.log('Копирование новых файлов...', logging.INFO, 'main.py')
            for item in os.listdir(extracted_dir):
                s = os.path.join(extracted_dir, item)
                d = os.path.join(self.projectpath, item)
                
                if os.path.exists(d):
                    if os.path.isdir(d):
                        shutil.rmtree(d)
                    else:
                        os.remove(d)
                
                if os.path.isdir(s):
                    shutil.copytree(s, d)
                else:
                    shutil.copy2(s, d)

            self.log.log('Проект успешно обновлен', logging.INFO, 'main.py')

        except Exception as e:
            self.log.log(f'Ошибка при обновлении проекта: {str(e)}', logging.ERROR, 'main.py')
            # В случае ошибки восстанавливаем из резервной копии
            if 'backup_path' in locals():
                self.log.log('Восстановление из резервной копии...', logging.WARNING, 'main.py')
                shutil.rmtree(self.projectpath)
                shutil.copytree(backup_path, self.projectpath)
            raise
        finally:
            # Очистка временных файлов
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)

    def get_latest_commit_info(self):
        """Получение информации о последнем коммите"""
        try:
            api_url = f"https://api.github.com/repos/{self.repo_url}/commits/{self.branch}"
            response = requests.get(api_url)
            response.raise_for_status()
            commit_info = response.json()
            
            info = {
                'sha': commit_info['sha'],
                'author': commit_info['commit']['author']['name'],
                'date': commit_info['commit']['author']['date'],
                'message': commit_info['commit']['message']
            }
            
            self.log.log(f'Получена информация о последнем коммите: {info}', logging.INFO, 'main.py')
            return info

        except requests.exceptions.RequestException as e:
            self.log.log(f'Ошибка при получении информации о коммите: {str(e)}', logging.ERROR, 'main.py')
            raise
