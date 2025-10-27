<?php
/**
 * Login Handler
 * Uses prepared statements and password verification
 */

require_once '../config/database.php';
startSecureSession();

// Only accept POST requests
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: ../index.php');
    exit;
}

// Validate and sanitize input
$email = filter_input(INPUT_POST, 'email', FILTER_SANITIZE_EMAIL);
$password = $_POST['password'] ?? '';

// Validate email format
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    $_SESSION['login_error'] = 'Email non valida';
    header('Location: ../index.php');
    exit;
}

// Check if fields are not empty
if (empty($email) || empty($password)) {
    $_SESSION['login_error'] = 'Tutti i campi sono obbligatori';
    header('Location: ../index.php');
    exit;
}

try {
    $pdo = getDbConnection();
    
    // Use prepared statement to prevent SQL injection
    $stmt = $pdo->prepare("SELECT * FROM users WHERE email = ?");
    $stmt->execute([$email]);
    $user = $stmt->fetch();
    
    // Verify user exists and password is correct
    if ($user && password_verify($password, $user['password_hash'])) {
        // Regenerate session ID to prevent session fixation
        session_regenerate_id(true);
        
        // Set session variables
        $_SESSION['user_id'] = $user['id'];
        $_SESSION['user_email'] = $user['email'];
        $_SESSION['user_name'] = $user['nome'];
        $_SESSION['role'] = $user['role'];
        $_SESSION['login_time'] = time();
        
        // Redirect based on role
        if ($user['role'] === 'admin') {
            header('Location: ../admin-dashboard.php');
        } else {
            header('Location: ../user-dashboard.php');
        }
        exit;
    } else {
        // Invalid credentials
        $_SESSION['login_error'] = 'Email o password non corretti';
        header('Location: ../index.php');
        exit;
    }
    
} catch (PDOException $e) {
    error_log("Login error: " . $e->getMessage());
    $_SESSION['login_error'] = 'Errore durante il login. Riprova più tardi.';
    header('Location: ../index.php');
    exit;
}
