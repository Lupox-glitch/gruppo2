# 🚀 Guida Rapida - Setup del Sistema CV

## Setup Veloce (5 minuti)

### 1️⃣ Database Setup

Apri **phpMyAdmin** o **MySQL Command Line** e esegui:

```bash
# Importa il database
mysql -u root -p < database.sql
```

Oppure in phpMyAdmin:
1. Crea database `cv_management`
2. Importa il file `database.sql`

### 2️⃣ Configura Credenziali

Apri `config/database.php` e modifica (se necessario):

```php
define('DB_HOST', 'localhost');
define('DB_NAME', 'cv_management');
define('DB_USER', 'root');
define('DB_PASS', '');  // La tua password MySQL
```

### 3️⃣ Avvia il Server

**Opzione A - XAMPP:**
1. Avvia Apache e MySQL
2. Vai a: `http://localhost/gruppo2/`

**Opzione B - PHP Built-in:**
```powershell
cd e:\gruppo2
php -S localhost:8000
```
Vai a: `http://localhost:8000/`

### 4️⃣ Test Login

**Account Admin:**
- Email: `admin@cvmanagement.it`
- Password: `admin123`

**Account Studente:**
- Email: `student@test.it`
- Password: `student123`

## ✅ Checklist Veloce

- [ ] MySQL/MariaDB installato e avviato
- [ ] PHP 7.4+ installato
- [ ] Database `cv_management` creato e importato
- [ ] Credenziali in `config/database.php` corrette
- [ ] Cartella `uploads/` scrivibile
- [ ] Server web avviato (Apache o PHP built-in)
- [ ] Login funzionante con account test

## 🆘 Problemi Comuni

**Errore connessione database:**
```
✓ Verifica MySQL sia avviato
✓ Controlla credenziali in config/database.php
✓ Esegui: mysql -u root -p < database.sql
```

**Errore upload CV:**
```
✓ Verifica cartella uploads/ esista
✓ Su Linux: chmod 755 uploads/
✓ Aumenta upload_max_filesize in php.ini
```

**Pagina bianca:**
```
✓ Abilita errori: ini_set('display_errors', 1);
✓ Controlla log: xampp/apache/logs/error.log
✓ Verifica estensioni PHP: PDO, PDO_MySQL
```

## 📋 Comandi Utili

```bash
# Verifica versione PHP
php -v

# Controlla estensioni PHP
php -m | grep -i pdo

# Backup database
mysqldump -u root -p cv_management > backup_$(date +%Y%m%d).sql

# Permessi uploads (Linux)
chmod -R 755 uploads/
chown -R www-data:www-data uploads/

# Test server PHP
php -S localhost:8000 -t .
```

## 🎯 Prossimi Passi

1. **Testa tutte le funzioni:**
   - [ ] Registrazione nuovo utente
   - [ ] Upload CV (PDF)
   - [ ] Aggiunta esperienze
   - [ ] Dashboard admin
   
2. **Personalizza:**
   - Cambia password account test
   - Modifica logo/colori in `css/style.css`
   - Aggiungi email admin in database

3. **Deploy:**
   - Leggi sezione "Deployment in Produzione" nel README.md
   - Configura HTTPS
   - Backup automatici

## 📖 Documentazione Completa

Consulta `README.md` per:
- Documentazione completa
- Sicurezza e best practices
- Risoluzione problemi avanzata
- API endpoints

---

**Hai bisogno di aiuto?** Controlla i log di errore e la documentazione completa!
