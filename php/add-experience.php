<?php
/**
 * Add Experience Handler
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
$tipo = filter_input(INPUT_POST, 'tipo', FILTER_SANITIZE_SPECIAL_CHARS);
$titolo = filter_input(INPUT_POST, 'titolo', FILTER_SANITIZE_SPECIAL_CHARS);
$azienda_istituto = filter_input(INPUT_POST, 'azienda_istituto', FILTER_SANITIZE_SPECIAL_CHARS);
$data_inizio = filter_input(INPUT_POST, 'data_inizio', FILTER_SANITIZE_SPECIAL_CHARS);
$data_fine = filter_input(INPUT_POST, 'data_fine', FILTER_SANITIZE_SPECIAL_CHARS);
$is_current = isset($_POST['is_current']) ? 1 : 0;
$descrizione = filter_input(INPUT_POST, 'descrizione', FILTER_SANITIZE_SPECIAL_CHARS);

// Validation
$errors = [];

if (!in_array($tipo, ['lavoro', 'formazione'])) {
    $errors[] = 'Tipo di esperienza non valido';
}

if (empty($titolo)) {
    $errors[] = 'Il titolo è obbligatorio';
}

if (empty($azienda_istituto)) {
    $errors[] = 'Azienda/Istituto è obbligatorio';
}

if (empty($data_inizio)) {
    $errors[] = 'La data di inizio è obbligatoria';
}

// If not current, data_fine is required
if (!$is_current && empty($data_fine)) {
    $errors[] = 'La data di fine è obbligatoria se l\'esperienza non è in corso';
}

// Validate dates
if (!empty($data_inizio)) {
    $start_date = strtotime($data_inizio);
    if ($start_date === false) {
        $errors[] = 'Data di inizio non valida';
    }
}

if (!empty($data_fine) && !$is_current) {
    $end_date = strtotime($data_fine);
    if ($end_date === false) {
        $errors[] = 'Data di fine non valida';
    } elseif (isset($start_date) && $end_date < $start_date) {
        $errors[] = 'La data di fine deve essere successiva alla data di inizio';
    }
}

if (!empty($errors)) {
    $_SESSION['error'] = implode('. ', $errors);
    header('Location: ../user-dashboard.php#esperienze');
    exit;
}

// If is_current, set data_fine to NULL
if ($is_current) {
    $data_fine = null;
}

try {
    $pdo = getDbConnection();
    
    // Insert experience with prepared statement
    $stmt = $pdo->prepare("
        INSERT INTO experiences 
        (user_id, tipo, titolo, azienda_istituto, data_inizio, data_fine, is_current, descrizione) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ");
    
    $stmt->execute([
        $user_id,
        $tipo,
        $titolo,
        $azienda_istituto,
        $data_inizio,
        $data_fine,
        $is_current,
        $descrizione
    ]);
    
    $_SESSION['success'] = 'Esperienza aggiunta con successo!';
    header('Location: ../user-dashboard.php#esperienze');
    exit;
    
} catch (PDOException $e) {
    error_log("Add experience error: " . $e->getMessage());
    $_SESSION['error'] = 'Errore durante l\'aggiunta dell\'esperienza';
    header('Location: ../user-dashboard.php#esperienze');
    exit;
}
