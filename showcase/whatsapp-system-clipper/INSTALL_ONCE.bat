@echo off
setlocal
cd /d "%~dp0"

echo.
echo === Clip for WhatsApp — one-time setup (Practic-AI) ===
echo.

where py >nul 2>&1
if %errorlevel%==0 goto :use_py
where python >nul 2>&1
if %errorlevel%==0 goto :use_python
echo Python not found. Install Python 3.11+ from https://www.python.org/
pause
exit /b 1

:use_py
if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment...
  py -3 -m venv .venv
  if errorlevel 1 (
    echo Failed to create venv.
    pause
    exit /b 1
  )
)
goto :install

:use_python
if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment...
  python -m venv .venv
  if errorlevel 1 (
    echo Failed to create venv.
    pause
    exit /b 1
  )
)
goto :install

:install
echo Installing packages (once)...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo Install failed.
  pause
  exit /b 1
)

echo.
echo Done. Next times: double-click RECORD.bat only.
echo Clips save to: %~dp0clips
echo.
pause
