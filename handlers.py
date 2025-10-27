"""
Request handlers for CV Management System
All functions use prepared statements for SQL injection prevention
"""

import os
import secrets
from pathlib import Path
from datetime import datetime
from database import (
    get_db_connection, hash_password, verify_password,
    sanitize_input, validate_email, validate_password,
    execute_query, execute_insert, execute_update
)

UPLOAD_DIR = Path(__file__).parent / 'uploads' / 'cv'
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def handle_login(data):
    """Handle user login with prepared statements"""
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    # Validation
    if not email or not password:
        return {'success': False, 'error': 'Tutti i campi sono obbligatori'}
    
    if not validate_email(email):
        return {'success': False, 'error': 'Email non valida'}
    
    # Query with prepared statement
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    
    if not user or not verify_password(password, user['password_hash']):
        return {'success': False, 'error': 'Email o password non corretti'}
    
    # Successful login
    redirect = '/admin-dashboard' if user['role'] == 'admin' else '/user-dashboard'
    
    return {
        'success': True,
        'user': {
            'user_id': user['id'],
            'email': user['email'],
            'nome': user['nome'],
            'cognome': user['cognome'],
            'role': user['role']
        },
        'redirect': redirect
    }


def handle_register(data):
    """Handle user registration with prepared statements"""
    nome = sanitize_input(data.get('nome', '').strip())
    cognome = sanitize_input(data.get('cognome', '').strip())
    email = data.get('email', '').strip()
    password = data.get('password', '')
    password_confirm = data.get('password_confirm', '')
    
    # Validation
    if not all([nome, cognome, email, password, password_confirm]):
        return {'success': False, 'error': 'Tutti i campi sono obbligatori'}
    
    if len(nome) < 2 or len(cognome) < 2:
        return {'success': False, 'error': 'Nome e cognome devono contenere almeno 2 caratteri'}
    
    if not validate_email(email):
        return {'success': False, 'error': 'Email non valida'}
    
    valid, error = validate_password(password)
    if not valid:
        return {'success': False, 'error': error}
    
    if password != password_confirm:
        return {'success': False, 'error': 'Le password non corrispondono'}
    
    # Check if email exists (prepared statement)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
    if cursor.fetchone():
        conn.close()
        return {'success': False, 'error': 'Questa email è già registrata'}
    
    # Insert new user (prepared statement)
    password_hash = hash_password(password)
    cursor.execute('''
        INSERT INTO users (email, password_hash, nome, cognome, role)
        VALUES (?, ?, ?, ?, 'student')
    ''', (email, password_hash, nome, cognome))
    
    user_id = cursor.lastrowid
    
    # Create cv_data entry
    cursor.execute('INSERT INTO cv_data (user_id) VALUES (?)', (user_id,))
    
    conn.commit()
    conn.close()
    
    return {'success': True, 'message': 'Registrazione completata!'}


