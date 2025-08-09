# Book Collection API

A secure, maintainable RESTful API built with FastAPI and SQLAlchemy for managing personal book collections.

## 🚀 Features

- **JWT Authentication** - Secure user authentication with access & refresh tokens
- **Rate Limiting** - Protection against DDoS attacks with configurable limits
- **Service Layer** - Clean business logic separation with validation
- **Connection Pooling** - Optimized database performance
- **Security Hardening** - CORS protection, secure secrets management
- **CRUD Operations** - Full CRUD for Authors and Books
- **User Isolation** - Each user manages only their own data
- **Cascading Deletes** - Deleting an author removes all their books
- **Pagination & Filtering** - Advanced book filtering by genre, year, author
- **Timestamps** - Automatic created_at and updated_at tracking
- **Testing** - Comprehensive test suite with high code coverage
- **Docker Support** - Easy deployment and development

## 🛠 Tech Stack

- **Python 3.11+**
- **FastAPI** - Modern web framework
- **SQLAlchemy 2.0** - ORM with declarative models
- **MySQL 8.0** - Primary database
- **Alembic** - Database migrations
- **JWT Authentication** - Secure token-based auth with refresh tokens
- **Pydantic** - Data validation
- **SlowAPI** - Rate limiting and protection
- **Pytest** - Testing framework with comprehensive coverage
- **Docker & Docker Compose** - Containerization

## 📋 Requirements

- Python 3.11+
- Docker & Docker Compose
- Git

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone <repository-url>
cd hub_security
```

### 2. Set up environment

Copy the example environment file:

```bash
cp env.example .env
```

### 3. Start the application

```bash
docker-compose up -d
```

The application will automatically:

- Start MySQL database
- Run database migrations
- Start the FastAPI server

### 4. Access the API

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### 5. Run Tests (Optional)

Now you can run the test suite:

```bash
# Run all tests
docker-compose exec api pytest tests/ -v

# Or use the test runner scripts
./run_tests.sh  # Linux/Mac
run_tests.bat   # Windows
```

## 🧪 Testing

This project includes a comprehensive testing suite with high code coverage.

### 🚀 Two Testing Modes Available

The same test files work in both modes - the system automatically detects the environment and adjusts accordingly.

#### **1. Isolated Testing (Recommended)**

**No Docker required!** Tests run with SQLite in-memory database:

```bash
# Run isolated tests (fast, no dependencies)
python scripts/run_tests_isolated.py

# Run specific test categories
python scripts/run_tests_isolated.py --auth      # Authentication tests only
python scripts/run_tests_isolated.py --authors   # Author tests only
python scripts/run_tests_isolated.py --books     # Book tests only
python scripts/run_tests_isolated.py --coverage  # With coverage report
python scripts/run_tests_isolated.py --fast      # Skip slow tests
```

# Run specific test categories

python scripts/run_tests_isolated.py --auth
python scripts/run_tests_isolated.py --authors
python scripts/run_tests_isolated.py --books

# Run with coverage

python scripts/run_tests_isolated.py --coverage

# Quick tests (stop on first failure)

python scripts/run_tests_isolated.py --fast

````

**✅ Advantages:**

- No Docker required
- Fast execution (SQLite in-memory)
- Isolated test environment
- Works offline
- Perfect for CI/CD

#### **2. Integration Testing (Docker Required)**

**Full integration tests with MySQL database:**

```bash
# Run integration tests (automatically starts Docker Compose)
python scripts/run_tests_integration.py

# Run specific test categories
python scripts/run_tests_integration.py --auth      # Authentication tests only
python scripts/run_tests_integration.py --authors   # Author tests only
python scripts/run_tests_integration.py --books     # Book tests only
python scripts/run_tests_integration.py --coverage  # With coverage report
python scripts/run_tests_integration.py --fast      # Skip slow tests
````

**⚠️ Requires:**

- Docker installed and running
- Docker Compose available
- Internet connection (for Docker images)

### Running Tests

#### Using the Test Runner Scripts

**Windows:**

```bash
# Run all tests
scripts/run_tests.bat

# Run specific test categories
scripts/run_tests.bat auth
scripts/run_tests.bat authors
scripts/run_tests.bat books

# Run with coverage
scripts/run_tests.bat coverage

# Performance tests
scripts/run_tests.bat performance

# Load tests
scripts/run_tests.bat load

# Quick tests (stop on first failure)
scripts/run_tests.bat fast

# Debug mode
scripts/run_tests.bat debug

# Show help
scripts/run_tests.bat help
```

**Linux/Mac:**

```bash
# Make script executable (first time only)
chmod +x scripts/run_tests.sh

# Run all tests
./scripts/run_tests.sh

# Run specific test categories
./scripts/run_tests.sh auth
./scripts/run_tests.sh authors
./scripts/run_tests.sh books

# Run with coverage
./scripts/run_tests.sh coverage

# Performance tests
./scripts/run_tests.sh performance

# Load tests
./scripts/run_tests.sh load

# Quick tests (stop on first failure)
./scripts/run_tests.sh fast

# Debug mode
./scripts/run_tests.sh debug

# Show help
./scripts/run_tests.sh help
```

