<?php
require_once 'config/database.php';
startSecureSession();

// Check if user is logged in
if (!isset($_SESSION['user_id'])) {
    header('Location: index.php');
    exit;
}

// Redirect admin to their dashboard
if ($_SESSION['role'] === 'admin') {
    header('Location: admin-dashboard.php');
    exit;
}

$pdo = getDbConnection();
$user_id = $_SESSION['user_id'];

// Get user data with prepared statement
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = ?");
$stmt->execute([$user_id]);
$user = $stmt->fetch();

// Get CV data
$stmt = $pdo->prepare("SELECT * FROM cv_data WHERE user_id = ?");
$stmt->execute([$user_id]);
$cv_data = $stmt->fetch();

// Get experiences
$stmt = $pdo->prepare("SELECT * FROM experiences WHERE user_id = ? ORDER BY data_inizio DESC");
$stmt->execute([$user_id]);
$experiences = $stmt->fetchAll();

$success = $_SESSION['success'] ?? '';
$error = $_SESSION['error'] ?? '';
unset($_SESSION['success'], $_SESSION['error']);

// Get initials for avatar
$initials = strtoupper(substr($user['nome'], 0, 1) . substr($user['cognome'], 0, 1));
?>
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Studente - Sistema Gestione CV</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="dashboard-wrapper">
        <!-- Sidebar -->
        <aside class="sidebar">
            <div class="sidebar-header">
                <h2>📄 CV Manager</h2>
            </div>

            <div class="sidebar-user">
                <div class="user-avatar"><?php echo htmlspecialchars($initials); ?></div>
                <div class="user-info">
                    <h4><?php echo htmlspecialchars($user['nome'] . ' ' . $user['cognome']); ?></h4>
                    <p><?php echo htmlspecialchars($user['email']); ?></p>
                </div>
            </div>

            <ul class="sidebar-nav">
                <li>
                    <a href="#dati-anagrafici" class="active">
                        <span>👤</span>
                        <span>Dati Anagrafici</span>
                    </a>
                </li>
                <li>
                    <a href="#cv-upload">
                        <span>📤</span>
                        <span>Upload CV</span>
                    </a>
                </li>
                <li>
                    <a href="#esperienze">
                        <span>💼</span>
                        <span>Esperienze</span>
                    </a>
                </li>
                <li>
                    <a href="php/logout.php">
                        <span>🚪</span>
                        <span>Esci</span>
                    </a>
                </li>
            </ul>
        </aside>

        <!-- Main Content -->
        <main class="main-content">
            <div class="dashboard-header">
                <div>
                    <h1>Benvenuto, <?php echo htmlspecialchars($user['nome']); ?>! 👋</h1>
                    <p class="text-muted">Gestisci il tuo curriculum e le tue esperienze</p>
                </div>
                <div>
                    <?php if ($cv_data && $cv_data['cv_file_path']): ?>
                        <a href="php/download-cv.php" class="btn btn-secondary btn-sm">
                            📥 Scarica CV
                        </a>
                    <?php endif; ?>
                </div>
            </div>

            <?php if ($success): ?>
                <div class="alert alert-success">
                    <strong>✓ Successo:</strong> <?php echo htmlspecialchars($success); ?>
                </div>
            <?php endif; ?>

            <?php if ($error): ?>
                <div class="alert alert-error">
                    <strong>⚠️ Errore:</strong> <?php echo htmlspecialchars($error); ?>
                </div>
            <?php endif; ?>

            <!-- Stats Cards -->
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">CV Caricato</div>
                    <div class="stat-value"><?php echo $cv_data && $cv_data['cv_file_path'] ? '✓' : '✗'; ?></div>
                </div>
                <div class="stat-card success">
                    <div class="stat-label">Esperienze Lavorative</div>
                    <div class="stat-value"><?php echo count(array_filter($experiences, fn($e) => $e['tipo'] === 'lavoro')); ?></div>
                </div>
                <div class="stat-card warning">
                    <div class="stat-label">Formazione</div>
                    <div class="stat-value"><?php echo count(array_filter($experiences, fn($e) => $e['tipo'] === 'formazione')); ?></div>
                </div>
            </div>

            <!-- Dati Anagrafici Section -->
            <div class="card" id="dati-anagrafici">
                <div class="card-header">
                    <h2>👤 Dati Anagrafici</h2>
                </div>
                <div class="card-body">
                    <form action="php/update-profile.php" method="POST" data-validate="true">
                        <div class="form-row">
                            <div class="form-group">
                                <label for="nome">Nome <span class="required">*</span></label>
                                <input type="text" id="nome" name="nome" class="form-control" 
                                       value="<?php echo htmlspecialchars($user['nome']); ?>" required>
                            </div>
                            <div class="form-group">
                                <label for="cognome">Cognome <span class="required">*</span></label>
                                <input type="text" id="cognome" name="cognome" class="form-control" 
                                       value="<?php echo htmlspecialchars($user['cognome']); ?>" required>
                            </div>
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label for="email">Email <span class="required">*</span></label>
                                <input type="email" id="email" name="email" class="form-control" 
                                       value="<?php echo htmlspecialchars($user['email']); ?>" required>
                            </div>
                            <div class="form-group">
                                <label for="telefono">Telefono</label>
                                <input type="tel" id="telefono" name="telefono" class="form-control phone" 
                                       value="<?php echo htmlspecialchars($cv_data['telefono'] ?? ''); ?>" 
                                       placeholder="+39 123 456 7890">
                            </div>
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label for="data_nascita">Data di Nascita</label>
                                <input type="date" id="data_nascita" name="data_nascita" class="form-control" 
                                       value="<?php echo htmlspecialchars($cv_data['data_nascita'] ?? ''); ?>">
                            </div>
                            <div class="form-group">
                                <label for="citta">Città</label>
                                <input type="text" id="citta" name="citta" class="form-control" 
                                       value="<?php echo htmlspecialchars($cv_data['citta'] ?? ''); ?>" 
                                       placeholder="Es. Milano">
                            </div>
                        </div>

                        <div class="form-group">
                            <label for="indirizzo">Indirizzo</label>
                            <input type="text" id="indirizzo" name="indirizzo" class="form-control" 
                                   value="<?php echo htmlspecialchars($cv_data['indirizzo'] ?? ''); ?>" 
                                   placeholder="Via, numero civico">
                        </div>

                        <div class="form-group">
                            <label for="linkedin_url">Profilo LinkedIn</label>
                            <input type="url" id="linkedin_url" name="linkedin_url" class="form-control url" 
                                   value="<?php echo htmlspecialchars($cv_data['linkedin_url'] ?? ''); ?>" 
                                   placeholder="https://linkedin.com/in/tuo-profilo">
                            <span class="form-help">Inserisci l'URL completo del tuo profilo LinkedIn</span>
                        </div>

                        <div class="card-footer">
                            <button type="submit" class="btn btn-primary">💾 Salva Modifiche</button>
                        </div>
                    </form>
                </div>
            </div>

            <!-- CV Upload Section -->
            <div class="card" id="cv-upload">
                <div class="card-header">
                    <h2>📤 Upload Curriculum Vitae</h2>
                </div>
                <div class="card-body">
                    <?php if ($cv_data && $cv_data['cv_file_path']): ?>
                        <div class="alert alert-info" style="margin-bottom: 1rem;">
                            <strong>📄 CV Corrente:</strong> 
                            Caricato il <?php echo date('d/m/Y H:i', strtotime($cv_data['cv_uploaded_at'])); ?>
                        </div>
                    <?php endif; ?>

                    <form action="php/upload-cv.php" method="POST" enctype="multipart/form-data" data-validate="true">
                        <div class="form-group">
                            <label for="cv_file">Carica il tuo CV (PDF) <span class="required">*</span></label>
                            <div class="file-input-wrapper">
                                <input type="file" id="cv_file" name="cv_file" accept=".pdf,application/pdf" required>
                                <label for="cv_file" class="file-input-label">
                                    <span>📁</span>
                                    <span>Clicca per selezionare un file PDF</span>
                                </label>
                                <span class="file-name">Nessun file selezionato</span>
                            </div>
                            <span class="form-help">Solo file PDF, dimensione massima: 5MB</span>
                        </div>

                        <div class="card-footer">
                            <button type="submit" class="btn btn-primary">📤 Carica CV</button>
                            <?php if ($cv_data && $cv_data['cv_file_path']): ?>
                                <a href="php/download-cv.php" class="btn btn-secondary">📥 Scarica CV Attuale</a>
                            <?php endif; ?>
                        </div>
                    </form>
                </div>
            </div>

            <!-- Esperienze Section -->
            <div class="card" id="esperienze">
                <div class="card-header">
                    <h2>💼 Esperienze</h2>
                    <button class="btn btn-primary btn-sm" onclick="toggleForm('add-experience-form')">
                        ➕ Aggiungi Esperienza
                    </button>
                </div>
                <div class="card-body">
                    <!-- Add Experience Form (Hidden by default) -->
                    <div id="add-experience-form" style="display: none; margin-bottom: 2rem; padding: 1.5rem; background: var(--light); border-radius: var(--radius);">
                        <h3>Nuova Esperienza</h3>
                        <form action="php/add-experience.php" method="POST" data-validate="true">
                            <div class="form-group">
                                <label for="tipo">Tipo <span class="required">*</span></label>
                                <select id="tipo" name="tipo" class="form-control" required>
                                    <option value="">Seleziona...</option>
                                    <option value="lavoro">💼 Esperienza Lavorativa</option>
                                    <option value="formazione">🎓 Formazione</option>
                                </select>
                            </div>

                            <div class="form-group">
                                <label for="titolo">Titolo/Posizione <span class="required">*</span></label>
                                <input type="text" id="titolo" name="titolo" class="form-control" required 
                                       placeholder="Es. Sviluppatore Web Junior">
                            </div>

                            <div class="form-group">
                                <label for="azienda_istituto">Azienda/Istituto <span class="required">*</span></label>
                                <input type="text" id="azienda_istituto" name="azienda_istituto" class="form-control" required 
                                       placeholder="Es. Tech Company S.r.l.">
                            </div>

                            <div class="form-row">
                                <div class="form-group">
                                    <label for="data_inizio">Data Inizio <span class="required">*</span></label>
                                    <input type="date" id="data_inizio" name="data_inizio" class="form-control" required>
                                </div>
                                <div class="form-group">
                                    <label for="data_fine">Data Fine</label>
                                    <input type="date" id="data_fine" name="data_fine" class="form-control">
                                </div>
                            </div>

                            <div class="form-group">
                                <label>
                                    <input type="checkbox" name="is_current" value="1">
                                    Attualmente in corso
                                </label>
                            </div>

                            <div class="form-group">
                                <label for="descrizione">Descrizione</label>
                                <textarea id="descrizione" name="descrizione" class="form-control" 
                                          placeholder="Descrivi le tue responsabilità e risultati..."></textarea>
                            </div>

                            <div style="display: flex; gap: 0.5rem;">
                                <button type="submit" class="btn btn-primary">💾 Salva Esperienza</button>
                                <button type="button" class="btn btn-outline" onclick="toggleForm('add-experience-form')">Annulla</button>
                            </div>
                        </form>
                    </div>

                    <!-- Experience List -->
                    <?php if (empty($experiences)): ?>
                        <div class="empty-state">
                            <div class="empty-state-icon">📋</div>
                            <h3>Nessuna esperienza ancora</h3>
                            <p>Aggiungi le tue esperienze lavorative e formative per completare il tuo profilo</p>
                        </div>
                    <?php else: ?>
                        <ul class="list">
                            <?php foreach ($experiences as $exp): ?>
                                <li class="list-item">
                                    <div class="list-item-content">
                                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                                            <span><?php echo $exp['tipo'] === 'lavoro' ? '💼' : '🎓'; ?></span>
                                            <h4><?php echo htmlspecialchars($exp['titolo']); ?></h4>
                                            <?php if ($exp['is_current']): ?>
                                                <span class="badge badge-success">In corso</span>
                                            <?php endif; ?>
                                        </div>
                                        <p style="font-weight: 600; color: var(--primary);">
                                            <?php echo htmlspecialchars($exp['azienda_istituto']); ?>
                                        </p>
                                        <div class="list-item-meta">
                                            <span>📅 <?php echo date('m/Y', strtotime($exp['data_inizio'])); ?></span>
                                            <span>→</span>
                                            <span><?php echo $exp['is_current'] ? 'Presente' : date('m/Y', strtotime($exp['data_fine'])); ?></span>
                                        </div>
                                        <?php if ($exp['descrizione']): ?>
                                            <p style="margin-top: 0.5rem;"><?php echo htmlspecialchars($exp['descrizione']); ?></p>
                                        <?php endif; ?>
                                    </div>
                                    <div class="table-actions">
                                        <a href="php/delete-experience.php?id=<?php echo $exp['id']; ?>" 
                                           class="btn btn-danger btn-sm" 
                                           data-confirm="Sei sicuro di voler eliminare questa esperienza?">
                                            🗑️ Elimina
                                        </a>
                                    </div>
                                </li>
                            <?php endforeach; ?>
                        </ul>
                    <?php endif; ?>
                </div>
            </div>
        </main>
    </div>

    <script src="js/validation.js"></script>
    <script>
        function toggleForm(formId) {
            const form = document.getElementById(formId);
            if (form.style.display === 'none') {
                form.style.display = 'block';
                form.scrollIntoView({ behavior: 'smooth', block: 'start' });
            } else {
                form.style.display = 'none';
            }
        }

        // Smooth scrolling for sidebar links
        document.querySelectorAll('.sidebar-nav a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    
                    // Update active state
                    document.querySelectorAll('.sidebar-nav a').forEach(a => a.classList.remove('active'));
                    this.classList.add('active');
                }
            });
        });
    </script>
</body>
</html>
