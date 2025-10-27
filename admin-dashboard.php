<?php
require_once 'config/database.php';
startSecureSession();

// Check if user is logged in and is admin
if (!isset($_SESSION['user_id']) || $_SESSION['role'] !== 'admin') {
    header('Location: index.php');
    exit;
}

$pdo = getDbConnection();

// Get all users with their CV data
$stmt = $pdo->prepare("
    SELECT u.*, 
           cv.cv_file_path, 
           cv.cv_uploaded_at,
           cv.telefono,
           COUNT(DISTINCT e.id) as total_experiences
    FROM users u
    LEFT JOIN cv_data cv ON u.id = cv.user_id
    LEFT JOIN experiences e ON u.id = e.user_id
    WHERE u.role = 'student'
    GROUP BY u.id
    ORDER BY u.created_at DESC
");
$stmt->execute();
$students = $stmt->fetchAll();

// Get statistics
$stmt = $pdo->query("SELECT COUNT(*) as total FROM users WHERE role = 'student'");
$total_students = $stmt->fetch()['total'];

$stmt = $pdo->query("SELECT COUNT(DISTINCT user_id) as total FROM cv_data WHERE cv_file_path IS NOT NULL");
$students_with_cv = $stmt->fetch()['total'];

$stmt = $pdo->query("SELECT COUNT(*) as total FROM experiences");
$total_experiences = $stmt->fetch()['total'];

$success = $_SESSION['success'] ?? '';
$error = $_SESSION['error'] ?? '';
unset($_SESSION['success'], $_SESSION['error']);

$admin_user = $pdo->prepare("SELECT * FROM users WHERE id = ?");
$admin_user->execute([$_SESSION['user_id']]);
$admin = $admin_user->fetch();
$initials = strtoupper(substr($admin['nome'], 0, 1) . substr($admin['cognome'], 0, 1));
?>
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Admin - Sistema Gestione CV</title>
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
                <div class="user-avatar" style="background: var(--danger);"><?php echo htmlspecialchars($initials); ?></div>
                <div class="user-info">
                    <h4><?php echo htmlspecialchars($admin['nome'] . ' ' . $admin['cognome']); ?></h4>
                    <p><span class="badge badge-danger">Amministratore</span></p>
                </div>
            </div>

            <ul class="sidebar-nav">
                <li>
                    <a href="#overview" class="active">
                        <span>📊</span>
                        <span>Panoramica</span>
                    </a>
                </li>
                <li>
                    <a href="#students">
                        <span>👥</span>
                        <span>Studenti</span>
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
                    <h1>Dashboard Amministratore 🛡️</h1>
                    <p class="text-muted">Gestisci utenti e visualizza i documenti caricati</p>
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

            <!-- Statistics -->
            <div class="stats-grid" id="overview">
                <div class="stat-card">
                    <div class="stat-label">Studenti Totali</div>
                    <div class="stat-value"><?php echo $total_students; ?></div>
                </div>
                <div class="stat-card success">
                    <div class="stat-label">CV Caricati</div>
                    <div class="stat-value"><?php echo $students_with_cv; ?></div>
                </div>
                <div class="stat-card warning">
                    <div class="stat-label">Esperienze Totali</div>
                    <div class="stat-value"><?php echo $total_experiences; ?></div>
                </div>
                <div class="stat-card danger">
                    <div class="stat-label">Profili Incompleti</div>
                    <div class="stat-value"><?php echo $total_students - $students_with_cv; ?></div>
                </div>
            </div>

            <!-- Students Table -->
            <div class="card" id="students">
                <div class="card-header">
                    <h2>👥 Elenco Studenti</h2>
                    <span class="text-muted"><?php echo count($students); ?> studenti registrati</span>
                </div>
                <div class="card-body">
                    <?php if (empty($students)): ?>
                        <div class="empty-state">
                            <div class="empty-state-icon">👥</div>
                            <h3>Nessuno studente registrato</h3>
                            <p>Gli studenti registrati appariranno qui</p>
                        </div>
                    <?php else: ?>
                        <div class="table-wrapper">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Studente</th>
                                        <th>Email</th>
                                        <th>Telefono</th>
                                        <th>CV</th>
                                        <th>Esperienze</th>
                                        <th>Registrato</th>
                                        <th>Azioni</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <?php foreach ($students as $student): ?>
                                        <tr>
                                            <td>
                                                <strong><?php echo htmlspecialchars($student['nome'] . ' ' . $student['cognome']); ?></strong>
                                            </td>
                                            <td><?php echo htmlspecialchars($student['email']); ?></td>
                                            <td><?php echo $student['telefono'] ? htmlspecialchars($student['telefono']) : '<span class="text-muted">-</span>'; ?></td>
                                            <td>
                                                <?php if ($student['cv_file_path']): ?>
                                                    <span class="badge badge-success">✓ Caricato</span>
                                                    <br><small class="text-muted"><?php echo date('d/m/Y', strtotime($student['cv_uploaded_at'])); ?></small>
                                                <?php else: ?>
                                                    <span class="badge badge-warning">✗ Non caricato</span>
                                                <?php endif; ?>
                                            </td>
                                            <td>
                                                <span class="badge badge-primary"><?php echo $student['total_experiences']; ?></span>
                                            </td>
                                            <td>
                                                <small class="text-muted"><?php echo date('d/m/Y', strtotime($student['created_at'])); ?></small>
                                            </td>
                                            <td>
                                                <div class="table-actions">
                                                    <a href="admin-view-student.php?id=<?php echo $student['id']; ?>" 
                                                       class="btn btn-primary btn-sm">
                                                        👁️ Visualizza
                                                    </a>
                                                    <?php if ($student['cv_file_path']): ?>
                                                        <a href="php/admin-download-cv.php?user_id=<?php echo $student['id']; ?>" 
                                                           class="btn btn-secondary btn-sm">
                                                            📥 CV
                                                        </a>
                                                    <?php endif; ?>
                                                </div>
                                            </td>
                                        </tr>
                                    <?php endforeach; ?>
                                </tbody>
                            </table>
                        </div>
                    <?php endif; ?>
                </div>
            </div>
        </main>
    </div>

    <script src="js/validation.js"></script>
    <script>
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
