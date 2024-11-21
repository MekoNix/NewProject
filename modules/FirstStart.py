import os
from RepoManager import Base,GitHubUpdater
from Logger import Logger
import logging

class FirstStart(Base,GitHubUpdater,Logger):
    def __init__(self,repourl=None):
        Logger.__init__(self,make_log_folder=False)
        self.repourl = repourl

    def DeleteInstallationFiles(self): # Удаленние 
        InstallationFiles=["install.sh","install.bat","requirements.txt"]
        if os.path.exists(f"{self.FindProjectPath()}/logs"):
            self.EnableChatLog()
            self.log("Удаление установочных файлов...", logging.INFO,"FirstStart.py")
            
            for delfile in InstallationFiles:
                try:
                    self.log(f"Удаление {delfile}",logging.INFO,"FirstSart.py")
                    os.remove(delfile)
                except Exception as e:
                    self.log(f"Ошибка при удалении {delfile}: {str(e)}",logging.ERROR,"FirstStart.py")
            
            self.log("Удаление завершено, запуск приложения...", logging.INFO,"FirstStart.py")
            self.DisableChatLog()
        else:
            exit("""Папка logs не существует, если install.bat/install.sh есть в папке запустите сначала их, а после программу""")


    


