<?php
/**
 * Registration Handler
 * Uses prepared statements and password hashing
 */

require_once '../config/database.php';
startSecureSession();

// Only accept POST requests
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: ../register.php');
    exit;
}

// Validate and sanitize input
$nome = filter_input(INPUT_POST, 'nome', FILTER_SANITIZE_SPECIAL_CHARS);
$cognome = filter_input(INPUT_POST, 'cognome', FILTER_SANITIZE_SPECIAL_CHARS);
$email = filter_input(INPUT_POST, 'email', FILTER_SANITIZE_EMAIL);
$password = $_POST['password'] ?? '';
$password_confirm = $_POST['password_confirm'] ?? '';

// Validation checks
$errors = [];

if (empty($nome) || strlen($nome) < 2) {
    $errors[] = 'Il nome deve contenere almeno 2 caratteri';
}

if (empty($cognome) || strlen($cognome) < 2) {
    $errors[] = 'Il cognome deve contenere almeno 2 caratteri';
}

if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    $errors[] = 'Email non valida';
}

if (strlen($password) < 8) {
    $errors[] = 'La password deve contenere almeno 8 caratteri';
}

if (!preg_match('/[A-Z]/', $password)) {
    $errors[] = 'La password deve contenere almeno una lettera maiuscola';
}

if (!preg_match('/[a-z]/', $password)) {
    $errors[] = 'La password deve contenere almeno una lettera minuscola';
}

if (!preg_match('/[0-9]/', $password)) {
    $errors[] = 'La password deve contenere almeno un numero';
}

if ($password !== $password_confirm) {
    $errors[] = 'Le password non corrispondono';
}

if (!empty($errors)) {
    $_SESSION['register_error'] = implode('. ', $errors);
    header('Location: ../register.php');
    exit;
}

try {
    $pdo = getDbConnection();
    
    // Check if email already exists using prepared statement
    $stmt = $pdo->prepare("SELECT id FROM users WHERE email = ?");
    $stmt->execute([$email]);
    
    if ($stmt->fetch()) {
        $_SESSION['register_error'] = 'Questa email è già registrata';
        header('Location: ../register.php');
        exit;
    }
    
    // Hash password securely
    $password_hash = password_hash($password, PASSWORD_BCRYPT, ['cost' => 12]);
    
    // Insert new user with prepared statement
    $stmt = $pdo->prepare("
        INSERT INTO users (email, password_hash, nome, cognome, role) 
        VALUES (?, ?, ?, ?, 'student')
    ");
    
    $stmt->execute([$email, $password_hash, $nome, $cognome]);
    
    // Get the new user ID
    $user_id = $pdo->lastInsertId();
    
    // Create empty CV data record
    $stmt = $pdo->prepare("INSERT INTO cv_data (user_id) VALUES (?)");
    $stmt->execute([$user_id]);
    
    // Success - redirect to login
    $_SESSION['login_success'] = 'Registrazione completata! Accedi con le tue credenziali.';
    header('Location: ../index.php');
    exit;
    
} catch (PDOException $e) {
    error_log("Registration error: " . $e->getMessage());
    $_SESSION['register_error'] = 'Errore durante la registrazione. Riprova più tardi.';
    header('Location: ../register.php');
    exit;
}
