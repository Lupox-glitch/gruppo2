<?php
require_once 'config/database.php';
startSecureSession();

// Redirect if already logged in
if (isset($_SESSION['user_id'])) {
    if ($_SESSION['role'] === 'admin') {
        header('Location: admin-dashboard.php');
    } else {
        header('Location: user-dashboard.php');
    }
    exit;
}

$error = $_SESSION['login_error'] ?? '';
$success = $_SESSION['login_success'] ?? '';
unset($_SESSION['login_error'], $_SESSION['login_success']);
?>
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Sistema Gestione CV</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="auth-container">
        <div class="auth-card">
            <div class="auth-header">
                <h1>📄 Sistema Gestione CV</h1>
                <p>Accedi al tuo account per gestire il tuo curriculum</p>
            </div>

            <?php if ($error): ?>
                <div class="alert alert-error">
                    <strong>⚠️ Errore:</strong> <?php echo htmlspecialchars($error); ?>
                </div>
            <?php endif; ?>

            <?php if ($success): ?>
                <div class="alert alert-success">
                    <strong>✓ Successo:</strong> <?php echo htmlspecialchars($success); ?>
                </div>
            <?php endif; ?>

            <form action="php/login.php" method="POST" data-validate="true">
                <div class="form-group">
                    <label for="email">
                        Email
                        <span class="required">*</span>
                    </label>
                    <input 
                        type="email" 
                        id="email" 
                        name="email" 
                        class="form-control" 
                        required 
                        autocomplete="email"
                        placeholder="tua@email.it"
                    >
                </div>

                <div class="form-group">
                    <label for="password">
                        Password
                        <span class="required">*</span>
                    </label>
                    <input 
                        type="password" 
                        id="password" 
                        name="password" 
                        class="form-control" 
                        required 
                        autocomplete="current-password"
                        placeholder="Inserisci la tua password"
                    >
                </div>

                <button type="submit" class="btn btn-primary btn-block">
                    Accedi
                </button>
            </form>

            <div style="text-align: center; margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid var(--border);">
                <p class="text-muted">Non hai un account?</p>
                <a href="register.php" class="btn btn-outline" style="margin-top: 0.5rem;">
                    Registrati
                </a>
            </div>

            <div style="margin-top: 2rem; padding: 1rem; background: var(--light); border-radius: var(--radius); font-size: 0.875rem;">
                <strong>Account di test:</strong><br>
                <strong>Admin:</strong> admin@cvmanagement.it / admin123<br>
                <strong>Studente:</strong> student@test.it / student123
            </div>
        </div>
    </div>

    <script src="js/validation.js"></script>
</body>
</html>
