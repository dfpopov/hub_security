"""
Load testing script for Book Collection API using Locust.
Run with: locust -f locustfile.py --host=http://localhost:8000
"""

import json
import random
from locust import HttpUser, task, between
from typing import Dict, Any


class BookCollectionUser(HttpUser):
    """Simulates a user interacting with the Book Collection API."""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Login and get authentication token on start."""
        # Register a new user for this test session
        user_data = {
            "username": f"loadtest_user_{random.randint(1000, 9999)}",
            "email": f"loadtest_{random.randint(1000, 9999)}@example.com",
            "password": "testpassword123"
        }
        
        # Register user
        response = self.client.post("/api/v1/auth/register", json=user_data)
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.user_id = response.json()["user"]["id"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
            
            # Create some test data
            self._create_test_data()
        else:
            # If registration fails, try to login
            login_data = {
                "username": "loadtest_user",
                "password": "testpassword123"
            }
            response = self.client.post("/api/v1/auth/login", data=login_data)
            if response.status_code == 200:
                self.token = response.json()["access_token"]
                self.headers = {"Authorization": f"Bearer {self.token}"}
            else:
                self.token = None
                self.headers = {}
    
    def _create_test_data(self):
        """Create test authors and books for load testing."""
        if not self.token:
            return
        
        # Create authors
        authors = []
        for i in range(5):
            author_data = {
                "name": f"Load Test Author {i}",
                "biography": f"Biography for load test author {i}"
            }
            response = self.client.post("/api/v1/authors/", json=author_data, headers=self.headers)
            if response.status_code == 200:
                authors.append(response.json()["id"])
        
        # Create books
        for i in range(10):
            if authors:
                book_data = {
                    "title": f"Load Test Book {i}",
                    "description": f"Description for load test book {i}",
                    "genre": f"Genre {i % 3}",
                    "publication_year": 2020 + (i % 5),
                    "author_id": random.choice(authors)
                }
                self.client.post("/api/v1/books/", json=book_data, headers=self.headers)
    
    @task(3)
    def get_books(self):
        """Get list of books (most common operation)."""
        if self.token:
            self.client.get("/api/v1/books/", headers=self.headers)
    
    @task(2)
    def get_authors(self):
        """Get list of authors."""
        if self.token:
            self.client.get("/api/v1/authors/", headers=self.headers)
    
    @task(1)
    def get_books_with_filter(self):
        """Get books with filtering."""
        if self.token:
            filters = ["genre=Genre 0", "genre=Genre 1", "genre=Genre 2"]
            filter_param = random.choice(filters)
            self.client.get(f"/api/v1/books/?{filter_param}", headers=self.headers)
    
    @task(1)
    def get_single_book(self):
        """Get a single book by ID."""
        if self.token:
            # Try to get a book with a random ID (might not exist, but tests error handling)
            book_id = random.randint(1, 100)
            self.client.get(f"/api/v1/books/{book_id}", headers=self.headers)
    
    @task(1)
    def get_single_author(self):
        """Get a single author by ID."""
        if self.token:
            # Try to get an author with a random ID
            author_id = random.randint(1, 50)
            self.client.get(f"/api/v1/authors/{author_id}", headers=self.headers)
    
    @task(1)
    def create_book(self):
        """Create a new book."""
        if self.token:
            book_data = {
                "title": f"New Book {random.randint(1000, 9999)}",
                "description": f"Description for new book {random.randint(1000, 9999)}",
                "genre": random.choice(["Fiction", "Non-Fiction", "Science Fiction"]),
                "publication_year": random.randint(2010, 2024),
                "author_id": random.randint(1, 10)  # Assume some authors exist
            }
            self.client.post("/api/v1/books/", json=book_data, headers=self.headers)
    
    @task(1)
    def create_author(self):
        """Create a new author."""
        if self.token:
            author_data = {
                "name": f"New Author {random.randint(1000, 9999)}",
                "biography": f"Biography for new author {random.randint(1000, 9999)}"
            }
            self.client.post("/api/v1/authors/", json=author_data, headers=self.headers)
    
    @task(1)
    def update_book(self):
        """Update an existing book."""
        if self.token:
            book_id = random.randint(1, 50)
            update_data = {
                "title": f"Updated Book {random.randint(1000, 9999)}",
                "description": f"Updated description {random.randint(1000, 9999)}"
            }
            self.client.put(f"/api/v1/books/{book_id}", json=update_data, headers=self.headers)
    
    @task(1)
    def delete_book(self):
        """Delete a book."""
        if self.token:
            book_id = random.randint(1, 50)
            self.client.delete(f"/api/v1/books/{book_id}", headers=self.headers)
    
    @task(1)
    def get_current_user(self):
        """Get current user information."""
        if self.token:
            self.client.get("/api/v1/auth/me", headers=self.headers)


class AuthenticationUser(HttpUser):
    """Simulates users performing authentication operations."""
    
    wait_time = between(2, 5)
    
    @task(1)
    def register_user(self):
        """Register a new user."""
        user_data = {
            "username": f"auth_user_{random.randint(10000, 99999)}",
            "email": f"auth_{random.randint(10000, 99999)}@example.com",
            "password": "testpassword123"
        }
        self.client.post("/api/v1/auth/register", json=user_data)
    
    @task(2)
    def login_user(self):
        """Login with existing user."""
        login_data = {
            "username": "loadtest_user",
            "password": "testpassword123"
        }
        response = self.client.post("/api/v1/auth/login", data=login_data)
        if response.status_code == 200:
            # Store token for potential use
            self.token = response.json()["access_token"]
    
    @task(1)
    def login_with_invalid_credentials(self):
        """Test login with invalid credentials."""
        login_data = {
            "username": "invalid_user",
            "password": "wrong_password"
        }
        self.client.post("/api/v1/auth/login", data=login_data)


class HealthCheckUser(HttpUser):
    """Simulates health check requests."""
    
    wait_time = between(10, 30)  # Less frequent health checks
    
    @task(1)
    def health_check(self):
        """Check API health."""
        self.client.get("/health")
    
    @task(1)
    def root_endpoint(self):
        """Access root endpoint."""
        self.client.get("/")
    
    @task(1)
    def openapi_docs(self):
        """Access OpenAPI documentation."""
        self.client.get("/docs")
