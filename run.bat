@echo off
:: Überprüfen, ob das Betriebssystem Windows 11 ist
ver | findstr /i "10.0.22000" >nul
if %errorlevel% equ 0 (
    :: Windows 11 erkannt - Skript mit Administratorrechten ausführen
    echo Dieses Skript erfordert Administratorrechte. Bitte gewähren Sie die Administratorrechte.
    powershell -Command "Start-Process python -ArgumentList 'main.py' -Verb RunAs"
) else (
    :: Windows 10 oder älter - Skript ohne Administratorrechte ausführen
    py main.py
)

echo Thanks for using Pytube
pause
