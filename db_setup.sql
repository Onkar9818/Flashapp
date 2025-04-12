
-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS flashapp;
USE flashapp;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    register_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create decks table
CREATE TABLE IF NOT EXISTS decks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_studied TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create cards table
CREATE TABLE IF NOT EXISTS cards (
    id INT AUTO_INCREMENT PRIMARY KEY,
    front TEXT NOT NULL,
    back TEXT NOT NULL,
    deck_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_reviewed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    difficulty_rating INT DEFAULT 0,
    review_count INT DEFAULT 0,
    FOREIGN KEY (deck_id) REFERENCES decks(id) ON DELETE CASCADE
);

-- Create study_sessions table for tracking study progress
CREATE TABLE IF NOT EXISTS study_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    deck_id INT NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    cards_reviewed INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (deck_id) REFERENCES decks(id) ON DELETE CASCADE
);

-- Create card_reviews table for detailed review history
CREATE TABLE IF NOT EXISTS card_reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    card_id INT NOT NULL,
    session_id INT NOT NULL,
    review_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rating INT NOT NULL, -- 1-5 rating of difficulty
    FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES study_sessions(id) ON DELETE CASCADE
);
