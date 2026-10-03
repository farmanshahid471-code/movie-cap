@echo off
REM ===========================================================
REM  NarratoAI - update-windows.bat
REM
REM  Installs everything NarratoAI needs INSIDE THIS FOLDER,
REM  so nothing large is written to drive C:.
REM
REM  Usage: put this file NEXT TO webui.py, then double-click it.
REM ===========================================================

REM --- keep this window open no matter what happens below ---
if /i not "%~1"=="__keepalive__" (
    cmd /k call "%~f0" __keepalive__
    exit /b
)

setlocal
chcp 65001 >nul
title NarratoAI - installer
cd /d "%~dp0"

set "ROOT=%~dp0"
set "ROOT=%ROOT:~0,-1%"

echo.
echo ===========================================================
echo    NarratoAI - installer
echo ===========================================================
echo.
echo   Folder: %ROOT%
echo   Everything is installed inside this folder, so drive C:
echo   only receives a few tiny files. Expect roughly 3 GB of usage
echo   in this folder after everything is downloaded.
echo.

if not exist "%ROOT%\webui.py" goto :err_wrong_folder

REM --- keep temp files, caches and downloads on this drive ---
if not exist "%ROOT%\runtime\temp" mkdir "%ROOT%\runtime\temp" >nul 2>nul
if not exist "%ROOT%\runtime\downloads" mkdir "%ROOT%\runtime\downloads" >nul 2>nul
if not exist "%ROOT%\tools" mkdir "%ROOT%\tools" >nul 2>nul
set "TEMP=%ROOT%\runtime\temp"
set "TMP=%ROOT%\runtime\temp"
set "PIP_CACHE_DIR=%ROOT%\.pip-cache"
set "UV_CACHE_DIR=%ROOT%\.uv-cache"
set "UV_PYTHON_INSTALL_DIR=%ROOT%\runtime\python"
set "UV_NO_MODIFY_PATH=1"
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

set "VPY=%ROOT%\.venv\Scripts\python.exe"
set "UV=%ROOT%\tools\uv\uv.exe"
set "FRESH="
set "USE_UV="

REM ===========================================================
REM  STEP 1 - Python
REM ===========================================================
echo [1/5] Python
echo -----------------------------------------------------------
if exist "%VPY%" goto :step2

if not exist "%UV%" call :install_uv
if not exist "%UV%" (
    for /f "delims=" %%F in ('dir /b /s "%ROOT%\tools\uv\uv.exe" 2^>nul') do set "UV=%%F"
)

if not exist "%UV%" goto :try_system_python

echo       Installing Python 3.12 with uv ...
"%UV%" python install 3.12
if errorlevel 1 goto :try_system_python

echo       Creating the virtual environment .venv ...
"%UV%" venv --seed --python 3.12 "%ROOT%\.venv"
if errorlevel 1 goto :try_system_python
if not exist "%VPY%" goto :try_system_python

set "USE_UV=1"
echo       Python is ready.
goto :step2

:try_system_python
echo       uv was not available - looking for an existing Python 3.12+ ...
call :find_system_python
if not defined SYSPY goto :err_no_python
echo       Found: %SYSPY%
%SYSPY% -m venv "%ROOT%\.venv"
if errorlevel 1 goto :err_no_python
if not exist "%VPY%" goto :err_no_python
echo       Python is ready.

REM ===========================================================
REM  STEP 2 - Python packages
REM ===========================================================
:step2
echo.
echo [2/5] Python packages
echo -----------------------------------------------------------
if not exist "%VPY%" goto :err_no_python

if defined USE_UV goto :deps_uv
"%VPY%" -m pip --version >nul 2>nul
if errorlevel 1 goto :deps_uv
goto :deps_pip

:deps_uv
if not exist "%UV%" (
    for /f "delims=" %%F in ('dir /b /s "%ROOT%\tools\uv\uv.exe" 2^>nul') do set "UV=%%F"
)
if not exist "%UV%" goto :deps_pip
echo       Installing packages with uv. This downloads roughly 500 MB, so
echo       it can take 5 to 20 minutes depending on your internet speed.
"%UV%" pip install -r "%ROOT%\requirements.txt" --python "%VPY%"
if errorlevel 1 goto :deps_pip
goto :deps_check

:deps_pip
echo       Installing packages with pip. This downloads roughly 500 MB, so
echo       it can take 5 to 20 minutes depending on your internet speed.
"%VPY%" -m pip install --upgrade pip setuptools wheel
"%VPY%" -m pip install -r "%ROOT%\requirements.txt"
if errorlevel 1 goto :err_deps

