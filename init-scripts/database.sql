-- Database Schema for CV Management System
-- Create database
CREATE DATABASE IF NOT EXISTS cv_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE cv_management;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    salt VARCHAR(255) NOT NULL,
    nome VARCHAR(100) NOT NULL,
    cognome VARCHAR(100) NOT NULL,
--  nazionalita' la metto come dato del cv non dell'utente 
--  data_nascita che troviamo nei dati del cv inutile ripeterla 
    role ENUM('student', 'admin') DEFAULT 'student',
    INDEX idx_email (email),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- CV Data table
CREATE TABLE IF NOT EXISTS cv_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    telefono VARCHAR(20),
    indirizzo VARCHAR(255),
--  email gia' presente nell'utente 
    data_nascita DATE,
    citta VARCHAR(100),
    nazionalita VARCHAR(100),
    linkedin_url VARCHAR(255),
    patente VARCHAR(100),
    hobby TEXT,
    skills TEXT,
    languages TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Experiences table (work and education)
CREATE TABLE IF NOT EXISTS experiences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    tipo ENUM('lavoro', 'formazione') NOT NULL,
    titolo VARCHAR(255) NOT NULL,
    azienda_istituto VARCHAR(255) NOT NULL,
    data_inizio DATE NOT NULL,
    data_fine DATE,
    descrizione TEXT,
    is_current BOOLEAN DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_tipo (tipo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- tabella dei cv in relazione a user_id
CREATE TABLE IF NOT EXISTS user_cvs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    cv_file_path VARCHAR(255) NOT NULL,
    uploaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_uploaded_at (uploaded_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
