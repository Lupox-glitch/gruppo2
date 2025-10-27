<?php
/**
 * Delete Experience Handler
 * Uses prepared statements for security
 */

require_once '../config/database.php';
startSecureSession();

// Check if user is logged in
if (!isset($_SESSION['user_id'])) {
    header('Location: ../index.php');
    exit;
}

$user_id = $_SESSION['user_id'];
$experience_id = filter_input(INPUT_GET, 'id', FILTER_VALIDATE_INT);

if (!$experience_id) {
    $_SESSION['error'] = 'ID esperienza non valido';
    header('Location: ../user-dashboard.php#esperienze');
    exit;
}

try {
    $pdo = getDbConnection();
    
    // Verify that the experience belongs to the current user (prevent unauthorized deletion)
    $stmt = $pdo->prepare("SELECT id FROM experiences WHERE id = ? AND user_id = ?");
    $stmt->execute([$experience_id, $user_id]);
    
    if (!$stmt->fetch()) {
        $_SESSION['error'] = 'Esperienza non trovata o non autorizzato';
        header('Location: ../user-dashboard.php#esperienze');
        exit;
    }
    
    // Delete experience with prepared statement
    $stmt = $pdo->prepare("DELETE FROM experiences WHERE id = ? AND user_id = ?");
    $stmt->execute([$experience_id, $user_id]);
    
    $_SESSION['success'] = 'Esperienza eliminata con successo!';
    header('Location: ../user-dashboard.php#esperienze');
    exit;
    
} catch (PDOException $e) {
    error_log("Delete experience error: " . $e->getMessage());
    $_SESSION['error'] = 'Errore durante l\'eliminazione dell\'esperienza';
    header('Location: ../user-dashboard.php#esperienze');
    exit;
}
