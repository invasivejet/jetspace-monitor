@echo off
wsl -d Ubuntu -e bash -lc "bash /mnt/c/Users/joela/jetspace-monitor/scripts/wsl-modal-network-diagnose.sh"
explorer.exe C:\Users\joela\jetspace-monitor\reports
