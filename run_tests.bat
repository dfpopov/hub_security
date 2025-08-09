@echo off
REM Test runner script for the Book Collection API (Windows)
REM Usage: run_tests.bat [option]

setlocal enabledelayedexpansion

REM Default action
if "%1"=="" (
    echo [INFO] No option specified. Running all tests...
    docker-compose exec api pytest tests/ -v
    exit /b %errorlevel%
)

REM Parse command line arguments
if "%1"=="all" goto :all
if "%1"=="full" goto :all
if "%1"=="fast" goto :fast
if "%1"=="quick" goto :fast
if "%1"=="auth" goto :auth
if "%1"=="authors" goto :authors
if "%1"=="books" goto :books
if "%1"=="coverage" goto :coverage
if "%1"=="timing" goto :timing
if "%1"=="performance" goto :performance
if "%1"=="load" goto :load
if "%1"=="parallel" goto :parallel
if "%1"=="debug" goto :debug
if "%1"=="clean" goto :clean
if "%1"=="setup" goto :setup
if "%1"=="help" goto :help
if "%1"=="-h" goto :help
if "%1"=="--help" goto :help
goto :unknown

:all
echo [INFO] Running all tests with coverage...
set start_time=%time%
docker-compose exec api pytest tests/ -v --cov=app --cov-report=term-missing
set end_time=%time%
echo [INFO] ⏱️  Execution time: %start_time% to %end_time%
goto :end

:fast
echo [INFO] Running quick tests (no coverage)...
set start_time=%time%
docker-compose exec api pytest tests/ -v -x
set end_time=%time%
echo [INFO] ⏱️  Execution time: %start_time% to %end_time%
goto :end

:auth
echo [INFO] Running authentication tests...
set start_time=%time%
docker-compose exec api pytest tests/test_auth.py -v
set end_time=%time%
echo [INFO] ⏱️  Execution time: %start_time% to %end_time%
goto :end

:authors
echo [INFO] Running author tests...
set start_time=%time%
docker-compose exec api pytest tests/test_authors.py -v
set end_time=%time%
echo [INFO] ⏱️  Execution time: %start_time% to %end_time%
goto :end

:books
echo [INFO] Running book tests...
set start_time=%time%
docker-compose exec api pytest tests/test_books.py -v
set end_time=%time%
echo [INFO] ⏱️  Execution time: %start_time% to %end_time%
goto :end

:coverage
echo [INFO] Running tests with detailed coverage report...
set start_time=%time%
docker-compose exec api pytest tests/ --cov=app --cov-report=html --cov-report=term-missing
set end_time=%time%
echo [INFO] ⏱️  Execution time: %start_time% to %end_time%
echo [INFO] Coverage report generated in htmlcov/index.html
goto :end

:timing
echo [INFO] Running tests with detailed timing analysis...
set start_time=%time%
docker-compose exec api pytest tests/ -v --durations=20 --durations-min=0.05
set end_time=%time%
echo [INFO] ⏱️  Execution time: %start_time% to %end_time%
goto :end

:performance
echo [INFO] Running performance tests...
set start_time=%time%
docker-compose exec api pytest tests/test_performance.py -v --durations=10
set end_time=%time%
echo [INFO] ⏱️  Execution time: %start_time% to %end_time%
goto :end

:load
echo [INFO] Running load tests...
set start_time=%time%
docker-compose exec api pytest tests/test_performance.py::TestLoadTesting -v --durations=10
set end_time=%time%
echo [INFO] ⏱️  Execution time: %start_time% to %end_time%
goto :end

:parallel
echo [INFO] Running tests in parallel...
docker-compose exec api pytest tests/ -n auto -v
goto :end

:debug
echo [INFO] Running tests with debug output...
docker-compose exec api pytest tests/ -v -s --tb=long
goto :end

:clean
echo [INFO] Cleaning up test artifacts...
docker-compose down -v
docker system prune -f
echo [SUCCESS] Cleanup completed!
goto :end

:setup
echo [INFO] Setting up test environment...
docker-compose down -v
docker-compose up -d
echo [INFO] Waiting for services to be ready...
timeout /t 10 /nobreak >nul
echo [SUCCESS] Test environment setup completed!
goto :end

:help
echo Book Collection API Test Runner
echo ================================
echo.
echo Usage: run_tests.bat [option]
echo.
echo Options:
echo   all, full     - Run all tests with coverage
echo   fast, quick   - Run tests quickly (stop on first failure)
echo   auth          - Run only authentication tests
echo   authors       - Run only author tests
echo   books         - Run only book tests
echo   coverage      - Run tests with detailed coverage report
echo   timing        - Run tests with detailed timing analysis
echo   performance   - Run performance tests
echo   load          - Run load tests
echo   parallel      - Run tests in parallel
echo   debug         - Run tests with debug output
echo   clean         - Clean up test artifacts
echo   setup         - Setup test environment
echo   help          - Show this help message
echo.
echo Examples:
echo   run_tests.bat          # Run all tests
echo   run_tests.bat auth     # Run only auth tests
echo   run_tests.bat coverage # Run with coverage report
echo.
goto :end

:unknown
echo [ERROR] Unknown option: %1
echo Use 'run_tests.bat help' for usage information.
exit /b 1

:end
exit /b %errorlevel%
