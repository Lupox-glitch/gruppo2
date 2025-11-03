#!/usr/bin/env python3
"""
CV Management System - Pure Python Server
No frameworks, only standard library
"""

import http.server
import http.cookies
import urllib.parse
import json
import os
import mimetypes
import secrets
import hashlib
import re
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
HOST = 'localhost'
PORT = 8080
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / 'uploads' / 'cv'

## AGGIUNTA: Configurazione Upload CV ##
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_EXTENSIONS = {'.pdf'}
# Ensure upload directory exists early
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

SECRET_KEY = secrets.token_hex(32)

# Session storage (in-memory, for simplicity)
SESSIONS = {}

# Ensure database schema exists at startup (safe: uses IF NOT EXISTS)
try:
    from database import create_tables
    create_tables()
    print("✓ Database schema ensured")
except Exception as e:
    # Don't crash the server on startup; surface a helpful message instead.
    print(f"Database init warning: {e}")


class CVHandler(http.server.BaseHTTPRequestHandler):
    """HTTP Request Handler for CV Management System"""
    
    def _set_headers(self, content_type='text/html', status=200):
        """Set HTTP headers"""
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.end_headers()
    
    def _get_session(self):
        """Get current session data"""
        cookies = http.cookies.SimpleCookie(self.headers.get('Cookie'))
        session_id = cookies.get('session_id')
        if session_id and session_id.value in SESSIONS:
            session = SESSIONS[session_id.value]
            # Check expiration
            if session.get('expires', 0) > datetime.now().timestamp():
                return session
            else:
                # Expired session
                del SESSIONS[session_id.value]
        return {}
    
    def _create_session(self, user_data):
        """Create new session and return cookie string"""
        session_id = secrets.token_urlsafe(32)
        expires = (datetime.now() + timedelta(hours=24)).timestamp()
        SESSIONS[session_id] = {
            **user_data,
            'expires': expires
        }
        
        # Return cookie string (don't send header yet)
        cookie = http.cookies.SimpleCookie()
        cookie['session_id'] = session_id
        cookie['session_id']['path'] = '/'
        cookie['session_id']['httponly'] = True
        cookie['session_id']['max-age'] = 86400  # 24 hours
        return cookie['session_id'].OutputString()
    
    def _destroy_session(self):
        """Destroy current session and return cookie string"""
        cookies = http.cookies.SimpleCookie(self.headers.get('Cookie'))
        session_id = cookies.get('session_id')
        if session_id and session_id.value in SESSIONS:
            del SESSIONS[session_id.value]
        
        # Return cookie clearing string
        cookie = http.cookies.SimpleCookie()
        cookie['session_id'] = ''
        cookie['session_id']['path'] = '/'
        cookie['session_id']['expires'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
        return cookie['session_id'].OutputString()
    
    def _redirect(self, location, set_cookie=None):
        """Redirect to another page"""
        self.send_response(302)
        self.send_header('Location', location)
        if set_cookie:
            self.send_header('Set-Cookie', set_cookie)
        self.end_headers()
    
    def _render_template(self, template_path, context=None):
        """Simple template rendering"""
        if context is None:
            context = {}
        
        template_file = BASE_DIR / template_path
        if not template_file.exists():
            self._send_error(404, f"Template not found: {template_path}")
            return
        
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
     # Simple variable replacement {{variable}}
        for key, value in context.items():
            if str(value) == 'None':
                content = content.replace('{{'+ key +'}}', '')
            
            else:
                content = content.replace('{{' + key + '}}', str(value))
        
        self._set_headers()
        self.wfile.write(content.encode('utf-8'))
    
    def _send_json(self, data, status=200):
        """Send JSON response"""
        self._set_headers('application/json', status)
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def _send_error(self, status, message):
        """Send error page"""
        self._set_headers(status=status)
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error {status}</title>
            <link rel="stylesheet" href="/css/style.css">
        </head>
        <body>
            <div class="auth-container">
                <div class="auth-card">
                    <h1>Error {status}</h1>
                    <p>{message}</p>
                    <a href="/" class="btn btn-primary">Go Home</a>
                </div>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))
    
    def _parse_post_data(self):
        """Parse POST data from request"""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return {}
        
        post_data = self.rfile.read(content_length).decode('utf-8', errors='replace')
        
        # Check content type
        content_type = self.headers.get('Content-Type', '')
        
        if 'application/x-www-form-urlencoded' in content_type:
            return dict(urllib.parse.parse_qsl(post_data))
        elif 'application/json' in content_type:
            return json.loads(post_data)
        elif 'multipart/form-data' in content_type:
            # Handle multipart (for file uploads)
            return self._parse_multipart()
        
        return {}
    
    def _parse_multipart(self):
        """Parse multipart form data (simplified)"""
        # This is a simplified version
        # For production, use a proper multipart parser
        content_length = int(self.headers.get('Content-Length', 0))
        boundary = self.headers.get('Content-Type').split('boundary=')[1]
        
        data = self.rfile.read(content_length)
        parts = data.split(f'--{boundary}'.encode())
        
        form_data = {}
        files = {}
        
        for part in parts:
            if b'Content-Disposition' in part:
                # Extract field name
                disposition = part.split(b'\r\n')[1].decode()
                if 'name="' in disposition:
                    name = disposition.split('name="')[1].split('"')[0]
                    
                    # Check if it's a file
                    if b'filename="' in part:
                        filename = disposition.split('filename="')[1].split('"')[0]
                        content = part.split(b'\r\n\r\n', 1)[1].rsplit(b'\r\n', 1)[0]
                        files[name] = {'filename': filename, 'content': content}
                    else:
                        value = part.split(b'\r\n\r\n', 1)[1].rsplit(b'\r\n', 1)[0].decode()
                        form_data[name] = value
        
        return {'form': form_data, 'files': files}
    
    def _serve_static(self, path):
        """Serve static files (CSS, JS, etc.)"""
        file_path = BASE_DIR / path.lstrip('/')
        
        if not file_path.exists() or not file_path.is_file():
            self._send_error(404, "File not found")
            return
        
        # Get mime type
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if not mime_type:
            mime_type = 'application/octet-stream'
        
        self._set_headers(mime_type)
        with open(file_path, 'rb') as f:
            self.wfile.write(f.read())

    ## AGGIUNTA: Gestione upload CV ##
    def _handle_upload_cv_form(self):
        content_type = self.headers.get('Content-Type', '')
        if 'boundary=' not in content_type:
            self._send_json({'success': False, 'error': 'Invalid Content-Type'}, 400)
            return

        boundary = content_type.split('boundary=')[-1].encode()
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        user_id = None
        filename = None
        file_data = None

        for part in body.split(b'--' + boundary):
            if b'Content-Disposition' not in part:
                continue
            try:
                headers, data = part.split(b'\r\n\r\n', 1)
            except ValueError:
                continue
            data = data.rstrip(b'\r\n')
            header_text = headers.decode(errors='ignore')
            if 'name="user_id"' in header_text:
                user_id = data.decode()
            elif 'name="cv_file"' in header_text:
                start = header_text.find('filename="') + 10
                end = header_text.find('"', start)
                filename = header_text[start:end]
                file_data = data
        # ✅ Controlla campi obbligatori
        if not user_id or not filename or not file_data:
            self._send_json({'success': False, 'error': 'manca cartello o user_id'}, 400)
            return
        # ✅ Controlla che sia un PDF
        if not filename.lower().endswith('.pdf'):
            self._send_json({'success': False, 'error': 'Solo file PDF sono ammessi'}, 400)
            return
        # ✅ Controlla dimensione file
        if len(file_data) > MAX_FILE_SIZE:
            self._send_json({'success': False, 'error': 'il file deve essere < 5 mb'}, 400)
            return



    # Rinomina sicura per evitare conflitti

        # Usa il nome originale del file caricato
        original_filename = os.path.basename(filename)

        # Pulisci il nome per evitare caratteri strani (sicurezza)
        safe_filename = re.sub(r'[^A-Za-z0-9._-]', '_', original_filename)




        # Percorso di salvataggio finale
        save_path = UPLOAD_DIR / safe_filename

        # Se esiste già un file con lo stesso nome, aggiungi un numero progressivo
        base, ext = os.path.splitext(safe_filename)
        counter = 1
        while os.path.exists(save_path):
                safe_filename = f"{base}_{counter}{ext}"
                save_path = UPLOAD_DIR / safe_filename
                counter += 1

        # Salva effettivamente il file
        with open(save_path, 'wb') as f:
            f.write(file_data)

        # Salva nel DB il nome effettivo
        from database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        relative_path = f"uploads/cv/{safe_filename}"
        cursor.execute("INSERT INTO user_cvs (user_id, file_path) VALUES (%s, %s)", (user_id, relative_path))
        conn.commit()
        conn.close()





        self._send_json({'success': True, 'message': 'CV caricato con successo!'})

    ## AGGIUNTA: Gestione download CV ###
    def _handle_download_cv(self, user_id):
        from database import get_cv_file
        file_name = get_cv_file(int(user_id))
        if not file_name:
            self._send_json({'success': False, 'error': 'CV not found'}, 404)
            return

    # ✅ Usa percorso corretto
        if file_name.startswith("uploads/cv/"):
            file_path = Path(file_name)
        else:
            file_path = UPLOAD_DIR / file_name

        if not file_path.exists():
            self._send_json({'success': False, 'error': 'File not found on server'}, 404)
            return

    # ✅ Imposta nome file corretto
        download_name = os.path.basename(file_path)

        self.send_response(200)
        self.send_header('Content-Type', 'application/pdf')
        self.send_header('Content-Disposition', f'inline; filename="{download_name}"')
        self.end_headers()
        with open(file_path, 'rb') as f:
            self.wfile.write(f.read())


    """Gestisce l'eliminazione di un CV"""

    def _handle_delete_cv(self, cv_id, session):
    
        from database import get_cv_by_id, delete_cv
        import os
        from pathlib import Path

        cv = get_cv_by_id(int(cv_id))
        if not cv:
            self._send_json({'success': False, 'error': 'CV non trovato'}, 404)
            return

        user_role = session.get('role')
        user_id = session.get('user_id')

        # 🔒 Controllo permessi
        if user_role != 'admin' and cv['user_id'] != int(user_id):
            self._send_json({'success': False, 'error': 'Non autorizzato a cancellare questo CV'}, 403)
            return

        # 🔧 Elimina file dal filesystem
        file_path = Path(cv['file_path'])
        if not file_path.is_absolute():
            file_path = Path.cwd() / file_path

        if file_path.exists():
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Errore durante l'eliminazione file: {e}")

        # 🗑️ Elimina dal database
        delete_cv(int(cv_id))

        self._send_json({'success': True, 'message': 'CV eliminato con successo'})


    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        query = dict(urllib.parse.parse_qsl(parsed_path.query))
        
        # Get session
        session = self._get_session()
        
        # Route handling
        if path in ['/', '/home', '/index']:
            # Always show homepage, even if logged in
            if session.get('user_id'):
                # Welcome for logged-in users
                welcome_section = f"""
<h1>Benvenuto, {session.get('nome','')} {session.get('cognome','')}</h1>
<p>Accedi rapidamente alla tua area.</p>
"""
                if session.get('role') == 'admin':
                    cta_section = """
<a href="/admin-dashboard" class="btn btn-primary">Vai alla Dashboard Admin</a>
<a href="/logout" class="btn btn-secondary">Logout</a>
"""
                else:
                    cta_section = """
<a href="/user-dashboard" class="btn btn-primary">Vai alla tua Dashboard</a>
<a href="/logout" class="btn btn-secondary">Logout</a>
"""
            else:
                # Generic homepage for guests
                welcome_section = """
<h1>Sistema Gestione CV</h1>
<p>Gestisci facilmente il tuo curriculum e le tue esperienze.</p>
"""
                cta_section = """
<a href="/login" class="btn btn-primary">Accedi</a>
<a href="/register" class="btn btn-secondary">Registrati</a>
"""

            self._render_template('templates/home.html', {
                'welcome_section': welcome_section,
                'cta_section': cta_section
            })

        elif path == '/login':
            # Show login page regardless of session state (optionally could redirect if logged in)
            self._render_template('templates/login.html', {
                'error': session.get('error', ''),
                'success': session.get('success', '')
            })
        
        elif path == '/register':
            if session.get('user_id'):
                self._redirect('/')
                return
            self._render_template('templates/register.html', {
                'error': session.get('error', '')
            })
        

        elif path == '/privacy':
            # Privacy & GDPR page
            self._render_template('templates/privacy.html')
        

        elif path == '/user-dashboard':
            if not session.get('user_id') or session.get('role') == 'admin':
                self._redirect('/')
                return
            
            from handlers import get_user_dashboard_data
            data = get_user_dashboard_data(session.get('user_id'))
            self._render_template('templates/user-dashboard.html', data)
        
        


        elif path == '/admin-dashboard':
            if not session.get('user_id') or session.get('role') != 'admin':
                self._redirect('/')
                return
            
            from handlers import get_admin_dashboard_data
            data = get_admin_dashboard_data()
            # Add admin session info to context
            data['user_nome'] = session.get('nome', 'Admin')
            data['user_cognome'] = session.get('cognome', 'Sistema')
            self._render_template('templates/admin-dashboard.html', data)
        

        elif path == '/admin-view-student':
            if not session.get('user_id') or session.get('role') != 'admin':
                self._redirect('/')
                return
            
            student_id = query.get('id')
            if not student_id:
                self._send_error(400, "ID studente mancante")
                return
            
            from handlers import get_admin_view_student_data
            data = get_admin_view_student_data(int(student_id))
            
            if not data:
                self._send_error(404, "Studente non trovato")
                return
            
            self._render_template('templates/admin-view-student.html', data)
        


        elif path == '/logout':
            cookie = self._destroy_session()
            self._redirect('/', set_cookie=cookie)
        
        # Static files
        elif path.startswith('/css/') or path.startswith('/js/') or path.startswith('/uploads/'):
            self._serve_static(path)
        
        elif path.startswith('/api/download-cv'):
            user_id = query.get('user_id')
            if not user_id:
                self._send_json({'success': False, 'error': 'Missing user_id'}, 400)
                return
            self._handle_download_cv(user_id)
            return
        elif path == '/api/delete-cv':
            session = self._get_session()
            if not session.get('user_id'):
                self._send_json({'success': False, 'error': 'Non autenticato'}, 401)
                return

            query = dict(urllib.parse.parse_qsl(parsed_path.query))
            cv_id = query.get('cv_id')
            if not cv_id:
                self._send_json({'success': False, 'error': 'cv_id mancante'}, 400)
                return

            self._handle_delete_cv(cv_id, session)
            return

        else:
            self._send_error(404, "Page not found")
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # Get session
        session = self._get_session()

        # Parse POST data, ma ATTENZIONE: non consumare il body se è multipart/form-data
        # destinato all'endpoint /api/upload-cv (che legge il body da solo).
        content_type = self.headers.get('Content-Type', '')
        if self.path == '/api/upload-cv' and 'multipart/form-data' in content_type:
            post_data = {}  # _handle_upload_cv_form() leggerà il body direttamente
        else:
            post_data = self._parse_post_data()

        
        # Import handlers
        from handlers import (
            handle_login, handle_register, handle_upload_cv,handle_download_cv,
            handle_update_profile, handle_add_experience, handle_delete_experience,
            handle_admin_delete_user
        )
        
        # Route handling
        # Form-based login (HTML)
        if path == '/login':
            result = handle_login(post_data)
            if result['success']:
                cookie = self._create_session(result['user'])
                # Redirect to appropriate dashboard
                self._redirect(result['redirect'], set_cookie=cookie)
            else:
                # Re-render login page with error message
                self._render_template('templates/login.html', {
                    'error': result.get('error', ''),
                    'success': ''
                })

        # JSON API login
        elif path == '/api/login':
            result = handle_login(post_data)
            if result['success']:
                cookie = self._create_session(result['user'])
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Set-Cookie', cookie)
                self.end_headers()
                self.wfile.write(json.dumps({'success': True, 'redirect': result['redirect']}).encode('utf-8'))
            else:
                self._send_json({'success': False, 'error': result['error']}, 400)
        
        # Form-based register (HTML)
        elif path == '/register':
            result = handle_register(post_data)
            if result['success']:
                # After registration, show login with success message
                self._render_template('templates/login.html', {
                    'error': '',
                    'success': result.get('message', 'Registrazione completata!')
                })
            else:
                self._render_template('templates/register.html', {
                    'error': result.get('error', '')
                })

        # JSON API register
        elif path == '/api/register':
            result = handle_register(post_data)
            if result['success']:
                self._send_json({'success': True, 'message': 'Registrazione completata!'})
            else:
                self._send_json({'success': False, 'error': result['error']}, 400)
        

        elif path == '/api/update-profile':
            if not session.get('user_id'):
                self._send_json({'success': False, 'error': 'Non autenticato'}, 401)
                return
            
            result = handle_update_profile(session.get('user_id'), post_data)
            self._send_json(result)
        
        elif path == '/api/add-experience':
            if not session.get('user_id'):
                self._send_json({'success': False, 'error': 'Non autenticato'}, 401)
                return
            
          
            result = handle_add_experience(session.get('user_id'), post_data)
            self._send_json(result)
        


        elif path == '/api/delete-experience':
            if not session.get('user_id'):
                self._send_json({'success': False, 'error': 'Non autenticato'}, 401)
                return
            exp_id = post_data.get('id') or post_data.get('experience_id')
            try:
                exp_id = int(exp_id)
            except (TypeError, ValueError):
                self._send_json({'success': False, 'error': 'ID esperienza non valido'}, 400)
                return

            result = handle_delete_experience(session.get('user_id'), exp_id)
            self._send_json(result)
        

        elif path == '/api/admin/delete-user':
                if not session.get('user_id') or session.get('role') != 'admin':
                    self._send_json({'success': False, 'error': 'Non autorizzato'}, 403)
                    return
                
                user_id = post_data.get('user_id')
                if not user_id:
                    self._send_json({'success': False, 'error': 'ID utente mancante'}, 400)
                    return
                
                try:
                    user_id = int(user_id)
                except (TypeError, ValueError):
                    self._send_json({'success': False, 'error': 'ID utente non valido'}, 400)
                    return
                
                result = handle_admin_delete_user(user_id)
                self._send_json(result)
        

        elif path == '/api/cv-content':
            # Return current CV content (hobby, skills, languages) as JSON for the logged-in user
            if not session.get('user_id'):
                self._redirect('/login')
                return
            # For cv-content, use form data (flatten if multipart)
            form_data = post_data.get('form', post_data) if isinstance(post_data, dict) and 'form' in post_data else post_data
            from handlers import add_cv_content
            result =add_cv_content(session.get('user_id'), form_data)
            self._redirect('/user-dashboard')



