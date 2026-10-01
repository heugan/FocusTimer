# Builds dist\Pomodoro.exe (requires: pip install pyinstaller)
Set-Location $PSScriptRoot
py -m PyInstaller --onefile --windowed --name Pomodoro pomodoro.py