:deps_check
echo       Checking the installation ...
"%VPY%" -c "import streamlit, moviepy, edge_tts, openai" >nul 2>nul
if errorlevel 1 goto :err_deps
echo       Python packages are ready.

REM ===========================================================
REM  STEP 3 - FFmpeg
REM ===========================================================
:step3
echo.
echo [3/5] FFmpeg
echo -----------------------------------------------------------
if exist "%ROOT%\tools\ffmpeg\bin\ffmpeg.exe" goto :step3_done
echo       Downloading FFmpeg - about 200 MB, one time only ...
call :download "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip" "%ROOT%\runtime\downloads\ffmpeg.zip" "FFmpeg"
if errorlevel 1 goto :err_ffmpeg
echo       Unpacking FFmpeg ...
call :unzip "%ROOT%\runtime\downloads\ffmpeg.zip" "%ROOT%\runtime\downloads\ffmpeg"
if errorlevel 1 goto :err_ffmpeg
set "FFSRC="
for /d %%D in ("%ROOT%\runtime\downloads\ffmpeg\*") do if exist "%%~fD\bin\ffmpeg.exe" set "FFSRC=%%~fD"
if not defined FFSRC goto :err_ffmpeg
if exist "%ROOT%\tools\ffmpeg" rmdir /s /q "%ROOT%\tools\ffmpeg" >nul 2>nul
move "%FFSRC%" "%ROOT%\tools\ffmpeg" >nul
if not exist "%ROOT%\tools\ffmpeg\bin\ffmpeg.exe" goto :err_ffmpeg
if exist "%ROOT%\runtime\downloads\ffmpeg.zip" del /f /q "%ROOT%\runtime\downloads\ffmpeg.zip" >nul 2>nul
:step3_done
echo       FFmpeg is ready.

REM ===========================================================
REM  STEP 4 - settings
REM ===========================================================
:step4
echo.
echo [4/5] Settings
echo -----------------------------------------------------------
if exist "%ROOT%\config.toml" goto :cfg_repeat
copy /y "%ROOT%\config.example.toml" "%ROOT%\config.toml" >nul
echo       Created config.toml
set "FRESH=1"

if not exist "%ROOT%\narrato_setup_helper.py" goto :step4b
if not defined FRESH goto :cfg_repeat
"%VPY%" "%ROOT%\narrato_setup_helper.py" --config "%ROOT%\config.toml" --first-run-english --ffmpeg-path "%ROOT%\tools\ffmpeg\bin\ffmpeg.exe"
if errorlevel 1 echo       [WARN] Could not update config.toml automatically.
goto :step4b

:cfg_repeat
if not exist "%ROOT%\narrato_setup_helper.py" goto :step4b
"%VPY%" "%ROOT%\narrato_setup_helper.py" --config "%ROOT%\config.toml" --ensure-language --ffmpeg-path "%ROOT%\tools\ffmpeg\bin\ffmpeg.exe"
if errorlevel 1 echo       [WARN] Could not update config.toml automatically.

REM ===========================================================
REM  STEP 4b - ffmpeg compatibility patch
REM  New ffmpeg builds removed an option NarratoAI still uses, which
REM  silently drops the film's original audio. This fixes the app.
REM ===========================================================
:step4b
if not exist "%ROOT%\fix_ffmpeg_filter_options.py" goto :step5
echo.
echo [4/5] ffmpeg compatibility fix
echo -----------------------------------------------------------
"%VPY%" "%ROOT%\fix_ffmpeg_filter_options.py"
if errorlevel 1 echo       [WARN] Could not apply the ffmpeg audio fix right now.
if errorlevel 1 echo              Run fix-ffmpeg-audio-merge.bat later, before rendering.

REM ===========================================================
REM  STEP 5 - summary
REM ===========================================================
:step5
echo.
echo [5/5] Finished
echo -----------------------------------------------------------
echo.
echo ===========================================================
echo    Installation complete
echo ===========================================================
echo.
echo    NEXT: double-click  start.bat  to run NarratoAI.
echo.
echo    This window was kept open on purpose, so you can read any
echo    errors. You can close it now.
echo.
echo    Note: an ffmpeg audio fix was applied automatically so the
echo    film's own audio stays under the narration.
echo.
echo    Inside the app, remember to set:
echo      - Narration Language  :  English ^(United States^)
echo      - Voice-over engine   :  Edge TTS  -^>  English Female Voice
echo      - And add your LLM API key in Basic Settings.
echo.
echo ===========================================================
echo.
pause
exit /b 0

