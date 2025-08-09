#!/bin/bash

# Load testing script using Locust
# Usage: ./run_load_test.sh [option]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if API is running
if ! docker-compose ps api | grep -q "Up"; then
    print_warning "API service is not running. Starting services..."
    docker-compose up -d
    print_status "Waiting for API to be ready..."
    sleep 10
fi

# Default values
USERS=10
SPAWN_RATE=2
RUNTIME=60
HOST="http://localhost:8000"

# Parse command line arguments
case "$1" in
    "quick")
        USERS=5
        SPAWN_RATE=1
        RUNTIME=30
        print_status "Running quick load test: $USERS users, ${SPAWN_RATE}/s spawn rate, ${RUNTIME}s runtime"
        ;;
    
    "medium")
        USERS=20
        SPAWN_RATE=5
        RUNTIME=120
        print_status "Running medium load test: $USERS users, ${SPAWN_RATE}/s spawn rate, ${RUNTIME}s runtime"
        ;;
    
    "heavy")
        USERS=50
        SPAWN_RATE=10
        RUNTIME=300
        print_status "Running heavy load test: $USERS users, ${SPAWN_RATE}/s spawn rate, ${RUNTIME}s runtime"
        ;;
    
    "stress")
        USERS=100
        SPAWN_RATE=20
        RUNTIME=600
        print_status "Running stress test: $USERS users, ${SPAWN_RATE}/s spawn rate, ${RUNTIME}s runtime"
        ;;
    
    "help"|"-h"|"--help")
        echo "Load Testing Script for Book Collection API"
        echo "==========================================="
        echo
        echo "Usage: ./run_load_test.sh [option]"
        echo
        echo "Options:"
        echo "  quick   - Quick test (5 users, 30s)"
        echo "  medium  - Medium load (20 users, 2min)"
        echo "  heavy   - Heavy load (50 users, 5min)"
        echo "  stress  - Stress test (100 users, 10min)"
        echo "  help    - Show this help message"
        echo
        echo "Examples:"
        echo "  ./run_load_test.sh quick   # Quick load test"
        echo "  ./run_load_test.sh medium  # Medium load test"
        echo "  ./run_load_test.sh stress  # Stress test"
        echo
        echo "After running, open http://localhost:8089 to view results"
        echo
        exit 0
        ;;
    
    *)
        print_error "Unknown option: $1"
        echo "Use './run_load_test.sh help' for usage information."
        exit 1
        ;;
esac

print_status "Starting Locust load testing..."
print_status "Target: $HOST"
print_status "Users: $USERS"
print_status "Spawn rate: $SPAWN_RATE users/second"
print_status "Runtime: $RUNTIME seconds"
echo

# Run Locust
docker-compose exec api locust \
    --host="$HOST" \
    --users="$USERS" \
    --spawn-rate="$SPAWN_RATE" \
    --run-time="${RUNTIME}s" \
    --headless \
    --html=load_test_report.html \
    --csv=load_test_results \
    --logfile=locust.log

print_success "Load test completed!"
print_status "Results saved to:"
echo "  - load_test_report.html (HTML report)"
echo "  - load_test_results.csv (CSV data)"
echo "  - locust.log (Log file)"

# Show summary
if [ -f "load_test_results_stats.csv" ]; then
    echo
    print_status "Test Summary:"
    tail -n 1 load_test_results_stats.csv | awk -F',' '{
        print "  - Total Requests: " $2
        print "  - Failed Requests: " $3
        print "  - Average Response Time: " $4 "ms"
        print "  - 95th Percentile: " $6 "ms"
        print "  - Requests/sec: " $7
    }'
fi
