@echo off
wsl -d Ubuntu -e bash -lc "bash /mnt/c/Users/joela/jetspace-monitor/scripts/wsl-harmony-audit.sh"
explorer.exe C:\Users\joela\jetspace-monitor\reports
