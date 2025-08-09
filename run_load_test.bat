@echo off
REM Load testing script using Locust (Windows)
REM Usage: run_load_test.bat [option]

setlocal enabledelayedexpansion

REM Default values
set USERS=10
set SPAWN_RATE=2
set RUNTIME=60
set HOST=http://localhost:8000

REM Parse command line arguments
if "%1"=="quick" goto :quick
if "%1"=="medium" goto :medium
if "%1"=="heavy" goto :heavy
if "%1"=="stress" goto :stress
if "%1"=="help" goto :help
if "%1"=="-h" goto :help
if "%1"=="--help" goto :help
goto :unknown

:quick
set USERS=5
set SPAWN_RATE=1
set RUNTIME=30
echo [INFO] Running quick load test: %USERS% users, %SPAWN_RATE%/s spawn rate, %RUNTIME%s runtime
goto :run_test

:medium
set USERS=20
set SPAWN_RATE=5
set RUNTIME=120
echo [INFO] Running medium load test: %USERS% users, %SPAWN_RATE%/s spawn rate, %RUNTIME%s runtime
goto :run_test

:heavy
set USERS=50
set SPAWN_RATE=10
set RUNTIME=300
echo [INFO] Running heavy load test: %USERS% users, %SPAWN_RATE%/s spawn rate, %RUNTIME%s runtime
goto :run_test

:stress
set USERS=100
set SPAWN_RATE=20
set RUNTIME=600
echo [INFO] Running stress test: %USERS% users, %SPAWN_RATE%/s spawn rate, %RUNTIME%s runtime
goto :run_test

:help
echo Load Testing Script for Book Collection API
echo ===========================================
echo.
echo Usage: run_load_test.bat [option]
echo.
echo Options:
echo   quick   - Quick test (5 users, 30s)
echo   medium  - Medium load (20 users, 2min)
echo   heavy   - Heavy load (50 users, 5min)
echo   stress  - Stress test (100 users, 10min)
echo   help    - Show this help message
echo.
echo Examples:
echo   run_load_test.bat quick   # Quick load test
echo   run_load_test.bat medium  # Medium load test
echo   run_load_test.bat stress  # Stress test
echo.
echo After running, open http://localhost:8089 to view results
echo.
goto :end

:unknown
echo [ERROR] Unknown option: %1
echo Use 'run_load_test.bat help' for usage information.
exit /b 1

:run_test
echo [INFO] Starting Locust load testing...
echo [INFO] Target: %HOST%
echo [INFO] Users: %USERS%
echo [INFO] Spawn rate: %SPAWN_RATE% users/second
echo [INFO] Runtime: %RUNTIME% seconds
echo.

REM Check if API is running
docker-compose ps api | findstr "Up" >nul
if errorlevel 1 (
    echo [WARNING] API service is not running. Starting services...
    docker-compose up -d
    echo [INFO] Waiting for API to be ready...
    timeout /t 10 /nobreak >nul
)

REM Run Locust
docker-compose exec api locust ^
    --host="%HOST%" ^
    --users="%USERS%" ^
    --spawn-rate="%SPAWN_RATE%" ^
    --run-time="%RUNTIME%s" ^
    --headless ^
    --html=load_test_report.html ^
    --csv=load_test_results ^
    --logfile=locust.log

echo [SUCCESS] Load test completed!
echo [INFO] Results saved to:
echo   - load_test_report.html (HTML report)
echo   - load_test_results.csv (CSV data)
echo   - locust.log (Log file)

:end
exit /b %errorlevel%
