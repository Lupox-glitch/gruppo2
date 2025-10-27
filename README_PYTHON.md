# Sistema di Gestione CV Online - Versione Python

Sistema completo per la gestione di curriculum vitae degli studenti, implementato in **Python puro** (solo librerie standard, nessun framework).

## 🚀 Caratteristiche

- ✅ **Zero dipendenze esterne**: usa solo la libreria standard Python
- ✅ **Database SQLite**: nessun server database da installare
- ✅ **Autenticazione sicura**: password hashate con SHA-256 + salt
- ✅ **Upload CV**: supporto PDF con validazione (max 5MB)
- ✅ **Gestione esperienze**: lavorative e formative
- ✅ **Pannello admin**: statistiche e visualizzazione studenti
- ✅ **Responsive**: interfaccia moderna e mobile-friendly

## 📋 Requisiti

- **Python 3.7+** (già installato su Windows 10/11)
- Nessun'altra dipendenza!

## 🔧 Installazione

1. **Verifica Python installato**:
   ```powershell
   python --version
   ```
   Se non installato, scarica da [python.org](https://www.python.org/downloads/)

2. **Inizializza il database**:
   ```powershell
   python init_db.py
   ```
   Questo crea il database SQLite e gli utenti di test

3. **Avvia il server**:
   ```powershell
   python server.py
   ```

4. **Apri il browser**:
   ```
   http://localhost:8000
   ```

## 👤 Credenziali di Test

**Amministratore:**
- Email: `admin@cvmanagement.it`
- Password: `admin123`

**Studente:**
- Email: `student@test.it`
- Password: `student123`

## 📁 Struttura del Progetto

```
gruppo2/
├── server.py              # Server HTTP con routing e sessioni
├── database.py            # Gestione database SQLite
├── handlers.py            # Logica business (login, CV, esperienze)
├── init_db.py            # Script inizializzazione database
├── cvmanager.db          # Database SQLite (creato automaticamente)
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

## 🔒 Sicurezza

- **Password hashing**: SHA-256 con salt casuale per ogni utente
- **Prepared statements**: protezione da SQL injection
- **Input sanitization**: validazione e pulizia di tutti gli input
- **Session management**: sessioni con cookie sicuri
- **File upload validation**: controllo tipo MIME e dimensione PDF
- **XSS prevention**: escape di tutti gli output HTML

## 🎯 Funzionalità

### Per Studenti
- ✅ Registrazione e login
- ✅ Gestione profilo personale
- ✅ Upload curriculum (PDF)
- ✅ Aggiunta esperienze lavorative
- ✅ Aggiunta esperienze formative
- ✅ Download CV caricato

### Per Amministratori
- ✅ Visualizzazione statistiche generali
- ✅ Lista completa studenti
- ✅ Ricerca studenti
- ✅ Visualizzazione dettagli studente
- ✅ Download CV studenti

## 🛠️ API Endpoints

### Pagine
- `GET /` - Login
- `GET /register` - Registrazione
- `GET /user-dashboard` - Dashboard studente
- `GET /admin-dashboard` - Dashboard admin
- `GET /admin-view-student?id=X` - Dettagli studente

### API
- `POST /login` - Autenticazione
- `POST /register` - Registrazione nuovo utente
- `POST /api/update-profile` - Aggiorna profilo
- `POST /api/upload-cv` - Carica CV (PDF)
- `POST /api/add-experience` - Aggiungi esperienza
- `POST /api/delete-experience` - Elimina esperienza
- `GET /api/download-cv` - Download proprio CV
- `GET /api/admin-download-cv?user_id=X` - Download CV studente (admin)

## 📊 Database Schema

### Tabella `users`
- id, nome, cognome, email, password, ruolo, data_registrazione

### Tabella `cv_data`
- id, user_id, data_nascita, telefono, indirizzo, cv_filename, cv_path

### Tabella `esperienze`
- id, user_id, tipo, titolo, azienda, data_inizio, data_fine, descrizione

## 🐛 Troubleshooting

### Porta già in uso
Se la porta 8000 è occupata, modifica in `server.py`:
```python
PORT = 8080  # Cambia numero porta
```

### Database locked
Chiudi tutte le istanze del server prima di riavviare.

### Permessi upload
Assicurati che la cartella `uploads/` sia scrivibile:
```powershell
mkdir uploads
```

### File non trovati (CSS/JS)
Verifica che le cartelle `css/`, `js/` e `templates/` esistano.

## 🔄 Come Funziona

1. **Server HTTP**: `server.py` usa `http.server.BaseHTTPRequestHandler` per gestire richieste HTTP
2. **Routing**: Le richieste vengono instradate ai handler appropriati
3. **Sessioni**: Gestite in memoria con cookie HTTP
4. **Template**: File HTML con placeholder `{{variable}}` sostituiti dinamicamente
5. **Database**: SQLite con query parametrizzate per sicurezza

## 📝 Note di Sviluppo

- **Nessun framework**: tutto implementato con libreria standard Python
- **Threading**: il server supporta richieste concorrenti
- **Persistenza**: database SQLite in file `cvmanager.db`
- **File upload**: parsing multipart form implementato da zero

## 🚀 Sviluppi Futuri

- [ ] Paginazione lista studenti
- [ ] Filtri avanzati ricerca
- [ ] Export dati in Excel
- [ ] Email notifiche
- [ ] Password recovery
- [ ] 2FA autenticazione

## 📄 Licenza

Progetto educativo - Uso libero per scopi didattici

## 👥 Supporto

Per problemi o domande, verifica:
1. Python sia nella versione 3.7+
2. Database inizializzato con `init_db.py`
3. Porta 8000 disponibile
4. Cartelle `templates/`, `css/`, `js/` presenti

---

**Versione Python** - Nessuna dipendenza esterna richiesta! 🎉
