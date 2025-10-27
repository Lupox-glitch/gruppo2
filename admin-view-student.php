<?php
require_once 'config/database.php';
startSecureSession();

// Check if user is logged in and is admin
if (!isset($_SESSION['user_id']) || $_SESSION['role'] !== 'admin') {
    header('Location: index.php');
    exit;
}

$student_id = filter_input(INPUT_GET, 'id', FILTER_VALIDATE_INT);
if (!$student_id) {
    header('Location: admin-dashboard.php');
    exit;
}

$pdo = getDbConnection();

// Get student data
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = ? AND role = 'student'");
$stmt->execute([$student_id]);
$student = $stmt->fetch();

if (!$student) {
    $_SESSION['error'] = 'Studente non trovato';
    header('Location: admin-dashboard.php');
    exit;
}

// Get CV data
$stmt = $pdo->prepare("SELECT * FROM cv_data WHERE user_id = ?");
$stmt->execute([$student_id]);
$cv_data = $stmt->fetch();

// Get experiences
$stmt = $pdo->prepare("SELECT * FROM experiences WHERE user_id = ? ORDER BY data_inizio DESC");
$stmt->execute([$student_id]);
$experiences = $stmt->fetchAll();

$initials = strtoupper(substr($student['nome'], 0, 1) . substr($student['cognome'], 0, 1));
?>
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Profilo Studente - <?php echo htmlspecialchars($student['nome'] . ' ' . $student['cognome']); ?></title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="dashboard-wrapper">
        <!-- Sidebar -->
        <aside class="sidebar">
            <div class="sidebar-header">
                <h2>🛡️ Admin Panel</h2>
            </div>

            <div class="sidebar-user">
                <div class="user-avatar"><?php echo htmlspecialchars($initials); ?></div>
                <div class="user-info">
                    <h4><?php echo htmlspecialchars($student['nome'] . ' ' . $student['cognome']); ?></h4>
                    <p><?php echo htmlspecialchars($student['email']); ?></p>
                </div>
            </div>

            <ul class="sidebar-nav">
                <li>
                    <a href="admin-dashboard.php">
                        <span>⬅️</span>
                        <span>Torna alla Dashboard</span>
                    </a>
                </li>
                <li>
                    <a href="#dati-personali" class="active">
                        <span>👤</span>
                        <span>Dati Personali</span>
                    </a>
                </li>
                <li>
                    <a href="#cv-documento">
                        <span>📄</span>
                        <span>Curriculum</span>
                    </a>
                </li>
                <li>
                    <a href="#esperienze">
                        <span>💼</span>
                        <span>Esperienze</span>
                    </a>
                </li>
            </ul>
        </aside>

        <!-- Main Content -->
        <main class="main-content">
            <div class="dashboard-header">
                <div>
                    <h1>Profilo di <?php echo htmlspecialchars($student['nome'] . ' ' . $student['cognome']); ?></h1>
                    <p class="text-muted">Visualizzazione dettagliata del profilo studente</p>
                </div>
                <div>
                    <a href="admin-dashboard.php" class="btn btn-outline btn-sm">⬅️ Indietro</a>
                    <?php if ($cv_data && $cv_data['cv_file_path']): ?>
                        <a href="php/admin-download-cv.php?user_id=<?php echo $student_id; ?>" class="btn btn-secondary btn-sm">
                            📥 Scarica CV
                        </a>
                    <?php endif; ?>
                </div>
            </div>

            <!-- Stats -->
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Registrato il</div>
                    <div class="stat-value" style="font-size: 1.25rem;">
                        <?php echo date('d/m/Y', strtotime($student['created_at'])); ?>
                    </div>
                </div>
                <div class="stat-card <?php echo $cv_data && $cv_data['cv_file_path'] ? 'success' : 'warning'; ?>">
                    <div class="stat-label">CV</div>
                    <div class="stat-value"><?php echo $cv_data && $cv_data['cv_file_path'] ? '✓' : '✗'; ?></div>
                </div>
                <div class="stat-card success">
                    <div class="stat-label">Esperienze</div>
                    <div class="stat-value"><?php echo count($experiences); ?></div>
                </div>
            </div>

            <!-- Dati Personali -->
            <div class="card" id="dati-personali">
                <div class="card-header">
                    <h2>👤 Dati Personali</h2>
                </div>
                <div class="card-body">
                    <div class="grid-2">
                        <div>
                            <p><strong>Nome Completo:</strong></p>
                            <p><?php echo htmlspecialchars($student['nome'] . ' ' . $student['cognome']); ?></p>
                        </div>
                        <div>
                            <p><strong>Email:</strong></p>
                            <p><?php echo htmlspecialchars($student['email']); ?></p>
                        </div>
                        <div>
                            <p><strong>Telefono:</strong></p>
                            <p><?php echo $cv_data && $cv_data['telefono'] ? htmlspecialchars($cv_data['telefono']) : '<span class="text-muted">Non fornito</span>'; ?></p>
                        </div>
                        <div>
                            <p><strong>Data di Nascita:</strong></p>
                            <p><?php echo $cv_data && $cv_data['data_nascita'] ? date('d/m/Y', strtotime($cv_data['data_nascita'])) : '<span class="text-muted">Non fornita</span>'; ?></p>
                        </div>
                        <div>
                            <p><strong>Città:</strong></p>
                            <p><?php echo $cv_data && $cv_data['citta'] ? htmlspecialchars($cv_data['citta']) : '<span class="text-muted">Non fornita</span>'; ?></p>
                        </div>
                        <div>
                            <p><strong>Indirizzo:</strong></p>
                            <p><?php echo $cv_data && $cv_data['indirizzo'] ? htmlspecialchars($cv_data['indirizzo']) : '<span class="text-muted">Non fornito</span>'; ?></p>
                        </div>
                    </div>
                    <?php if ($cv_data && $cv_data['linkedin_url']): ?>
                        <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--border);">
                            <p><strong>LinkedIn:</strong></p>
                            <p><a href="<?php echo htmlspecialchars($cv_data['linkedin_url']); ?>" target="_blank" rel="noopener">
                                <?php echo htmlspecialchars($cv_data['linkedin_url']); ?> 🔗
                            </a></p>
                        </div>
                    <?php endif; ?>
                </div>
            </div>

            <!-- CV Document -->
            <div class="card" id="cv-documento">
                <div class="card-header">
                    <h2>📄 Curriculum Vitae</h2>
                </div>
                <div class="card-body">
                    <?php if ($cv_data && $cv_data['cv_file_path']): ?>
                        <div class="alert alert-success">
                            <div>
                                <strong>✓ CV Caricato</strong>
                                <p style="margin: 0.5rem 0 0 0;">
                                    Caricato il <?php echo date('d/m/Y \a\l\l\e H:i', strtotime($cv_data['cv_uploaded_at'])); ?>
                                </p>
                            </div>
                        </div>
                        <div style="margin-top: 1rem;">
                            <a href="php/admin-download-cv.php?user_id=<?php echo $student_id; ?>" class="btn btn-primary">
                                📥 Scarica CV (PDF)
                            </a>
                        </div>
                    <?php else: ?>
                        <div class="alert alert-warning">
                            <strong>⚠️ CV Non Caricato</strong>
                            <p style="margin: 0.5rem 0 0 0;">Lo studente non ha ancora caricato il proprio curriculum</p>
                        </div>
                    <?php endif; ?>
                </div>
            </div>

            <!-- Esperienze -->
            <div class="card" id="esperienze">
                <div class="card-header">
                    <h2>💼 Esperienze</h2>
                    <span class="badge badge-primary"><?php echo count($experiences); ?> totali</span>
                </div>
                <div class="card-body">
                    <?php if (empty($experiences)): ?>
                        <div class="empty-state">
                            <div class="empty-state-icon">📋</div>
                            <h3>Nessuna esperienza registrata</h3>
                            <p>Lo studente non ha ancora aggiunto esperienze lavorative o formative</p>
                        </div>
                    <?php else: ?>
                        <!-- Work Experiences -->
                        <?php 
                        $work_exp = array_filter($experiences, fn($e) => $e['tipo'] === 'lavoro');
                        if (!empty($work_exp)): 
                        ?>
                            <h3 style="margin-bottom: 1rem;">💼 Esperienze Lavorative</h3>
                            <ul class="list" style="margin-bottom: 2rem;">
                                <?php foreach ($work_exp as $exp): ?>
                                    <li class="list-item">
                                        <div class="list-item-content">
                                            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
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
                                                <p style="margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid var(--border);">
                                                    <?php echo nl2br(htmlspecialchars($exp['descrizione'])); ?>
                                                </p>
                                            <?php endif; ?>
                                        </div>
                                    </li>
                                <?php endforeach; ?>
                            </ul>
                        <?php endif; ?>

                        <!-- Education -->
                        <?php 
                        $education = array_filter($experiences, fn($e) => $e['tipo'] === 'formazione');
                        if (!empty($education)): 
                        ?>
                            <h3 style="margin-bottom: 1rem;">🎓 Formazione</h3>
                            <ul class="list">
                                <?php foreach ($education as $exp): ?>
                                    <li class="list-item">
                                        <div class="list-item-content">
                                            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
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
                                                <p style="margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid var(--border);">
                                                    <?php echo nl2br(htmlspecialchars($exp['descrizione'])); ?>
                                                </p>
                                            <?php endif; ?>
                                        </div>
                                    </li>
                                <?php endforeach; ?>
                            </ul>
                        <?php endif; ?>
                    <?php endif; ?>
                </div>
            </div>
        </main>
    </div>

    <script src="js/validation.js"></script>
    <script>
        // Smooth scrolling
        document.querySelectorAll('.sidebar-nav a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    document.querySelectorAll('.sidebar-nav a').forEach(a => a.classList.remove('active'));
                    this.classList.add('active');
                }
            });
        });
    </script>
</body>
</html>
