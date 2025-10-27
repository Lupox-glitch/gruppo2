<?php
/**
 * CV Download Handler
 * Secure file download for users
 */

require_once '../config/database.php';
startSecureSession();

// Check if user is logged in
if (!isset($_SESSION['user_id'])) {
    header('Location: ../index.php');
    exit;
}

$user_id = $_SESSION['user_id'];

try {
    $pdo = getDbConnection();
    
    // Get CV file path with prepared statement
    $stmt = $pdo->prepare("SELECT cv_file_path FROM cv_data WHERE user_id = ?");
    $stmt->execute([$user_id]);
    $cv_data = $stmt->fetch();
    
    if (!$cv_data || !$cv_data['cv_file_path']) {
        $_SESSION['error'] = 'Nessun CV caricato';
        header('Location: ../user-dashboard.php');
        exit;
    }
    
    $file_path = '../' . $cv_data['cv_file_path'];
    
    // Check if file exists
    if (!file_exists($file_path)) {
        $_SESSION['error'] = 'File CV non trovato';
        header('Location: ../user-dashboard.php');
        exit;
    }
    
    // Get user info for filename
    $stmt = $pdo->prepare("SELECT nome, cognome FROM users WHERE id = ?");
    $stmt->execute([$user_id]);
    $user = $stmt->fetch();
    
    // Set headers for download
    $download_name = 'CV_' . $user['nome'] . '_' . $user['cognome'] . '.pdf';
    
    header('Content-Type: application/pdf');
    header('Content-Disposition: attachment; filename="' . $download_name . '"');
    header('Content-Length: ' . filesize($file_path));
    header('Cache-Control: no-cache, must-revalidate');
    header('Pragma: no-cache');
    
    // Output file
    readfile($file_path);
    exit;
    
} catch (Exception $e) {
    error_log("CV download error: " . $e->getMessage());
    $_SESSION['error'] = 'Errore durante il download del CV';
    header('Location: ../user-dashboard.php');
    exit;
}