#### Direct Commands

**⚠️ Prerequisite: Ensure Docker Compose is running (`docker-compose up -d`)**

```bash
# Run all tests
docker-compose exec api pytest tests/ -v

# Run specific test files
docker-compose exec api pytest tests/test_auth.py -v
docker-compose exec api pytest tests/test_authors.py -v
docker-compose exec api pytest tests/test_books.py -v

# Run with coverage
docker-compose exec api pytest tests/ --cov=app --cov-report=html

# Run tests in parallel
docker-compose exec api pytest tests/ -n auto

# Run with debug output
docker-compose exec api pytest tests/ -v -s --tb=long

# Run performance tests
docker-compose exec api pytest tests/test_performance.py -v

# Run load tests
docker-compose exec api pytest tests/test_performance.py::TestLoadTesting -v
```

### Test Coverage

The test suite provides comprehensive coverage including:

- ✅ **Authentication & Authorization** - JWT token validation
- ✅ **CRUD Operations** - Full Create, Read, Update, Delete testing
- ✅ **Data Validation** - Pydantic schema validation
- ✅ **Error Handling** - 400, 401, 403, 404 responses
- ✅ **User Isolation** - Multi-user data separation
- ✅ **Business Logic** - Cascading deletes, filtering, pagination
- ✅ **Edge Cases** - Invalid data, missing fields, duplicates
- ✅ **Performance Testing** - Response time and load testing
- ✅ **Memory Usage** - Memory consumption monitoring

### Load Testing

The project includes comprehensive load testing capabilities using Locust:

**Quick Load Test:**

```bash
# Linux/Mac
./scripts/run_load_test.sh quick

# Windows
scripts/run_load_test.bat quick
```

**Available Load Test Options:**

- `quick` - 5 users, 30 seconds
- `medium` - 20 users, 2 minutes
- `heavy` - 50 users, 5 minutes
- `stress` - 100 users, 10 minutes

**Load Test Features:**

- ✅ **Realistic User Simulation** - Simulates actual user behavior
- ✅ **Concurrent User Testing** - Tests multiple simultaneous users
- ✅ **Response Time Analysis** - Measures average and percentile response times
- ✅ **Error Rate Monitoring** - Tracks failed requests
- ✅ **HTML Reports** - Generates detailed performance reports
- ✅ **CSV Data Export** - Exports test data for analysis

**Performance Benchmarks:**

- Books list: < 1.0s for 50 books
- Single book retrieval: < 0.1s
- Authentication: < 0.5s
- Concurrent requests: < 2.0s max response time
- Memory usage: < 50MB increase under load

## 📚 API Endpoints

### Authentication

- `POST /api/v1/auth/register` - Register new user (Rate limit: 5/minute)
- `POST /api/v1/auth/login` - Login user (email or username) (Rate limit: 10/minute)
- `GET /api/v1/auth/me` - Get current user information

### Rate Limiting

The API includes built-in rate limiting to protect against abuse:

- **Registration**: 5 requests per minute per IP
- **Login**: 10 requests per minute per IP
- **General endpoints**: 10 requests per minute per IP
- **Health check**: 30 requests per minute per IP

Rate limiting is disabled in development mode (DEBUG=True) for easier testing.

### Authors

- `GET /api/v1/authors/` - List all authors (paginated)
- `POST /api/v1/authors/` - Create new author
- `GET /api/v1/authors/{id}` - Get author by ID
- `PUT /api/v1/authors/{id}` - Update author
- `DELETE /api/v1/authors/{id}` - Delete author

### Books

- `GET /api/v1/books/` - List all books (with filtering & pagination)
- `POST /api/v1/books/` - Create new book
- `GET /api/v1/books/{id}` - Get book by ID
- `PUT /api/v1/books/{id}` - Update book
- `DELETE /api/v1/books/{id}` - Delete book

### Query Parameters for Books

- `genre` - Filter by genre
- `publication_year` - Filter by publication year
- `author_id` - Filter by author
- `skip` - Pagination offset (default: 0)
- `limit` - Pagination limit (default: 100, max: 100)

## 🔧 Development

### Project Structure

