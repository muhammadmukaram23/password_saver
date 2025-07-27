-- Create the database
CREATE DATABASE IF NOT EXISTS credentials_vault;
USE credentials_vault;

-- Table to store users (owners of the credentials)
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    master_password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- General credentials table (for websites, services, etc.)
CREATE TABLE credentials (
    credential_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(100),
    username VARCHAR(100),
    password_encrypted TEXT,
    url VARCHAR(255),
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Email accounts (e.g., Gmail, Yahoo, etc.)
CREATE TABLE email_accounts (
    email_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    email_address VARCHAR(100) NOT NULL,
    provider VARCHAR(50), -- e.g., Gmail, Yahoo
    password_encrypted TEXT,
    recovery_email VARCHAR(100),
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Credit and Debit cards
CREATE TABLE credit_cards (
    card_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    card_holder_name VARCHAR(100),
    card_number_encrypted TEXT,
    expiration_date DATE,
    cvv_encrypted TEXT,
    billing_address TEXT,
    card_type ENUM('Credit', 'Debit', 'Prepaid') DEFAULT 'Credit',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Computers and Laptops
CREATE TABLE devices (
    device_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    device_type ENUM('Laptop', 'Desktop', 'Tablet', 'Other') DEFAULT 'Laptop',
    brand VARCHAR(50),
    model VARCHAR(100),
    serial_number VARCHAR(100),
    operating_system VARCHAR(50),
    admin_password_encrypted TEXT,
    purchase_date DATE,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