#################### PARTE CREAZIONE E DOWNLOAD CV PDF ##############################
        elif path == '/api/generate-cv':
            if not session.get('user_id'):
                self._send_json({'success': False, 'error': 'Non autenticato'}, 401)
                return

            from handlers import handle_download_cv
            result = handle_download_cv(session['user_id'])

            if not result['success']:
                self._send_json(result, 500)
                return

            self.send_response(200)
            self.send_header('Content-Type', 'application/pdf')
            self.send_header('Content-Disposition', f'attachment; filename="cv_{session["user_id"]}.pdf"')  ### file name da cambiare (mettere tipo il nome dell'utente)
            self.end_headers()
            self.wfile.write(result['pdf_bytes'])

        elif path == '/api/upload-cv':
            if not session.get('user_id'):
                self._send_json({'success': False, 'error': 'Non autenticato'}, 401)
                return
            self._handle_upload_cv_form()
            return

##########################################################################################

    def log_message(self, format, *args):
        """Log HTTP requests"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")


def init_database():
    """Initialize database (MySQL)"""
    from database import create_tables, create_default_users
    create_tables()
    create_default_users()
    print("✓ Database initialized (MySQL)")


def main():
    """Start the server"""
    # Create necessary directories
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    # Initialize database
    init_database()
    
    # Start server
    server = http.server.HTTPServer((HOST, PORT), CVHandler)
    print(f"""
╔════════════════════════════════════════════════════════════╗
║  📄 CV Management System - Python Server                   ║
║  🚀 Server started at: http://{HOST}:{PORT}               ║
║                                                            ║
║  👤 Test Accounts:                                         ║
║     Admin:    admin@cvmanagement.it / admin123             ║
║     Student:  student@test.it / student123                 ║
║                                                            ║
║  Press Ctrl+C to stop                                      ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✓ Server stopped")
        server.shutdown()


if __name__ == '__main__':
    main()