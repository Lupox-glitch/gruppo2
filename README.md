# 📄 Sistema di Gestione CV Online per Studenti

Sistema web completo e sicuro per la gestione dei curriculum vitae degli studenti, con dashboard separate per studenti e amministratori.

## 🎯 Caratteristiche Principali

### Per gli Studenti
- ✅ **Registrazione e Login Sicuri** - Sistema di autenticazione con password hashate
- 📝 **Gestione Dati Anagrafici** - Aggiornamento di informazioni personali, contatti e LinkedIn
- 📤 **Upload CV (PDF)** - Caricamento sicuro del curriculum in formato PDF
- 💼 **Gestione Esperienze** - Aggiunta di esperienze lavorative e formative
- 📥 **Download CV** - Possibilità di scaricare il proprio CV caricato

### Per gli Amministratori
- 👥 **Visualizzazione Utenti** - Lista completa di tutti gli studenti registrati
- 📊 **Dashboard Statistiche** - Panoramica con metriche chiave
- 👁️ **Profili Dettagliati** - Visualizzazione completa dei dati di ogni studente
- 📥 **Download CV** - Possibilità di scaricare i CV degli studenti

## 🔒 Sicurezza

Il sistema implementa le best practices di sicurezza web:

### 1. **Validazione Input**
- ✓ Validazione lato client con JavaScript
- ✓ Validazione lato server con PHP (fondamentale)
- ✓ Sanitizzazione di tutti gli input utente
- ✓ Filtri PHP per email, URL e dati speciali

### 2. **Protezione SQL Injection**
- ✓ **Prepared Statements** per TUTTE le query MySQL
- ✓ Nessuna concatenazione diretta di stringhe nelle query
- ✓ Utilizzo di PDO con parametri placeholder (?)

### 3. **Protezione XSS (Cross-Site Scripting)**
- ✓ Uso di `htmlspecialchars()` per output di dati utente
- ✓ Codifica dell'output in tutti i template HTML
- ✓ Content Security Policy headers

### 4. **Gestione Password**
- ✓ Hash delle password con `password_hash()` (bcrypt)
- ✓ Verifica con `password_verify()`
- ✓ Requisiti password forti (8+ caratteri, maiuscole, minuscole, numeri)

### 5. **Gestione Sessioni**
- ✓ Cookie HttpOnly per prevenire accesso JavaScript
- ✓ Rigenerazione ID sessione dopo login
- ✓ Timeout sessioni
- ✓ Protezione CSRF

### 6. **Upload File Sicuro**
- ✓ Validazione tipo MIME (solo PDF)
- ✓ Limite dimensione file (5MB)
- ✓ Nome file randomizzato
- ✓ Directory protetta con .htaccess
- ✓ Download solo tramite script PHP autenticati

## 📁 Struttura Progetto

```
gruppo2/
├── config/
│   └── database.php          # Configurazione database e connessione PDO
├── css/
│   └── style.css             # Stili responsive e moderni
├── js/
│   └── validation.js         # Validazione client-side
├── php/
│   ├── login.php             # Handler login
│   ├── register.php          # Handler registrazione
│   ├── logout.php            # Handler logout
│   ├── update-profile.php    # Aggiornamento profilo utente
│   ├── upload-cv.php         # Upload CV
│   ├── download-cv.php       # Download CV utente
│   ├── add-experience.php    # Aggiunta esperienza
│   ├── delete-experience.php # Eliminazione esperienza
│   └── admin-download-cv.php # Download CV (admin)
├── uploads/
│   ├── cv/                   # Directory CV caricati
│   └── .htaccess             # Protezione directory uploads
├── index.php                 # Pagina login
├── register.php              # Pagina registrazione
├── user-dashboard.php        # Dashboard studente
├── admin-dashboard.php       # Dashboard amministratore
├── admin-view-student.php    # Dettaglio studente (admin)
├── database.sql              # Schema database
└── README.md                 # Questa documentazione
```

## 🚀 Installazione

### Prerequisiti
- **PHP 7.4+** (consigliato PHP 8.0+)
- **MySQL 5.7+** o **MariaDB 10.3+**
- **Apache** con mod_rewrite abilitato
- **Estensioni PHP richieste:**
  - PDO
  - PDO_MySQL
  - mbstring
  - fileinfo

