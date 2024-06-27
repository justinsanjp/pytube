@echo off
setlocal

REM Python Installation
echo Installing Python...
set /p INSTALL_LOCATION="Enter installation location (e.g. C:\Python312): "
echo.
msiexec /i https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe

REM Clone Repository
echo.
echo Cloning pytube repository from GitHub...
git clone https://github.com/justinsanjp/pytube
cd pytube

REM Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt

REM Create desktop shortcut
echo.
set /p CREATE_DESKTOP_SHORTCUT="Create desktop shortcut? (Y/N): "
if /i "%CREATE_DESKTOP_SHORTCUT%"=="Y" (
    echo Creating desktop shortcut...
    echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
    echo sLinkFile = "%USERPROFILE%\Desktop\pytube.lnk" >> CreateShortcut.vbs
    echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
    echo oLink.TargetPath = "%CD%\pytube.bat" >> CreateShortcut.vbs
    echo oLink.Save >> CreateShortcut.vbs
    cscript /nologo CreateShortcut.vbs
    del CreateShortcut.vbs
)

REM Create start menu shortcut
echo.
set /p CREATE_STARTMENU_SHORTCUT="Create start menu shortcut? (Y/N): "
if /i "%CREATE_STARTMENU_SHORTCUT%"=="Y" (
    echo Creating start menu shortcut...
    set "SHORTCUT_NAME=pytube"
    set "SHORTCUT_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs"
    echo [InternetShortcut] > "%SHORTCUT_FOLDER%\%SHORTCUT_NAME%.url"
    echo URL=file://%CD%\pytube.bat >> "%SHORTCUT_FOLDER%\%SHORTCUT_NAME%.url"
)

REM Run pytube
echo.
set /p RUN_PYTUBE="Run pytube now? (Y/N): "
if /i "%RUN_PYTUBE%"=="Y" (
    echo Running pytube...
    start "" "%CD%\run.bat"
)

echo.
echo Setup complete.
pause
