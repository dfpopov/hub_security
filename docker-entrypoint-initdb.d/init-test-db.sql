-- Create test database
CREATE DATABASE IF NOT EXISTS book_collection_test;

-- Grant permissions to user
GRANT ALL PRIVILEGES ON book_collection_test.* TO 'user'@'%';

-- Flush privileges
FLUSH PRIVILEGES;
