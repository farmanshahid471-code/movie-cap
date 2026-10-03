@echo off
REM ===========================================================
REM  NarratoAI - fix-max-tokens.bat
REM
REM  Fixes: "Unsupported parameter: 'max_tokens' is not supported
REM  with this model. Use 'max_completion_tokens' instead."
REM
REM  Only needed if you use an o-series or gpt-5 model.
REM  Put this file (and fix_max_completion_tokens.py) next to webui.py.
REM ===========================================================

REM --- keep this window open no matter what happens below ---
if /i not "%~1"=="__keepalive__" (
    cmd /k call "%~f0" __keepalive__
    exit /b
)

setlocal
chcp 65001 >nul
title NarratoAI - fix max_tokens
cd /d "%~dp0"

set "ROOT=%~dp0"
set "ROOT=%ROOT:~0,-1%"
set "VPY=%ROOT%\.venv\Scripts\python.exe"

echo.
echo ===========================================================
echo    NarratoAI - max_tokens compatibility fix
echo ===========================================================
echo.

if not exist "%ROOT%\webui.py" goto :err_wrong_folder
if not exist "%ROOT%\fix_max_completion_tokens.py" goto :err_missing_script
if not exist "%VPY%" goto :err_not_installed

"%VPY%" "%ROOT%\fix_max_completion_tokens.py"
if errorlevel 1 goto :err_failed

echo.
echo -----------------------------------------------------------
echo    Next step: close NarratoAI and start it again with start.bat
echo    Alternatively set "Max Output Tokens" to 0 in the app,
echo    which also avoids the error.
echo -----------------------------------------------------------
echo.
pause
exit /b 0

:err_wrong_folder
echo [ERROR] webui.py was not found in this folder.
echo.
echo         Put fix-max-tokens.bat NEXT TO webui.py, then run it again.
echo.
pause
exit /b 1

:err_missing_script
echo [ERROR] fix_max_completion_tokens.py was not found next to this file.
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
echo        No problem - use this instead, it needs no patching:
echo          In the app, open Basic Settings, then set
echo          "Max Output Tokens" to 0 for BOTH model panels.
echo          That stops the app from sending max_tokens at all.
echo.
pause
exit /b 1
