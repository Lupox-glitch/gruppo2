<?php
/**
 * CV Upload Handler
 * Secure file upload with validation
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

// Check if file was uploaded
if (!isset($_FILES['cv_file']) || $_FILES['cv_file']['error'] === UPLOAD_ERR_NO_FILE) {
    $_SESSION['error'] = 'Nessun file selezionato';
    header('Location: ../user-dashboard.php#cv-upload');
    exit;
}

$file = $_FILES['cv_file'];

// Check for upload errors
if ($file['error'] !== UPLOAD_ERR_OK) {
    $_SESSION['error'] = 'Errore durante il caricamento del file';
    header('Location: ../user-dashboard.php#cv-upload');
    exit;
}

// Validate file type (PDF only)
$finfo = finfo_open(FILEINFO_MIME_TYPE);
$mime_type = finfo_file($finfo, $file['tmp_name']);
finfo_close($finfo);

if ($mime_type !== 'application/pdf') {
    $_SESSION['error'] = 'Tipo di file non valido. Solo file PDF sono consentiti';
    header('Location: ../user-dashboard.php#cv-upload');
    exit;
}

// Validate file size (max 5MB)
$max_size = 5 * 1024 * 1024; // 5MB in bytes
if ($file['size'] > $max_size) {
    $_SESSION['error'] = 'Il file è troppo grande. Dimensione massima: 5MB';
    header('Location: ../user-dashboard.php#cv-upload');
    exit;
}

try {
    $pdo = getDbConnection();
    
    // Get user email for filename
    $stmt = $pdo->prepare("SELECT email FROM users WHERE id = ?");
    $stmt->execute([$user_id]);
    $user = $stmt->fetch();
    
    // Generate secure filename
    $extension = '.pdf';
    $filename = 'cv_' . $user_id . '_' . date('YmdHis') . $extension;
    $upload_dir = '../uploads/cv/';
    $upload_path = $upload_dir . $filename;
    
    // Ensure upload directory exists
    if (!is_dir($upload_dir)) {
        mkdir($upload_dir, 0755, true);
    }
    
    // Get old CV path to delete it
    $stmt = $pdo->prepare("SELECT cv_file_path FROM cv_data WHERE user_id = ?");
    $stmt->execute([$user_id]);
    $old_cv = $stmt->fetch();
    
    // Move uploaded file
    if (!move_uploaded_file($file['tmp_name'], $upload_path)) {
        $_SESSION['error'] = 'Errore durante il salvataggio del file';
        header('Location: ../user-dashboard.php#cv-upload');
        exit;
    }
    
    // Delete old CV file if exists
    if ($old_cv && $old_cv['cv_file_path'] && file_exists('../' . $old_cv['cv_file_path'])) {
        unlink('../' . $old_cv['cv_file_path']);
    }
    
    // Update database with prepared statement
    $relative_path = 'uploads/cv/' . $filename;
    
    $stmt = $pdo->prepare("SELECT id FROM cv_data WHERE user_id = ?");
    $stmt->execute([$user_id]);
    $cv_exists = $stmt->fetch();
    
    if ($cv_exists) {
        // Update existing record
        $stmt = $pdo->prepare("
            UPDATE cv_data 
            SET cv_file_path = ?, cv_uploaded_at = NOW() 
            WHERE user_id = ?
        ");
        $stmt->execute([$relative_path, $user_id]);
    } else {
        // Insert new record
        $stmt = $pdo->prepare("
            INSERT INTO cv_data (user_id, cv_file_path, cv_uploaded_at) 
            VALUES (?, ?, NOW())
        ");
        $stmt->execute([$user_id, $relative_path]);
    }
    
    $_SESSION['success'] = 'CV caricato con successo!';
    header('Location: ../user-dashboard.php#cv-upload');
    exit;
    
} catch (Exception $e) {
    error_log("CV upload error: " . $e->getMessage());
    $_SESSION['error'] = 'Errore durante il caricamento del CV';
    header('Location: ../user-dashboard.php#cv-upload');
    exit;
}
