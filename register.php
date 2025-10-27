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

$error = $_SESSION['register_error'] ?? '';
unset($_SESSION['register_error']);
?>
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Registrazione - Sistema Gestione CV</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="auth-container">
        <div class="auth-card">
            <div class="auth-header">
                <h1>📝 Crea un Account</h1>
                <p>Registrati per iniziare a gestire il tuo CV</p>
            </div>

            <?php if ($error): ?>
                <div class="alert alert-error">
                    <strong>⚠️ Errore:</strong> <?php echo htmlspecialchars($error); ?>
                </div>
            <?php endif; ?>

            <form action="php/register.php" method="POST" data-validate="true">
                <div class="form-row">
                    <div class="form-group">
                        <label for="nome">
                            Nome
                            <span class="required">*</span>
                        </label>
                        <input 
                            type="text" 
                            id="nome" 
                            name="nome" 
                            class="form-control" 
                            required 
                            minlength="2"
                            maxlength="100"
                            autocomplete="given-name"
                            placeholder="Mario"
                        >
                    </div>

                    <div class="form-group">
                        <label for="cognome">
                            Cognome
                            <span class="required">*</span>
                        </label>
                        <input 
                            type="text" 
                            id="cognome" 
                            name="cognome" 
                            class="form-control" 
                            required 
                            minlength="2"
                            maxlength="100"
                            autocomplete="family-name"
                            placeholder="Rossi"
                        >
                    </div>
                </div>

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
                    <span class="form-help">Utilizza un indirizzo email valido</span>
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
                        class="form-control password-strength" 
                        required 
                        minlength="8"
                        autocomplete="new-password"
                        placeholder="Minimo 8 caratteri"
                    >
                    <span class="form-help">Deve contenere almeno 8 caratteri, una maiuscola, una minuscola e un numero</span>
                </div>

                <div class="form-group">
                    <label for="password_confirm">
                        Conferma Password
                        <span class="required">*</span>
                    </label>
                    <input 
                        type="password" 
                        id="password_confirm" 
                        name="password_confirm" 
                        class="form-control password-confirm" 
                        required 
                        autocomplete="new-password"
                        placeholder="Ripeti la password"
                    >
                </div>

                <button type="submit" class="btn btn-primary btn-block">
                    Registrati
                </button>
            </form>

            <div style="text-align: center; margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid var(--border);">
                <p class="text-muted">Hai già un account?</p>
                <a href="index.php" class="btn btn-outline" style="margin-top: 0.5rem;">
                    Accedi
                </a>
            </div>
        </div>
    </div>

    <script src="js/validation.js"></script>
</body>
</html>
