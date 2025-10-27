<?php
/**
 * Database Configuration
 * Secure PDO connection with prepared statements
 */

// Database credentials
define('DB_HOST', 'localhost');
define('DB_NAME', 'cv_management');
define('DB_USER', 'root');
define('DB_PASS', '');

// Create secure PDO connection
function getDbConnection() {
    try {
        $dsn = "mysql:host=" . DB_HOST . ";dbname=" . DB_NAME . ";charset=utf8mb4";
        $options = [
            PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES   => false, // Use real prepared statements
        ];
        
        $pdo = new PDO($dsn, DB_USER, DB_PASS, $options);
        return $pdo;
    } catch (PDOException $e) {
        error_log("Database Connection Error: " . $e->getMessage());
        die("Errore di connessione al database. Riprova più tardi.");
    }
}

// Start session securely
function startSecureSession() {
    if (session_status() === PHP_SESSION_NONE) {
        ini_set('session.cookie_httponly', 1);
        ini_set('session.use_only_cookies', 1);
        ini_set('session.cookie_secure', 0); // Set to 1 if using HTTPS
        session_start();
    }
}
