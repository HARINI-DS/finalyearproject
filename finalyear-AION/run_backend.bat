@echo off
setlocal
set "PYTHON_EXE=C:\Users\jayas\AppData\Local\Programs\Python\Python311\python.exe"
cd /d "%~dp0"
"%PYTHON_EXE%" -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
