<?php
/**
 * Logout Handler
 */

require_once '../config/database.php';
startSecureSession();

// Unset all session variables
$_SESSION = [];

// Destroy the session cookie
if (isset($_COOKIE[session_name()])) {
    setcookie(session_name(), '', time() - 3600, '/');
}

// Destroy the session
session_destroy();

// Redirect to login page
header('Location: ../index.php');
exit;