### Passo 1: Clona/Copia i File

```bash
# Copia tutti i file nella directory del web server
# Esempio: C:\xampp\htdocs\gruppo2\ (Windows)
#         /var/www/html/gruppo2/ (Linux)
```

### Passo 2: Configura il Database

1. **Accedi a phpMyAdmin** o al client MySQL

2. **Importa il database:**
   ```bash
   mysql -u root -p < database.sql
   ```
   
   Oppure tramite phpMyAdmin:
   - Crea un database chiamato `cv_management`
   - Importa il file `database.sql`

3. **Modifica le credenziali** in `config/database.php`:
   ```php
   define('DB_HOST', 'localhost');
   define('DB_NAME', 'cv_management');
   define('DB_USER', 'root');        // Cambia con il tuo user
   define('DB_PASS', '');            // Cambia con la tua password
   ```

### Passo 3: Configura i Permessi

**Su Linux/Mac:**
```bash
# Permessi directory uploads
chmod 755 uploads/
chmod 755 uploads/cv/

# Proprietario Apache/www-data
chown -R www-data:www-data uploads/
```

**Su Windows (XAMPP):**
- Assicurati che la cartella `uploads/` sia scrivibile
- Nessuna configurazione particolare necessaria

### Passo 4: Avvia il Server

**Con XAMPP:**
1. Avvia Apache e MySQL da XAMPP Control Panel
2. Apri il browser: `http://localhost/gruppo2/`

**Con PHP Built-in Server (sviluppo):**
```bash
cd e:\gruppo2
php -S localhost:8000
```
Poi apri: `http://localhost:8000/`

## 👤 Account Predefiniti

Il sistema include due account di test:

### 🛡️ Amministratore
- **Email:** `admin@cvmanagement.it`
- **Password:** `admin123`

### 👨‍🎓 Studente
- **Email:** `student@test.it`
- **Password:** `student123`

> ⚠️ **IMPORTANTE:** Cambia queste password prima di mettere in produzione!

## 📖 Utilizzo

### Per gli Studenti

1. **Registrazione**
   - Vai su `index.php` e clicca "Registrati"
   - Compila il modulo con i tuoi dati
   - La password deve essere forte (8+ caratteri, maiuscole, minuscole, numeri)

2. **Login**
   - Inserisci email e password
   - Verrai reindirizzato alla tua dashboard

3. **Gestione Profilo**
   - Sezione "Dati Anagrafici": aggiorna nome, email, telefono, città, indirizzo, LinkedIn
   - Clicca "Salva Modifiche" per confermare

4. **Upload CV**
   - Sezione "Upload CV": seleziona un file PDF (max 5MB)
   - Clicca "Carica CV"
   - Puoi scaricare il CV caricato in qualsiasi momento

5. **Gestione Esperienze**
   - Sezione "Esperienze": clicca "Aggiungi Esperienza"
   - Scegli tipo (Lavoro o Formazione)
   - Compila i campi richiesti
   - Spunta "Attualmente in corso" se applicabile

### Per gli Amministratori

1. **Login**
   - Accedi con credenziali admin
   - Verrai reindirizzato alla dashboard amministratore

2. **Dashboard**
   - Visualizza statistiche: studenti totali, CV caricati, esperienze
   - Tabella con lista di tutti gli studenti

3. **Visualizza Profilo Studente**
   - Clicca "Visualizza" su uno studente
   - Vedi tutti i dati: anagrafici, CV, esperienze
   - Scarica il CV dello studente

## 🗄️ Schema Database

### Tabella `users`
- Informazioni account (email, password, nome, cognome, ruolo)

### Tabella `cv_data`
- Dati anagrafici estesi
- Riferimento al file CV caricato
- Collegata a `users` via `user_id`

### Tabella `experiences`
- Esperienze lavorative e formative
- Tipo, titolo, azienda/istituto, date, descrizione
- Collegata a `users` via `user_id`

## 🔧 Configurazione Avanzata

### Aumentare Limite Upload

**In `php.ini`:**
```ini
upload_max_filesize = 10M
post_max_size = 10M
```

**In `.htaccess` (se supportato):**
```apache
php_value upload_max_filesize 10M
php_value post_max_size 10M
```

