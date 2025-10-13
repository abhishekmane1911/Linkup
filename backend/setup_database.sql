-- MySQL Database Setup for Linkup Backend
-- Run this script in MySQL Workbench to create the database

-- Create the database
CREATE DATABASE IF NOT EXISTS linkup_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create a user for the application (optional, you can use root)
-- CREATE USER IF NOT EXISTS 'linkup_user'@'localhost' IDENTIFIED BY 'your_password_here';

-- Grant privileges to the user
-- GRANT ALL PRIVILEGES ON linkup_db.* TO 'linkup_user'@'localhost';

-- If using root user, just make sure you have access to the database
-- GRANT ALL PRIVILEGES ON linkup_db.* TO 'root'@'localhost';

-- Flush privileges
FLUSH PRIVILEGES;

-- Use the database
USE linkup_db;

-- Show that the database was created successfully
SHOW DATABASES LIKE 'linkup_db';