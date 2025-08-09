#!/bin/bash

# Test runner script for the Book Collection API
# Usage: ./run_tests.sh [option]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to run tests with timing
run_tests() {
    local test_command="$1"
    local test_name="$2"
    
    print_status "Running $test_name..."
    echo "Command: $test_command"
    echo "----------------------------------------"
    
    # Record start time
    start_time=$(date +%s.%N)
    
    if eval "$test_command"; then
        # Record end time and calculate duration
        end_time=$(date +%s.%N)
        duration=$(echo "$end_time - $start_time" | bc -l)
        
        print_success "$test_name completed successfully!"
        echo -e "${GREEN}⏱️  Execution time: ${duration%.3f} seconds${NC}"
    else
        # Record end time and calculate duration even if failed
        end_time=$(date +%s.%N)
        duration=$(echo "$end_time - $start_time" | bc -l)
        
        print_error "$test_name failed!"
        echo -e "${RED}⏱️  Execution time: ${duration%.3f} seconds${NC}"
        return 1
    fi
    echo "----------------------------------------"
    echo
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "docker-compose is not installed. Please install it and try again."
    exit 1
fi

# Default action
if [ $# -eq 0 ]; then
    print_status "No option specified. Running all tests..."
    TEST_COMMAND="docker-compose exec api pytest tests/ -v"
    run_tests "$TEST_COMMAND" "All Tests"
    exit 0
fi

# Parse command line arguments
case "$1" in
    "all"|"full")
        print_status "Running all tests with coverage..."
        TEST_COMMAND="docker-compose exec api pytest tests/ -v --cov=app --cov-report=term-missing"
        run_tests "$TEST_COMMAND" "All Tests with Coverage"
        ;;
    
    "fast"|"quick")
        print_status "Running quick tests (no coverage)..."
        TEST_COMMAND="docker-compose exec api pytest tests/ -v -x"
        run_tests "$TEST_COMMAND" "Quick Tests"
        ;;
    
    "auth")
        print_status "Running authentication tests..."
        TEST_COMMAND="docker-compose exec api pytest tests/test_auth.py -v"
        run_tests "$TEST_COMMAND" "Authentication Tests"
        ;;
    
    "authors")
        print_status "Running author tests..."
        TEST_COMMAND="docker-compose exec api pytest tests/test_authors.py -v"
        run_tests "$TEST_COMMAND" "Author Tests"
        ;;
    
    "books")
        print_status "Running book tests..."
        TEST_COMMAND="docker-compose exec api pytest tests/test_books.py -v"
        run_tests "$TEST_COMMAND" "Book Tests"
        ;;
    
    "coverage")
        print_status "Running tests with detailed coverage report..."
        TEST_COMMAND="docker-compose exec api pytest tests/ --cov=app --cov-report=html --cov-report=term-missing"
        run_tests "$TEST_COMMAND" "Tests with Coverage Report"
        print_status "Coverage report generated in htmlcov/index.html"
        ;;
    
    "timing")
        print_status "Running tests with detailed timing information..."
        TEST_COMMAND="docker-compose exec api pytest tests/ -v --durations=20 --durations-min=0.05"
        run_tests "$TEST_COMMAND" "Timing Analysis"
        ;;
    
    "performance")
        print_status "Running performance tests..."
        TEST_COMMAND="docker-compose exec api pytest tests/test_performance.py -v --durations=10"
        run_tests "$TEST_COMMAND" "Performance Tests"
        ;;
    
    "load")
        print_status "Running load tests..."
        TEST_COMMAND="docker-compose exec api pytest tests/test_performance.py::TestLoadTesting -v --durations=10"
        run_tests "$TEST_COMMAND" "Load Tests"
        ;;
    
    "parallel")
        print_status "Running tests in parallel..."
        TEST_COMMAND="docker-compose exec api pytest tests/ -n auto -v"
        run_tests "$TEST_COMMAND" "Parallel Tests"
        ;;
    
    "debug")
        print_status "Running tests with debug output..."
        TEST_COMMAND="docker-compose exec api pytest tests/ -v -s --tb=long"
        run_tests "$TEST_COMMAND" "Debug Tests"
        ;;
    
    "clean")
        print_status "Cleaning up test artifacts..."
        docker-compose down -v
        docker system prune -f
        print_success "Cleanup completed!"
        ;;
    
    "setup")
        print_status "Setting up test environment..."
        docker-compose down -v
        docker-compose up -d
        print_status "Waiting for services to be ready..."
        sleep 10
        print_success "Test environment setup completed!"
        ;;
    
    "help"|"-h"|"--help")
        echo "Book Collection API Test Runner"
        echo "================================"
        echo
        echo "Usage: ./run_tests.sh [option]"
        echo
        echo "Options:"
        echo "  all, full     - Run all tests with coverage"
        echo "  fast, quick   - Run tests quickly (stop on first failure)"
        echo "  auth          - Run only authentication tests"
        echo "  authors       - Run only author tests"
        echo "  books         - Run only book tests"
        echo "  coverage      - Run tests with detailed coverage report"
        echo "  timing        - Run tests with detailed timing analysis"
        echo "  performance   - Run performance tests"
        echo "  load          - Run load tests"
        echo "  parallel      - Run tests in parallel"
        echo "  debug         - Run tests with debug output"
        echo "  clean         - Clean up test artifacts"
        echo "  setup         - Setup test environment"
        echo "  help          - Show this help message"
        echo
        echo "Examples:"
        echo "  ./run_tests.sh          # Run all tests"
        echo "  ./run_tests.sh auth     # Run only auth tests"
        echo "  ./run_tests.sh coverage # Run with coverage report"
        echo
        ;;
    
    *)
        print_error "Unknown option: $1"
        echo "Use './run_tests.sh help' for usage information."
        exit 1
        ;;
esac