REM ===========================================================
REM  ERROR HANDLERS
REM ===========================================================
:err_wrong_folder
echo.
echo [ERROR] webui.py was not found in this folder.
echo.
echo         Put update-windows.bat and start.bat NEXT TO webui.py
echo         ^(the folder that contains app, webui and webui.py^),
echo         then run this file again.
echo.
pause
exit /b 1

:err_no_python
echo.
echo [ERROR] Python 3.12 or newer is required and could not be installed.
echo.
echo         Quickest fix: install Python 3.12 by hand from
echo             https://www.python.org/downloads/windows/
echo         On the first installer screen, TICK "Add python.exe to PATH",
echo         then run update-windows.bat again.
echo.
pause
exit /b 1

:err_deps
echo.
echo [ERROR] Installing the Python packages failed.
echo.
echo         Most common causes:
echo           - no internet access, or a proxy / firewall is blocking
echo           - the download was interrupted - just run this file again
echo.
echo         You can also open a Command Prompt in this folder and run:
echo             .venv\Scripts\python.exe -m pip install -r requirements.txt
echo.
pause
exit /b 1

:err_ffmpeg
echo.
echo [WARN] FFmpeg could not be installed automatically.
echo.
echo        NarratoAI will still start, but cutting videos and burning
echo        subtitles will fail until FFmpeg is available.
echo.
echo        To fix it later, download this file and unzip it into
echo        tools\ffmpeg so that tools\ffmpeg\bin\ffmpeg.exe exists:
echo          https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
echo.
goto :step4

REM ===========================================================
REM  SUBROUTINES
REM ===========================================================

:install_uv
echo       Downloading uv - a small and fast Python installer, about 18 MB ...
call :download "https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip" "%ROOT%\runtime\downloads\uv.zip" "uv"
if errorlevel 1 exit /b 1
echo       Unpacking uv ...
call :unzip "%ROOT%\runtime\downloads\uv.zip" "%ROOT%\tools\uv"
if errorlevel 1 exit /b 1
if exist "%ROOT%\runtime\downloads\uv.zip" del /f /q "%ROOT%\runtime\downloads\uv.zip" >nul 2>nul
exit /b 0

:find_system_python
set "SYSPY="
py -3.12 -c "import sys" >nul 2>nul && set "SYSPY=py -3.12"
if defined SYSPY exit /b 0
py -3.13 -c "import sys" >nul 2>nul && set "SYSPY=py -3.13"
if defined SYSPY exit /b 0
py -3 -c "import sys; sys.exit(0 if sys.version_info>=(3,12) else 1)" >nul 2>nul && set "SYSPY=py -3"
if defined SYSPY exit /b 0
python -c "import sys; sys.exit(0 if sys.version_info>=(3,12) else 1)" >nul 2>nul && set "SYSPY=python"
exit /b 0

:download
REM  %1 = url, %2 = destination file, %3 = label
set "DL_URL=%~1"
set "DL_DEST=%~2"
if exist "%DL_DEST%" del /f /q "%DL_DEST%" >nul 2>nul
echo       Downloading %~3 ...
if not exist "%SystemRoot%\System32\curl.exe" goto :download_ps
"%SystemRoot%\System32\curl.exe" -L --fail --retry 3 --retry-delay 2 --connect-timeout 30 -o "%DL_DEST%" "%DL_URL%"
if errorlevel 1 goto :download_ps
if not exist "%DL_DEST%" goto :download_ps
for %%A in ("%DL_DEST%") do if %%~zA LSS 1000 goto :download_ps
echo       Downloaded %~3 OK.
exit /b 0

:download_ps
echo       Retrying the download with PowerShell ...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ProgressPreference='SilentlyContinue'; try { [Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%DL_URL%' -OutFile '%DL_DEST%' -UseBasicParsing; exit 0 } catch { Write-Host $_.Exception.Message; exit 1 }"
if errorlevel 1 exit /b 1
if not exist "%DL_DEST%" exit /b 1
for %%A in ("%DL_DEST%") do if %%~zA LSS 1000 exit /b 1
exit /b 0

:unzip
REM  %1 = zip file, %2 = destination folder
if not exist "%~2" mkdir "%~2" >nul 2>nul
where tar >nul 2>nul
if errorlevel 1 goto :unzip_ps
tar -xf "%~1" -C "%~2"
if not errorlevel 1 exit /b 0

:unzip_ps
echo       Using PowerShell to unpack ...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ProgressPreference='SilentlyContinue'; try { Expand-Archive -LiteralPath '%~1' -DestinationPath '%~2' -Force; exit 0 } catch { Write-Host $_.Exception.Message; exit 1 }"
if errorlevel 1 exit /b 1
exit /b 0
