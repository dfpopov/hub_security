# Scripts Directory

This directory contains all utility scripts for the Book Collection API project.

## 📁 Scripts Overview

### 🧪 Testing Scripts

#### `run_tests_isolated.py`

**Isolated testing with SQLite database (no Docker required)**

```bash
# Run all tests
python scripts/run_tests_isolated.py --all

# Run specific test categories
python scripts/run_tests_isolated.py --auth      # Authentication tests
python scripts/run_tests_isolated.py --authors   # Author tests
python scripts/run_tests_isolated.py --books     # Book tests

# Run with coverage
python scripts/run_tests_isolated.py --coverage

# Quick tests (skip slow tests)
python scripts/run_tests_isolated.py --fast

# Debug mode
python scripts/run_tests_isolated.py --debug

# Parallel execution
python scripts/run_tests_isolated.py --parallel

# Parallel with specific number of workers
python scripts/run_tests_isolated.py --parallel --workers 4
```

**Features:**

- ✅ No Docker required
- ✅ Fast execution (SQLite in-memory)
- ✅ Isolated test environment
- ✅ Works offline
- ✅ Perfect for CI/CD
- ✅ Parallel execution support

#### `run_tests_parallel.py`

**Parallel testing with optimized performance**

```bash
# Run all tests in parallel (auto-detect workers)
python scripts/run_tests_parallel.py --all

# Run specific test categories in parallel
python scripts/run_tests_parallel.py --auth      # Authentication tests
python scripts/run_tests_parallel.py --authors   # Author tests
python scripts/run_tests_parallel.py --books     # Book tests

# Run with specific number of workers
python scripts/run_tests_parallel.py --workers 4

# Run with coverage
python scripts/run_tests_parallel.py --coverage

# Quick tests (skip slow tests)
python scripts/run_tests_parallel.py --fast

# Debug mode
python scripts/run_tests_parallel.py --debug
```

**Features:**

- ✅ Parallel execution for maximum speed
- ✅ Auto-detection of optimal worker count
- ✅ Isolated database per worker process
- ✅ No Docker required
- ✅ SQLite in-memory databases
- ✅ Perfect for CI/CD and development

#### `run_tests_integration.py`

**Integration testing with Docker and MySQL database**

```bash
# Run all tests (automatically starts Docker Compose)
python scripts/run_tests_integration.py --all

# Run specific test categories
python scripts/run_tests_integration.py --auth      # Authentication tests
python scripts/run_tests_integration.py --authors   # Author tests
python scripts/run_tests_integration.py --books     # Book tests

# Run with coverage
python scripts/run_tests_integration.py --coverage

# Quick tests (skip slow tests)
python scripts/run_tests_integration.py --fast
```

**Features:**

- ✅ Full integration testing
- ✅ Production-like environment
- ✅ MySQL database
- ✅ Docker Compose automation

### 🐚 Shell Scripts

#### `run_tests.sh` (Linux/Mac)

**Comprehensive test runner for Unix systems**

```bash
# Make executable (first time only)
chmod +x scripts/run_tests.sh

# Run all tests
./scripts/run_tests.sh

# Run specific categories
./scripts/run_tests.sh auth
./scripts/run_tests.sh authors
./scripts/run_tests.sh books

# Run with coverage
./scripts/run_tests.sh coverage

# Performance tests
./scripts/run_tests.sh performance

# Load tests
./scripts/run_tests.sh load

# Quick tests
./scripts/run_tests.sh fast

# Debug mode
./scripts/run_tests.sh debug

# Show help
./scripts/run_tests.sh help
```

#### `run_tests.bat` (Windows)

**Comprehensive test runner for Windows**

```bash
# Run all tests
scripts/run_tests.bat

# Run specific categories
scripts/run_tests.bat auth
scripts/run_tests.bat authors
scripts/run_tests.bat books

# Run with coverage
scripts/run_tests.bat coverage

# Performance tests
scripts/run_tests.bat performance

# Load tests
scripts/run_tests.bat load

# Quick tests
scripts/run_tests.bat fast

# Debug mode
scripts/run_tests.bat debug

# Show help
scripts/run_tests.bat help
```

### 🚀 Load Testing Scripts

#### `run_load_test.sh` (Linux/Mac)

**Load testing with Locust for Unix systems**

```bash
# Make executable (first time only)
chmod +x scripts/run_load_test.sh

# Quick load test (5 users, 30 seconds)
./scripts/run_load_test.sh quick

# Medium load test (20 users, 2 minutes)
./scripts/run_load_test.sh medium

# Heavy load test (50 users, 5 minutes)
./scripts/run_load_test.sh heavy

# Stress test (100 users, 10 minutes)
./scripts/run_load_test.sh stress
```

#### `run_load_test.bat` (Windows)

**Load testing with Locust for Windows**

```bash
# Quick load test (5 users, 30 seconds)
scripts/run_load_test.bat quick

# Medium load test (20 users, 2 minutes)
scripts/run_load_test.bat medium

# Heavy load test (50 users, 5 minutes)
scripts/run_load_test.bat heavy

# Stress test (100 users, 10 minutes)
scripts/run_load_test.bat stress
```

### 📊 Load Testing Configuration

#### `locustfile.py`

**Locust configuration for load testing**

This file defines the load testing scenarios and user behaviors for the Book Collection API.

**Features:**

- ✅ Realistic user simulation
- ✅ Concurrent user testing
- ✅ Response time analysis
- ✅ Error rate monitoring
- ✅ HTML reports generation
- ✅ CSV data export

## 🎯 Usage Examples

### Quick Start

1. **Run isolated tests (recommended for development):**

   ```bash
   python scripts/run_tests_isolated.py --all
   ```

2. **Run parallel tests (fastest execution):**

   ```bash
   python scripts/run_tests_parallel.py --all
   ```

3. **Run integration tests (requires Docker):**

   ```bash
   python scripts/run_tests_integration.py --all
   ```

4. **Run load tests:**

   ```bash
   # Linux/Mac
   ./scripts/run_load_test.sh quick

   # Windows
   scripts/run_load_test.bat quick
   ```

### Development Workflow

1. **During development (fast feedback):**

   ```bash
   python scripts/run_tests_isolated.py --fast
   ```

2. **Before commit (full testing with parallel execution):**

   ```bash
   python scripts/run_tests_parallel.py --coverage
   ```

3. **Before deployment (integration testing):**
   ```bash
   python scripts/run_tests_integration.py --all
   ```

### Performance Comparison

| Test Mode   | Speed     | Resource Usage | Isolation | Best For          |
| ----------- | --------- | -------------- | --------- | ----------------- |
| Isolated    | Fast      | Low            | High      | Development       |
| Parallel    | Very Fast | Medium         | High      | CI/CD, Pre-commit |
| Integration | Slow      | High           | Medium    | Pre-deployment    |

## 🔧 Script Dependencies

### Python Scripts

- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `pytest-xdist` - Parallel testing

### Load Testing

- `locust` - Load testing framework

### Shell Scripts

- `docker` - Container management
- `docker-compose` - Multi-container orchestration

## 📝 Notes

- All scripts are designed to work from the project root directory
- Python scripts automatically detect the environment and adjust accordingly
- Shell scripts include comprehensive error handling and user feedback
- Load testing scripts generate detailed reports in the `reports/` directory
- All scripts support both development and production environments
- Parallel tests use isolated SQLite databases per worker process to avoid conflicts
- Parallel execution is automatically optimized based on CPU cores available
