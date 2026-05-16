@echo off
REM ============================================================================
REM Story Teller Bot - Windows launcher
REM
REM Usage:
REM   run.bat                          Interactive menu (audio / text / continue)
REM   run.bat --text "king and lion"  One-shot generation from text
REM   run.bat --text "..." --no-play  Generate without speaking
REM   run.bat help                     Show this help
REM ============================================================================

setlocal

REM --- Resolve project root from this script's location ----------------------
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

REM --- Show help -------------------------------------------------------------
if /i "%~1"=="help"   goto :show_help
if /i "%~1"=="--help" goto :show_help
if /i "%~1"=="-h"     goto :show_help

REM --- Pick Python: prefer the project venv ----------------------------------
set "VENV_PY=%PROJECT_ROOT%.venv\Scripts\python.exe"

if exist "%VENV_PY%" (
    set "PYTHON=%VENV_PY%"
) else (
    echo [warn] No .venv found at %VENV_PY%
    echo [warn] Falling back to system Python. Create the venv with:
    echo            python -m venv .venv
    echo            .venv\Scripts\activate
    echo            pip install -r requirements.txt
    echo            python -m spacy download en_core_web_sm
    echo.
    set "PYTHON=python"
)

REM --- Make Kokoro TTS find espeak-ng if installed in the default location ---
if not defined PHONEMIZER_ESPEAK_LIBRARY (
    if exist "C:\Program Files\eSpeak NG\libespeak-ng.dll" (
        set "PHONEMIZER_ESPEAK_LIBRARY=C:\Program Files\eSpeak NG\libespeak-ng.dll"
    )
)

REM --- Run the bot, forwarding all args --------------------------------------
echo ============================================================
echo  Story Teller Bot
echo  Python : %PYTHON%
echo  Args   : %*
echo ============================================================
echo.

"%PYTHON%" -m src.bot %*
set "EXITCODE=%ERRORLEVEL%"

if not "%EXITCODE%"=="0" (
    echo.
    echo [error] Bot exited with code %EXITCODE%.
)

endlocal & exit /b %EXITCODE%

REM ---------------------------------------------------------------------------
:show_help
echo.
echo Story Teller Bot - Windows launcher
echo.
echo Usage:
echo   run.bat                              Interactive menu
echo   run.bat --text "your story idea"    Non-interactive generation
echo   run.bat --text "..." --no-play      Generate without TTS playback
echo   run.bat help                         Show this help
echo.
echo Examples:
echo   run.bat
echo   run.bat --text "a brave knight and a friendly dragon"
echo   run.bat --text "princess and a unicorn" --no-play
echo.
endlocal & exit /b 0
