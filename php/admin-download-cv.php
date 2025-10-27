<?php
/**
 * Admin CV Download Handler
 * Allows admin to download any student's CV
 */

require_once '../config/database.php';
startSecureSession();

// Check if user is logged in and is admin
if (!isset($_SESSION['user_id']) || $_SESSION['role'] !== 'admin') {
    header('Location: ../index.php');
    exit;
}

$student_id = filter_input(INPUT_GET, 'user_id', FILTER_VALIDATE_INT);

if (!$student_id) {
    $_SESSION['error'] = 'ID studente non valido';
    header('Location: ../admin-dashboard.php');
    exit;
}

try {
    $pdo = getDbConnection();
    
    // Get CV file path with prepared statement
    $stmt = $pdo->prepare("
        SELECT cv.cv_file_path, u.nome, u.cognome 
        FROM cv_data cv
        JOIN users u ON cv.user_id = u.id
        WHERE cv.user_id = ? AND u.role = 'student'
    ");
    $stmt->execute([$student_id]);
    $data = $stmt->fetch();
    
    if (!$data || !$data['cv_file_path']) {
        $_SESSION['error'] = 'CV non trovato per questo studente';
        header('Location: ../admin-dashboard.php');
        exit;
    }
    
    $file_path = '../' . $data['cv_file_path'];
    
    // Check if file exists
    if (!file_exists($file_path)) {
        $_SESSION['error'] = 'File CV non trovato sul server';
        header('Location: ../admin-dashboard.php');
        exit;
    }
    
    // Set headers for download
    $download_name = 'CV_' . $data['nome'] . '_' . $data['cognome'] . '.pdf';
    
    header('Content-Type: application/pdf');
    header('Content-Disposition: attachment; filename="' . $download_name . '"');
    header('Content-Length: ' . filesize($file_path));
    header('Cache-Control: no-cache, must-revalidate');
    header('Pragma: no-cache');
    
    // Output file
    readfile($file_path);
    exit;
    
} catch (Exception $e) {
    error_log("Admin CV download error: " . $e->getMessage());
    $_SESSION['error'] = 'Errore durante il download del CV';
    header('Location: ../admin-dashboard.php');
    exit;
}
