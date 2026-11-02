@echo off
setlocal
echo ===================================================
echo  Starting Timetable & Exam Scheduling Optimizer
echo ===================================================

:: Ensure C++ engine is built
if not exist "cpp\scheduler.exe" (
    echo Building C++ scheduler engine...
    call build.bat
    if errorlevel 1 (
        echo [ERROR] Failed to compile C++ engine.
        pause
        exit /b 1
    )
)

:: Find Python
set "PY_CMD="
if exist "C:\Users\iamsu\AppData\Local\Programs\Python311\python.exe" (
    set "PY_CMD=C:\Users\iamsu\AppData\Local\Programs\Python311\python.exe"
) else (
    where python >nul 2>&1
    if not errorlevel 1 (
        set "PY_CMD=python"
    ) else (
        where py >nul 2>&1
        if not errorlevel 1 (
            set "PY_CMD=py"
        )
    )
)

if "%PY_CMD%"=="" (
    echo [ERROR] Python not found on system.
    pause
    exit /b 1
)

echo Using Python: %PY_CMD%
echo Launching Flask application at http://127.0.0.1:5000 ...
"%PY_CMD%" app.py

pause