```
hub_security/
├── app/
│   ├── main.py              # FastAPI application
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py          # User model
│   │   ├── author.py        # Author model
│   │   └── book.py          # Book model
│   ├── schemas/             # Pydantic schemas
│   │   ├── user.py          # User schemas
│   │   ├── author.py        # Author schemas
│   │   └── book.py          # Book schemas
│   ├── services/            # Business logic layer
│   │   ├── book_service.py  # Book business logic
│   │   └── user_service.py  # User business logic
│   ├── api/                 # API routes
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── author.py        # Author endpoints
│   │   ├── book.py          # Book endpoints
│   │   └── deps.py          # Dependencies
│   ├── core/                # Configuration & security
│   │   ├── rate_limiter.py  # Rate limiting
│   │   ├── config.py        # Settings
│   │   └── security.py      # JWT & password hashing
│   ├── db/                  # Database setup
│   │   ├── base.py          # Database configuration
│   │   └── session.py       # Session management
│   └── crud/                # CRUD operations
│       ├── user.py          # User CRUD
│       ├── author.py        # Author CRUD
│       └── book.py          # Book CRUD
├── alembic/                 # Database migrations
│   └── versions/            # Migration files
├── tests/                   # Test suite
│   ├── conftest.py          # Test configuration & fixtures
│   ├── test_auth.py         # Authentication tests
│   ├── test_authors.py      # Author tests
│   ├── test_books.py        # Book tests
│   ├── test_crud.py         # CRUD operation tests
│   ├── test_db.py           # Database tests
│   ├── test_deps.py         # Dependency tests
│   ├── test_main.py         # Main app tests
│   └── test_security.py     # Security tests
├── docker-entrypoint-initdb.d/  # Database initialization
├── docker-compose.yml       # Docker services
├── Dockerfile              # API container
├── requirements.txt        # Python dependencies
├── pytest.ini             # Pytest configuration
├── alembic.ini            # Alembic configuration
├── run_tests.sh           # Linux/Mac test runner
├── run_tests.bat          # Windows test runner
├── env.example            # Environment variables example
└── README.md              # This file
```

### Environment Variables

Create a `.env` file based on `env.example`:

```env
# Database Configuration
MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_USER=user
MYSQL_PASSWORD=password
DATABASE_URL=mysql+pymysql://${MYSQL_USER}:${MYSQL_PASSWORD}@localhost:3306/book_collection
TEST_DATABASE_URL=mysql+pymysql://${MYSQL_USER}:${MYSQL_PASSWORD}@localhost:3306/book_collection_test

# JWT Configuration
SECRET_KEY=your-super-secret-key-here-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS Configuration
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com

# Database Pool Configuration
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# API Configuration
API_V1_STR=/api/v1
PROJECT_NAME=Book Collection API
DEBUG=True
```

### Database Migrations

```bash
# Create new migration
docker-compose exec api alembic revision --autogenerate -m "Description"

# Apply migrations
docker-compose exec api alembic upgrade head

# Rollback migration
docker-compose exec api alembic downgrade -1

# Check migration status
docker-compose exec api alembic current
```

## 🐳 Docker

### Services

- **api** - FastAPI application (port 8000)
- **db** - MySQL database (port 3306)

### Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build

# Clean up volumes
docker-compose down -v
```

## 📊 Assumptions Made

1. **User Authentication**: Users must be authenticated to access any API endpoint
2. **Data Isolation**: Users can only access their own authors and books
3. **Cascading Deletes**: Deleting an author removes all associated books
4. **Input Validation**: All inputs are validated using Pydantic schemas
5. **Error Handling**: Proper HTTP status codes and error messages
6. **Pagination**: Large result sets are paginated with configurable limits
7. **Filtering**: Books can be filtered by multiple criteria simultaneously
8. **Timestamps**: All entities have automatic created_at and updated_at fields
9. **Email/Username Login**: Users can login with either email or username
10. **Password Security**: Passwords are hashed using bcrypt
11. **JWT Tokens**: Access tokens expire after 30 minutes
12. **Database**: MySQL 8.0 with proper indexing and foreign key constraints
13. **Rate Limiting**: Configurable request limits for API protection
14. **Service Layer**: Business logic separation for maintainability
15. **Connection Pooling**: Optimized database connection management

## 🔒 Security Features

- **JWT Authentication** with access & refresh tokens
- **Rate Limiting** - Configurable request limits per endpoint
- **CORS Protection** - Secure cross-origin request handling
- **Secure Secrets** - Environment-based configuration
- **Password Hashing** using bcrypt with salt
- **Input Validation** with Pydantic schemas
- **User Data Isolation** - users can only access their own data
- **SQL Injection Protection** through SQLAlchemy ORM
- **Connection Pooling** - Optimized database connections
- **Business Logic Validation** - Service layer security checks

## 🚀 Performance Features

- **Database Indexing** on frequently queried fields
- **Pagination** to limit result set sizes
- **Connection Pooling** for database connections
- **Efficient Queries** with proper SQLAlchemy usage
- **N+1 Query Prevention** - Eager loading for related data
- **Rate Limiting** - Protection against abuse
- **Caching Ready** - structure supports Redis integration

## 🚀 Production Deployment

- Set production SECRET_KEY
- Configure CORS_ORIGINS for production domains
- Set DEBUG=False
- Configure database connection pooling
- Set up monitoring and logging
- Configure rate limiting for production

### Environment Variables for Production

```env
# Production Settings
DEBUG=False
SECRET_KEY=your-production-secret-key-here-minimum-32-characters
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com

# Database Pool Configuration
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# Rate Limiting
# Configure appropriate limits for your use case
# Default: 5/minute for register, 10/minute for login
```
