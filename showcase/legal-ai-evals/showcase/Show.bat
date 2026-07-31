@echo off
title Legal Reasoning Evals Showcase
cd /d "%~dp0"

echo.
echo  Legal Reasoning Evals - Showcase
echo  --------------------------------
echo  Starting at http://127.0.0.1:8780
echo  Press Ctrl+C to stop.
echo.

start "" "http://127.0.0.1:8780"

py -3 -m http.server 8780
if errorlevel 1 (
  echo.
  echo Could not start. Try: py -3 --version
  pause
)