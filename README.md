# Sistema di Gestione CV Online - Versione Python

Sistema completo per la gestione di curriculum vitae degli studenti, implementato in Python puro (nessun framework). Backend ora su MySQL.

## 🚀 Caratteristiche

- ✅ Dipendenze minime: solo il driver MySQL per Python
- ✅ Database MySQL: schema ottimizzato InnoDB/UTF8MB4
- ✅ Autenticazione sicura: password hashate con SHA-256 + salt
- ✅ Upload CV: supporto PDF con validazione (max 5MB)
- ✅ Gestione esperienze: lavorative e formative
- ✅ Pannello admin: statistiche e visualizzazione studenti
- ✅ Responsive: interfaccia moderna e mobile-friendly

## 📋 Requisiti

- Python 3.8+
- MySQL Server 8+
- Pip per installare le dipendenze

## 🔧 Installazione rapida (Windows PowerShell)

1) Verifica Python
   ```powershell
   python --version
   ```

2) Installa dipendenze Python
   ```powershell
   pip install -r requirements.txt
   ```

3) Prepara MySQL (da client MySQL)
   Esegui lo script `database.sql` per creare database e tabelle:
   ```sql
   SOURCE path\\to\\gruppo2\\database.sql;
   ```

4) Configura variabili d'ambiente (opzionale, hanno default)
   ```powershell
   $Env:MYSQL_HOST = "localhost"
   $Env:MYSQL_PORT = "3306"
   $Env:MYSQL_USER = "root"
   $Env:MYSQL_PASSWORD = ""
   $Env:MYSQL_DB = "cv_management"
   ```

5) Avvia il server
   ```powershell
   python server.py
   ```

6) Apri il browser: http://localhost:8000

## 👤 Credenziali di Test

Amministratore:
- Email: admin@cvmanagement.it
- Password: admin123

Studente:
- Email: student@test.it
- Password: student123

## 📁 Struttura del Progetto

```
gruppo2/
├── server.py              # Server HTTP con routing e sessioni
├── database.py            # Gestione database MySQL (mysql-connector)
├── handlers.py            # Logica business (login, CV, esperienze)
├── init_db.py             # Script inizializzazione database
│
├── templates/            # Template HTML
│   ├── login.html
│   ├── register.html
│   ├── user-dashboard.html
│   ├── admin-dashboard.html
│   └── admin-view-student.html
│
├── css/
│   └── style.css         # Styling completo
│
├── js/
│   └── validation.js     # Validazione client-side
│
└── uploads/              # CV caricati (creata automaticamente)
```

## 🔐 Sicurezza

- Password hashing: SHA-256 con salt
- Prepared statements: protezione da SQL injection
- Input sanitization: validazione e pulizia di tutti gli input
- Session management: sessioni con cookie sicuri
- File upload validation: controllo tipo MIME e dimensione PDF
- XSS prevention: escape degli output HTML

## 🎯 Funzionalità

Per Studenti
- Registrazione e login
- Gestione profilo personale
- Upload curriculum (PDF)
- Aggiunta esperienze lavorative e formative
- Download CV caricato

Per Amministratori
- Visualizzazione statistiche generali
- Lista completa studenti e ricerca
- Visualizzazione dettagli studente
- Download CV studenti

## 🛠️ Endpoint

Pagine
- GET / — Login
- GET /register — Registrazione
- GET /user-dashboard — Dashboard studente
- GET /admin-dashboard — Dashboard admin

API
- POST /login — Autenticazione (form)
- POST /register — Registrazione (form)
- POST /api/update-profile — Aggiorna profilo
- POST /api/upload-cv — Carica CV (PDF)
- POST /api/add-experience — Aggiungi esperienza
- POST /api/delete-experience — Elimina esperienza

## 🧰 Troubleshooting

Porta già in uso: cambia PORT in server.py

Errore connessione MySQL: verifica credenziali/host/porta o imposta le variabili d'ambiente.

Permessi upload: assicurati che la cartella uploads/ sia scrivibile (viene creata automaticamente all'avvio).

File non trovati (CSS/JS): verifica che le cartelle css/, js/ e templates/ esistano.

## 📄 Licenza

Progetto educativo - Uso libero per scopi didattici.
