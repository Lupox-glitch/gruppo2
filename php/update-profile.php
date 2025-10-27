<?php
/**
 * Update Profile Handler
 * Uses prepared statements and input validation
 */

require_once '../config/database.php';
startSecureSession();

// Check if user is logged in
if (!isset($_SESSION['user_id'])) {
    header('Location: ../index.php');
    exit;
}

// Only accept POST requests
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: ../user-dashboard.php');
    exit;
}

$user_id = $_SESSION['user_id'];

// Sanitize and validate input
$nome = filter_input(INPUT_POST, 'nome', FILTER_SANITIZE_SPECIAL_CHARS);
$cognome = filter_input(INPUT_POST, 'cognome', FILTER_SANITIZE_SPECIAL_CHARS);
$email = filter_input(INPUT_POST, 'email', FILTER_SANITIZE_EMAIL);
$telefono = filter_input(INPUT_POST, 'telefono', FILTER_SANITIZE_SPECIAL_CHARS);
$data_nascita = filter_input(INPUT_POST, 'data_nascita', FILTER_SANITIZE_SPECIAL_CHARS);
$citta = filter_input(INPUT_POST, 'citta', FILTER_SANITIZE_SPECIAL_CHARS);
$indirizzo = filter_input(INPUT_POST, 'indirizzo', FILTER_SANITIZE_SPECIAL_CHARS);
$linkedin_url = filter_input(INPUT_POST, 'linkedin_url', FILTER_SANITIZE_URL);

// Validation
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

if (!empty($linkedin_url) && !filter_var($linkedin_url, FILTER_VALIDATE_URL)) {
    $errors[] = 'URL LinkedIn non valido';
}

if (!empty($errors)) {
    $_SESSION['error'] = implode('. ', $errors);
    header('Location: ../user-dashboard.php');
    exit;
}

try {
    $pdo = getDbConnection();
    
    // Check if email is already used by another user
    $stmt = $pdo->prepare("SELECT id FROM users WHERE email = ? AND id != ?");
    $stmt->execute([$email, $user_id]);
    
    if ($stmt->fetch()) {
        $_SESSION['error'] = 'Questa email è già utilizzata da un altro utente';
        header('Location: ../user-dashboard.php');
        exit;
    }
    
    // Update users table with prepared statement
    $stmt = $pdo->prepare("
        UPDATE users 
        SET nome = ?, cognome = ?, email = ? 
        WHERE id = ?
    ");
    $stmt->execute([$nome, $cognome, $email, $user_id]);
    
    // Update or insert CV data
    $stmt = $pdo->prepare("SELECT id FROM cv_data WHERE user_id = ?");
    $stmt->execute([$user_id]);
    $cv_exists = $stmt->fetch();
    
    if ($cv_exists) {
        // Update existing record
        $stmt = $pdo->prepare("
            UPDATE cv_data 
            SET telefono = ?, data_nascita = ?, citta = ?, indirizzo = ?, linkedin_url = ? 
            WHERE user_id = ?
        ");
        $stmt->execute([$telefono, $data_nascita, $citta, $indirizzo, $linkedin_url, $user_id]);
    } else {
        // Insert new record
        $stmt = $pdo->prepare("
            INSERT INTO cv_data (user_id, telefono, data_nascita, citta, indirizzo, linkedin_url) 
            VALUES (?, ?, ?, ?, ?, ?)
        ");
        $stmt->execute([$user_id, $telefono, $data_nascita, $citta, $indirizzo, $linkedin_url]);
    }
    
    // Update session name if changed
    $_SESSION['user_name'] = $nome;
    
    $_SESSION['success'] = 'Profilo aggiornato con successo!';
    header('Location: ../user-dashboard.php#dati-anagrafici');
    exit;
    
} catch (PDOException $e) {
    error_log("Update profile error: " . $e->getMessage());
    $_SESSION['error'] = 'Errore durante l\'aggiornamento del profilo';
    header('Location: ../user-dashboard.php');
    exit;
}
