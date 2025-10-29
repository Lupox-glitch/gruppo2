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



-- Insert default admin user
-- Password: admin123 (CHANGE THIS IN PRODUCTION!)
INSERT INTO users (email, password_hash, nome, cognome, role) 
VALUES ('admin@cvmanagement.it', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Admin', 'Sistema', 'admin')
ON DUPLICATE KEY UPDATE id=id;

-- Insert sample student user
-- Password: student123
INSERT INTO users (email, password_hash, nome, cognome, role) 
VALUES ('student@test.it', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Mario', 'Rossi', 'student')
ON DUPLICATE KEY UPDATE id=id;

INSERT INTO users (email, password_hash, nome, cognome, role) 
VALUES ('prova@test.it', 'd2c8e3b5a1f09c7d4e6f8a2b0c4d6e8f1a3b5c7d9e1f0a8b2c4d6e8f0a1b2c3d', '4f8a3d1c9b2e5f7a0c1b3d5e7f9a2c4d', 'gennaro', 'prova', 'student')
ON DUPLICATE KEY UPDATE id=id;

INSERT INTO users (email, password_hash, nome, cognome, role) 
VALUES ('admin@test.it', 'd2c8e3b5a1f09c7d4e6f8a2b0c4d6e8f1a3b5c7d9e1f0a8b2c4d6e8f0a1b2c3d', '4f8a3d1c9b2e5f7a0c1b3d5e7f9a2c4d', 'gennaro', 'bullo', 'admin')
ON DUPLICATE KEY UPDATE id=id;