### Abilitare HTTPS (Raccomandato per produzione)

1. Ottieni certificato SSL (Let's Encrypt gratuito)
2. Configura Apache per HTTPS
3. Modifica in `config/database.php`:
   ```php
   ini_set('session.cookie_secure', 1); // Abilita per HTTPS
   ```

### Log degli Errori

Gli errori sono loggati tramite `error_log()`. Controlla:
- **XAMPP:** `xampp/apache/logs/error.log`
- **Linux:** `/var/log/apache2/error.log`

## 🐛 Risoluzione Problemi

### Errore "Database Connection Error"
- Verifica che MySQL sia in esecuzione
- Controlla le credenziali in `config/database.php`
- Assicurati che il database `cv_management` esista

### Upload CV non funziona
- Verifica permessi cartella `uploads/`
- Controlla limite upload in `php.ini`
- Assicurati che il file sia un PDF valido

### Errore 404 sulle pagine
- Verifica che `mod_rewrite` sia abilitato in Apache
- Controlla il percorso del progetto nel browser

### Sessione non persiste
- Verifica che `session.save_path` sia configurato in `php.ini`
- Assicurati che i cookie siano abilitati nel browser

## 🚀 Deployment in Produzione

Prima di andare in produzione:

1. **Cambia le password di default**
   ```sql
   UPDATE users SET password_hash = ? WHERE email = 'admin@cvmanagement.it';
   ```

2. **Configura database dedicato**
   - Crea un utente MySQL con privilegi limitati
   - Non usare `root` in produzione

3. **Abilita HTTPS**
   - Usa Let's Encrypt per certificati gratuiti
   - Forza HTTPS in `.htaccess`

4. **Disabilita errori dettagliati**
   ```php
   // In php.ini o config
   display_errors = Off
   log_errors = On
   ```

5. **Backup regolari**
   - Database: `mysqldump -u user -p cv_management > backup.sql`
   - File: copia directory `uploads/`

6. **Aggiorna credenziali**
   - Modifica `config/database.php` con credenziali sicure
   - Usa variabili d'ambiente per dati sensibili

## 📝 API/Endpoints

Tutti gli endpoint richiedono autenticazione (tranne login/register):

| Endpoint | Metodo | Descrizione | Ruolo |
|----------|--------|-------------|-------|
| `/php/login.php` | POST | Login utente | Tutti |
| `/php/register.php` | POST | Registrazione | Tutti |
| `/php/logout.php` | GET | Logout | Autenticato |
| `/php/update-profile.php` | POST | Aggiorna profilo | Studente |
| `/php/upload-cv.php` | POST | Upload CV | Studente |
| `/php/download-cv.php` | GET | Download proprio CV | Studente |
| `/php/add-experience.php` | POST | Aggiungi esperienza | Studente |
| `/php/delete-experience.php` | GET | Elimina esperienza | Studente |
| `/php/admin-download-cv.php` | GET | Download CV studente | Admin |

## 📚 Tecnologie Utilizzate

- **Backend:** PHP 7.4+
- **Database:** MySQL 5.7+ / MariaDB 10.3+
- **Frontend:** HTML5, CSS3 (Custom), JavaScript (Vanilla)
- **Sicurezza:** PDO Prepared Statements, password_hash, htmlspecialchars
- **Server:** Apache 2.4+

## 🤝 Contributi

Questo è un progetto educativo. Suggerimenti per miglioramenti:

1. Implementare autenticazione a due fattori (2FA)
2. Aggiungere API REST per integrazione mobile
3. Sistema di notifiche via email
4. Export profilo completo in PDF
5. Ricerca e filtri avanzati nella dashboard admin
6. Supporto multilingua (i18n)

## 📄 Licenza

Progetto educativo - Libero utilizzo per scopi didattici.

## 👨‍💻 Supporto

Per domande o problemi:
1. Controlla la sezione "Risoluzione Problemi"
2. Verifica i log di errore di PHP e Apache
3. Testa con gli account predefiniti per isolare il problema

---

**Versione:** 1.0  
**Data Creazione:** Ottobre 2025  
**Compatibilità:** PHP 7.4+, MySQL 5.7+, Apache 2.4+
Grande progetto
