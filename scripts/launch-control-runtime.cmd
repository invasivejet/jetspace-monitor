@echo off
cd /d "C:\Users\joela\jetspace-monitor\backend"
start "Jetspace Control API" /min powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ".\.venv\Scripts\python -m uvicorn app:app --host 127.0.0.1 --port 8010"
start "Jetspace Hotkey" /min powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Users\joela\jetspace-monitor\scripts\panel-hotkey-daemon.ps1"
