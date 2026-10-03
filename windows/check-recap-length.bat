@echo off
REM ===========================================================
REM  NarratoAI - check-recap-length.bat
REM
REM  Tells you roughly how long the finished video will be,
REM  BEFORE you spend an hour rendering it.
REM
REM  Why: the length of the recap is decided by the editing
REM  script, not by the renderer. If the script holds only a few
REM  items you get a one-minute video no matter what else you set.
REM
REM  Put this file (and check_recap_length.py) next to webui.py.
REM  Run it after "Save Script" and before "Generate Video".
REM ===========================================================

REM --- keep this window open no matter what happens below ---
if /i not "%~1"=="__keepalive__" (
    cmd /k call "%~f0" __keepalive__ %*
    exit /b
)

setlocal
chcp 65001 >nul
title NarratoAI - recap length check
cd /d "%~dp0"

set "ROOT=%~dp0"
set "ROOT=%ROOT:~0,-1%"
set "VPY=%ROOT%\.venv\Scripts\python.exe"

echo.
echo ===========================================================
echo    NarratoAI - recap length check
echo ===========================================================
echo.

if not exist "%ROOT%\webui.py" goto :err_wrong_folder
if not exist "%ROOT%\check_recap_length.py" goto :err_missing_script
if not exist "%VPY%" goto :err_not_installed

REM only the first option is read; paths with spaces keep working
set "EXTRA="
if /i "%~2"=="--script" if not "%~3"=="" set "EXTRA=--script "%~3""
if /i "%~2"=="--target" if not "%~3"=="" set "EXTRA=--target %~3"
if /i "%~2"=="--wpm" if not "%~3"=="" set "EXTRA=--wpm %~3"

"%VPY%" "%ROOT%\check_recap_length.py" %EXTRA%

echo.
echo -----------------------------------------------------------
echo    Tip: a 15-minute recap needs roughly 100 to 200 items in
echo    the script. If the count is tiny, raise "Copy Length" and
echo    generate the script again before rendering.
echo -----------------------------------------------------------
echo.
pause
exit /b 0

:err_wrong_folder
echo [ERROR] webui.py was not found in this folder.
echo.
echo         Put check-recap-length.bat NEXT TO webui.py, then run it again.
echo.
pause
exit /b 1

:err_missing_script
echo [ERROR] check_recap_length.py was not found next to this file.
echo.
echo         Both files must sit in the same folder (next to webui.py).
echo.
pause
exit /b 1

:err_not_installed
echo [ERROR] The Python environment was not found at:
echo         %VPY%
echo.
echo         Run update-windows.bat first, then try again.
echo.
pause
exit /b 1
