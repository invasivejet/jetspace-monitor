@echo off
REM Use when PowerShell breaks git commit (trailer injection). Edit message inside WSL heredoc if needed.
wsl bash -c "cd /mnt/c/Users/joela/jetspace-monitor && export GIT_EDITOR=true && git add -A && git status && git diff --cached --stat && git commit -m 'docs: PowerShell git commit workaround in PRIVATE-REPO' && git push origin main && git push joel-saucedo main"
