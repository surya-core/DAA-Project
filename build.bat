@echo off
echo Compiling C++ scheduling engine...
g++ -std=c++17 -O2 -Wall -static -static-libgcc -static-libstdc++ -o cpp/scheduler.exe cpp/main.cpp cpp/csv_io.cpp cpp/conflict.cpp cpp/timetable.cpp cpp/exam.cpp cpp/report.cpp
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Build successful: cpp/scheduler.exe created.
) else (
    echo [ERROR] Build failed with error code %ERRORLEVEL%.
    exit /b %ERRORLEVEL%
)
