@echo off
chcp 65001 >nul
title Dictado EN/ES (F8) - VozLocal
cd /d "D:\Hermes\dictation"
set PYTHONPATH=%CD%\src
".venv\Scripts\python.exe" -m vozlocal
echo.
echo [dictado] El proceso se detuvo.
pause >nul
