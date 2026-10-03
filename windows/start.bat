@echo off
REM ===========================================================
REM  NarratoAI - start.bat
REM
REM  Starts the NarratoAI web interface.
REM  Run update-windows.bat once before using this the first time.
REM ===========================================================

REM --- keep this window open no matter what happens below ---
if /i not "%~1"=="__keepalive__" (
    cmd /k call "%~f0" __keepalive__
    exit /b
)

setlocal
chcp 65001 >nul
title NarratoAI
cd /d "%~dp0"

set "ROOT=%~dp0"
set "ROOT=%ROOT:~0,-1%"

echo.
echo ===========================================================
echo    NarratoAI
echo ===========================================================
echo.

if not exist "%ROOT%\webui.py" goto :err_wrong_folder

REM --- keep temporary files on this drive, not on C: ---
if not exist "%ROOT%\runtime\temp" mkdir "%ROOT%\runtime\temp" >nul 2>nul
set "TEMP=%ROOT%\runtime\temp"
set "TMP=%ROOT%\runtime\temp"
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

set "VPY=%ROOT%\.venv\Scripts\python.exe"
if not exist "%VPY%" goto :err_not_installed

"%VPY%" -c "import streamlit" >nul 2>nul
if errorlevel 1 goto :err_not_installed

REM --- make the bundled FFmpeg available to this session ---
if exist "%ROOT%\tools\ffmpeg\bin\ffmpeg.exe" set "PATH=%ROOT%\tools\ffmpeg\bin;%PATH%"

echo   Starting NarratoAI. Please wait a few seconds.
echo.
echo   The app opens automatically in your browser at:
echo       http://localhost:8501
echo.
echo   Keep THIS window open while you use NarratoAI.
echo   Press Ctrl+C here ^(or close this window^) to stop the app.
echo   If the browser shows an error, wait 5 seconds and reload the page,
echo   or use the "Local URL" printed below.
echo.
echo -----------------------------------------------------------

REM --- open the browser a few seconds from now, once the app is up ---
start "" powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 10; Start-Process 'http://localhost:8501'"

"%VPY%" -m streamlit run webui.py --server.maxUploadSize=2048 --server.headless=true --browser.gatherUsageStats=false

echo.
echo -----------------------------------------------------------
echo   NarratoAI has stopped.
echo.
pause
exit /b 0

:err_wrong_folder
echo [ERROR] webui.py was not found in this folder.
echo.
echo         Put start.bat NEXT TO webui.py ^(the folder that contains
echo         app, webui and webui.py^), then run it again.
echo.
pause
exit /b 1

:err_not_installed
echo [ERROR] NarratoAI is not installed yet, or the install is incomplete.
echo.
echo         Double-click  update-windows.bat  first, and wait until it
echo         says "Installation complete". Then run start.bat.
echo.
pause
exit /b 1
