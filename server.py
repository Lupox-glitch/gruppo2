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
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
HOST = 'localhost'
PORT = 8000
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / 'uploads' / 'cv'
DB_PATH = BASE_DIR / 'cv_management.db'
SECRET_KEY = secrets.token_hex(32)

# Session storage (in-memory, for simplicity)
SESSIONS = {}

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
        """Create new session"""
        session_id = secrets.token_urlsafe(32)
        expires = (datetime.now() + timedelta(hours=24)).timestamp()
        SESSIONS[session_id] = {
            **user_data,
            'expires': expires
        }
        
        # Set cookie
        cookie = http.cookies.SimpleCookie()
        cookie['session_id'] = session_id
        cookie['session_id']['path'] = '/'
        cookie['session_id']['httponly'] = True
        cookie['session_id']['max-age'] = 86400  # 24 hours
        self.send_header('Set-Cookie', cookie['session_id'].OutputString())
        return session_id
    
    def _destroy_session(self):
        """Destroy current session"""
        cookies = http.cookies.SimpleCookie(self.headers.get('Cookie'))
        session_id = cookies.get('session_id')
        if session_id and session_id.value in SESSIONS:
            del SESSIONS[session_id.value]
        
        # Clear cookie
        cookie = http.cookies.SimpleCookie()
        cookie['session_id'] = ''
        cookie['session_id']['path'] = '/'
        cookie['session_id']['expires'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
        self.send_header('Set-Cookie', cookie['session_id'].OutputString())
    
    def _redirect(self, location):
        """Redirect to another page"""
        self.send_response(302)
        self.send_header('Location', location)
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
        
        post_data = self.rfile.read(content_length).decode('utf-8')
        
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
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        query = dict(urllib.parse.parse_qsl(parsed_path.query))
        
        # Get session
        session = self._get_session()
        
        # Route handling
        if path == '/' or path == '/index':
            # Check if already logged in
            if session.get('user_id'):
                if session.get('role') == 'admin':
                    self._redirect('/admin-dashboard')
                else:
                    self._redirect('/user-dashboard')
                return
            
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
            self._render_template('templates/admin-dashboard.html', data)
        
        elif path == '/logout':
            self._destroy_session()
            self._redirect('/')
        
        # Static files
        elif path.startswith('/css/') or path.startswith('/js/') or path.startswith('/uploads/'):
            self._serve_static(path)
        
        else:
            self._send_error(404, "Page not found")
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # Parse POST data
        post_data = self._parse_post_data()
        
        # Get session
        session = self._get_session()
        
        # Import handlers
        from handlers import (
            handle_login, handle_register, handle_upload_cv,
            handle_update_profile, handle_add_experience, handle_delete_experience
        )
        
        # Route handling
        # Form-based login (HTML)
        if path == '/login':
            result = handle_login(post_data)
            if result['success']:
                self._create_session(result['user'])
                # Redirect to appropriate dashboard
                self._redirect(result['redirect'])
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
                self._create_session(result['user'])
                self._send_json({'success': True, 'redirect': result['redirect']})
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
        
        elif path == '/api/upload-cv':
            if not session.get('user_id'):
                self._send_json({'success': False, 'error': 'Non autenticato'}, 401)
                return
            
            result = handle_upload_cv(session.get('user_id'), post_data.get('files', {}))
            self._send_json(result)
        
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
        
        else:
            self._send_error(404, "Endpoint not found")
    
    def log_message(self, format, *args):
        """Log HTTP requests"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")


def init_database():
    """Initialize SQLite database"""
    from database import create_tables, create_default_users
    create_tables()
    create_default_users()
    print(f"✓ Database initialized: {DB_PATH}")


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
║  📄 CV Management System - Python Server                  ║
║  🚀 Server started at: http://{HOST}:{PORT}              ║
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
