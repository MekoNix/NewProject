@echo off
chcp 65001 > nul
@echo:Первоначальная настройка

rem Определение текущей директории
set "SCRIPT_DIR=%~dp0"

rem Спросить пользователя, хочет ли он установить модули
set /p install=Начать установку? (y/n, нажмите Enter для "y"):
if "%install%"=="" set install=y
if "%install%"=="y" goto install
if "%install%"=="n" goto end
goto end

:install
@echo Обновление pip
@python -m pip install --upgrade pip
@echo Установка модулей
@pip install -r "%SCRIPT_DIR%requirements.txt"
@mkdir "%SCRIPT_DIR%logs" 2>nul
@cls
@echo Запуск программы
ping localhost -n 5 >nul

@python "%SCRIPT_DIR%modules\FirstStart.py"

:end
 
@echo:Нажмите любую клавишу, чтобы закрыть окно...
pause > nul