def handle_update_profile(user_id, data):
    """Handle profile update with prepared statements"""
    nome = sanitize_input(data.get('nome', '').strip())
    cognome = sanitize_input(data.get('cognome', '').strip())
    email = data.get('email', '').strip()
    telefono = sanitize_input(data.get('telefono', '').strip())
    data_nascita = data.get('data_nascita', '').strip()
    citta = sanitize_input(data.get('citta', '').strip())
    indirizzo = sanitize_input(data.get('indirizzo', '').strip())
    linkedin_url = data.get('linkedin_url', '').strip()
    
    # Validation
    if not all([nome, cognome, email]):
        return {'success': False, 'error': 'Nome, cognome e email sono obbligatori'}
    
    if not validate_email(email):
        return {'success': False, 'error': 'Email non valida'}
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if email is used by another user (prepared statement)
    cursor.execute('SELECT id FROM users WHERE email = ? AND id != ?', (email, user_id))
    if cursor.fetchone():
        conn.close()
        return {'success': False, 'error': 'Questa email è già utilizzata'}
    
    # Update users table (prepared statement)
    cursor.execute('''
        UPDATE users 
        SET nome = ?, cognome = ?, email = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (nome, cognome, email, user_id))
    
    # Update cv_data (prepared statement)
    cursor.execute('SELECT id FROM cv_data WHERE user_id = ?', (user_id,))
    cv_exists = cursor.fetchone()
    
    if cv_exists:
        cursor.execute('''
            UPDATE cv_data
            SET telefono = ?, data_nascita = ?, citta = ?, 
                indirizzo = ?, linkedin_url = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (telefono, data_nascita, citta, indirizzo, linkedin_url, user_id))
    else:
        cursor.execute('''
            INSERT INTO cv_data (user_id, telefono, data_nascita, citta, indirizzo, linkedin_url)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, telefono, data_nascita, citta, indirizzo, linkedin_url))
    
    conn.commit()
    conn.close()
    
    return {'success': True, 'message': 'Profilo aggiornato con successo!'}


def handle_upload_cv(user_id, files):
    """Handle CV file upload with validation"""
    if 'cv_file' not in files:
        return {'success': False, 'error': 'Nessun file selezionato'}
    
    file_data = files['cv_file']
    filename = file_data.get('filename', '')
    content = file_data.get('content', b'')
    
    # Validate file
    if not filename.lower().endswith('.pdf'):
        return {'success': False, 'error': 'Solo file PDF sono consentiti'}
    
    if len(content) > MAX_FILE_SIZE:
        return {'success': False, 'error': 'Il file è troppo grande (max 5MB)'}
    
    # Check PDF signature (basic validation)
    if not content.startswith(b'%PDF'):
        return {'success': False, 'error': 'File non valido'}
    
    # Generate secure filename
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    secure_filename = f'cv_{user_id}_{timestamp}.pdf'
    file_path = UPLOAD_DIR / secure_filename
    
    # Ensure upload directory exists
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save file
    with open(file_path, 'wb') as f:
        f.write(content)
    
    # Update database (prepared statement)
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get old CV path to delete it
    cursor.execute('SELECT cv_file_path FROM cv_data WHERE user_id = ?', (user_id,))
    old_cv = cursor.fetchone()
    
    if old_cv and old_cv['cv_file_path']:
        old_path = Path(__file__).parent / old_cv['cv_file_path']
        if old_path.exists():
            old_path.unlink()
    
    # Update database
    relative_path = f'uploads/cv/{secure_filename}'
    cursor.execute('''
        UPDATE cv_data
        SET cv_file_path = ?, cv_uploaded_at = CURRENT_TIMESTAMP
        WHERE user_id = ?
    ''', (relative_path, user_id))
    
    conn.commit()
    conn.close()
    
    return {'success': True, 'message': 'CV caricato con successo!'}


def handle_add_experience(user_id, data):
    """Handle adding experience with prepared statements"""
    tipo = data.get('tipo', '').strip()
    titolo = sanitize_input(data.get('titolo', '').strip())
    azienda_istituto = sanitize_input(data.get('azienda_istituto', '').strip())
    data_inizio = data.get('data_inizio', '').strip()
    data_fine = data.get('data_fine', '').strip()
    is_current = 1 if data.get('is_current') else 0
    descrizione = sanitize_input(data.get('descrizione', '').strip())
    
    # Validation
    if tipo not in ['lavoro', 'formazione']:
        return {'success': False, 'error': 'Tipo di esperienza non valido'}
    
    if not all([titolo, azienda_istituto, data_inizio]):
        return {'success': False, 'error': 'Tutti i campi obbligatori devono essere compilati'}
    
    if not is_current and not data_fine:
        return {'success': False, 'error': 'Data di fine obbligatoria se non in corso'}
    
    if is_current:
        data_fine = None
    
    # Insert experience (prepared statement)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO experiences 
        (user_id, tipo, titolo, azienda_istituto, data_inizio, data_fine, is_current, descrizione)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, tipo, titolo, azienda_istituto, data_inizio, data_fine, is_current, descrizione))
    
    conn.commit()
    conn.close()
    
    return {'success': True, 'message': 'Esperienza aggiunta con successo!'}


def handle_delete_experience(user_id, experience_id):
    """Handle deleting experience with prepared statements"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verify ownership (prepared statement)
    cursor.execute('SELECT id FROM experiences WHERE id = ? AND user_id = ?', (experience_id, user_id))
    if not cursor.fetchone():
        conn.close()
        return {'success': False, 'error': 'Esperienza non trovata'}
    
    # Delete (prepared statement)
    cursor.execute('DELETE FROM experiences WHERE id = ? AND user_id = ?', (experience_id, user_id))
    
    conn.commit()
    conn.close()
    
    return {'success': True, 'message': 'Esperienza eliminata con successo!'}


def get_user_dashboard_data(user_id):
    """Get all data for user dashboard"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get user data (prepared statement)
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = dict(cursor.fetchone())
    
    # Get CV data
    cursor.execute('SELECT * FROM cv_data WHERE user_id = ?', (user_id,))
    cv_data = cursor.fetchone()
    cv_data = dict(cv_data) if cv_data else {}
    
    # Get experiences
    cursor.execute('''
        SELECT * FROM experiences 
        WHERE user_id = ? 
        ORDER BY data_inizio DESC
    ''', (user_id,))
    experiences = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    # Sanitize output
    for key in user:
        if isinstance(user[key], str):
            user[key] = sanitize_input(user[key])
    
    # Flatten data for template
    context = {
        'user_nome': user.get('nome', ''),
        'user_cognome': user.get('cognome', ''),
        'user_email': user.get('email', ''),
        'telefono': cv_data.get('telefono', ''),
        'data_nascita': cv_data.get('data_nascita', ''),
        'citta': cv_data.get('citta', ''),
        'indirizzo': cv_data.get('indirizzo', ''),
        'linkedin_url': cv_data.get('linkedin_url', ''),
        'success_message': '',
        'error_message': '',
        'cv_section': _render_cv_section(cv_data),
        'esperienze_lavorative': _render_experiences(experiences, 'lavoro'),
        'esperienze_formative': _render_experiences(experiences, 'formazione')
    }
    
    return context


def _render_cv_section(cv_data):
    """Render CV section HTML"""
    cv_path = cv_data.get('cv_file_path', '')
    if cv_path:
        return f'''
        <div class="alert alert-success">
            <strong>✓ CV caricato:</strong> {cv_path.split('/')[-1]}
            <br>
            <a href="/{cv_path}" class="btn btn-secondary btn-sm" target="_blank">Visualizza CV</a>
        </div>
        '''
    else:
        return '<p class="text-muted">Nessun CV caricato ancora.</p>'


def _render_experiences(experiences, tipo):
    """Render experiences list HTML"""
    filtered = [exp for exp in experiences if exp.get('tipo') == tipo]
    
    if not filtered:
        return '<p class="text-muted">Nessuna esperienza aggiunta ancora.</p>'
    
    html = '<div class="experiences-list">'
    for exp in filtered:
        is_current = exp.get('is_current', 0)
        data_fine = exp.get('data_fine', '')
        periodo = f"{exp.get('data_inizio', '')} - {'In corso' if is_current else data_fine}"
        
        html += f'''
        <div class="experience-card">
            <h4>{sanitize_input(exp.get('titolo', ''))}</h4>
            <p class="company">{sanitize_input(exp.get('azienda_istituto', ''))}</p>
            <p class="period">{periodo}</p>
            <p class="description">{sanitize_input(exp.get('descrizione', ''))}</p>
            <button onclick="deleteExperience({exp.get('id')})" class="btn btn-danger btn-sm">Elimina</button>
        </div>
        '''
    
    html += '</div>'
    return html


def get_admin_dashboard_data():
    """Get all data for admin dashboard"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all students with their data
    cursor.execute('''
        SELECT u.*, cv.cv_file_path, cv.cv_uploaded_at, cv.telefono, cv.data_nascita,
               COUNT(e.id) as total_experiences
        FROM users u
        LEFT JOIN cv_data cv ON u.id = cv.user_id
        LEFT JOIN experiences e ON u.id = e.user_id
        WHERE u.role = 'student'
        GROUP BY u.id
        ORDER BY u.created_at DESC
    ''')
    students = [dict(row) for row in cursor.fetchall()]
    
    # Get statistics
    cursor.execute("SELECT COUNT(*) as total FROM users WHERE role = 'student'")
    total_students = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(DISTINCT user_id) as total FROM cv_data WHERE cv_file_path IS NOT NULL")
    students_with_cv = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM experiences WHERE tipo = 'lavoro'")
    total_work_exp = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM experiences WHERE tipo = 'formazione'")
    total_edu_exp = cursor.fetchone()['total']
    
    conn.close()
    
    # Render student rows
    students_rows_html = _render_students_table(students)
    
    return {
        'user_nome': 'Admin',
        'user_cognome': 'Sistema',
        'total_students': total_students,
        'total_cvs': students_with_cv,
        'total_work_exp': total_work_exp,
        'total_edu_exp': total_edu_exp,
        'students_rows': students_rows_html
    }


def _render_students_table(students):
    """Render students table rows HTML"""
    if not students:
        return '<tr><td colspan="7" class="text-center">Nessuno studente registrato</td></tr>'
    
    html = ''
    for student in students:
        cv_status = '✓' if student.get('cv_file_path') else '✗'
        html += f'''
        <tr>
            <td>{student.get('id')}</td>
            <td>{sanitize_input(student.get('nome', ''))}</td>
            <td>{sanitize_input(student.get('cognome', ''))}</td>
            <td>{sanitize_input(student.get('email', ''))}</td>
            <td>{student.get('data_nascita', 'N/A')}</td>
            <td>{cv_status}</td>
            <td>
                <a href="/admin-view-student?id={student.get('id')}" class="btn btn-primary btn-sm">Visualizza</a>
            </td>
        </tr>
        '''
    
    return html
