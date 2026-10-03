@echo off
REM ===========================================================
REM  NarratoAI - fix-ffmpeg-audio-merge.bat
REM
REM  Fixes: the finished recap has narration and subtitles only -
REM  the film's own dialogue, music and sound effects are missing.
REM
REM  Cause: the app asks ffmpeg for an option that new ffmpeg
REM  builds removed, then silently falls back to an audio-less
REM  merge. The log shows:
REM      Unrecognized option 'filter_complex_script'
REM      then a Chinese "fallback merge WITHOUT audio" warning
REM      and later a Chinese "video has no audio track" warning.
REM
REM  Put this file (and fix_ffmpeg_filter_options.py) next to webui.py.
REM ===========================================================

REM --- keep this window open no matter what happens below ---
if /i not "%~1"=="__keepalive__" (
    cmd /k call "%~f0" __keepalive__
    exit /b
)

setlocal
chcp 65001 >nul
title NarratoAI - fix missing original audio
cd /d "%~dp0"

set "ROOT=%~dp0"
set "ROOT=%ROOT:~0,-1%"
set "VPY=%ROOT%\.venv\Scripts\python.exe"

echo.
echo ===========================================================
echo    NarratoAI - fix missing original audio
echo ===========================================================
echo.

if not exist "%ROOT%\webui.py" goto :err_wrong_folder
if not exist "%ROOT%\fix_ffmpeg_filter_options.py" goto :err_missing_script
if not exist "%VPY%" goto :err_not_installed

"%VPY%" "%ROOT%\fix_ffmpeg_filter_options.py"
if errorlevel 1 goto :err_failed

echo.
echo -----------------------------------------------------------
echo    Next step: close NarratoAI and start it again with start.bat
echo    Then render your movie again. The film's own audio will be
echo    back under the narration.
echo.
echo    To check it worked, the log should now show that the audio
echo    was mixed and that the final merge finished. It should NOT
echo    contain the Chinese warning about merging without audio,
echo    and it should NOT say the video has no audio track.
echo    MOVIE-RECAP-SETTINGS.md lists those exact messages.
echo -----------------------------------------------------------
echo.
pause
exit /b 0

:err_wrong_folder
echo [ERROR] webui.py was not found in this folder.
echo.
echo         Put fix-ffmpeg-audio-merge.bat NEXT TO webui.py, then run it again.
echo.
pause
exit /b 1

:err_missing_script
echo [ERROR] fix_ffmpeg_filter_options.py was not found next to this file.
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

:err_failed
echo.
echo [WARN] The patch did not apply. Your files were NOT modified.
echo.
echo        Please send the text above so the patch can be updated.
echo        Your project files are untouched and still work as before.
echo.
pause
exit /b 1
