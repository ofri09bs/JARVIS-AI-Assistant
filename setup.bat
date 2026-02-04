@echo off
setlocal
title Jarvis AI Assistant - Dedicated Environment Setup

set "ISOLATED_PYTHON_DIR=%USERPROFILE%\JarvisPythonEnv"
set "PYTHON_EXE=%ISOLATED_PYTHON_DIR%\python.exe"
set "PYTHON_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
set "INSTALLER_SCRIPT=installer.py"

echo ========================================================
echo      J.A.R.V.I.S  ISOLATED  ENV  SETUP (Python 3.11)
echo ========================================================
echo.

if exist "%PYTHON_EXE%" (
    echo [v] Dedicated Python 3.11 environment found.
    goto :RUN_SCRIPT
)

echo [!] Creating a dedicated Python 3.11 environment...
echo     (This will keep your main Python installation untouched)
echo.

echo [*] Downloading Python 3.11...
curl -o python_installer.exe %PYTHON_URL%

if not exist python_installer.exe (
    echo [x] Failed to download Python. Check internet connection.
    pause
    exit /b
)

echo [*] Installing local Python environment...
python_installer.exe /quiet InstallAllUsers=0 TargetDir="%ISOLATED_PYTHON_DIR%" PrependPath=0 Include_test=0 Include_tcltk=1 Include_pip=1


del python_installer.exe

echo [v] Environment created successfully!

:RUN_SCRIPT
echo.
echo [*] Launching Installer...
echo.

if not exist "%INSTALLER_SCRIPT%" (
    echo [x] Error: %INSTALLER_SCRIPT% not found!
    pause
    exit /b
)


set "PYTHONW_EXE=%ISOLATED_PYTHON_DIR%\pythonw.exe"

start "" "%PYTHONW_EXE%" "%INSTALLER_SCRIPT%"

exit