"""
Request handlers for CV Management System
All functions use prepared statements for SQL injection prevention
"""

import os
import secrets
from pathlib import Path
from datetime import datetime
from database import (
    get_db_connection, hash_password, salt_generation,verify_password,
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
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
    user = cursor.fetchone()
    conn.close()
    
    if not user or not verify_password(password, user['password_hash'],user['salt']):
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
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id FROM users WHERE email = %s', (email,))
    if cursor.fetchone():
        conn.close()
        return {'success': False, 'error': 'Questa email è già registrata'}
    
    # Insert new user (prepared statement)
    salt=salt_generation()
    password_hash = hash_password(password,salt)
    cursor.execute(
        'INSERT INTO users (email, password_hash, salt, nome, cognome, role) VALUES (%s, %s, %s, %s, %s, "student")',
        (email, password_hash, salt,nome, cognome)
    )
    
    user_id = cursor.lastrowid
    
    # Create cv_data entry
    cursor.execute('INSERT INTO cv_data (user_id) VALUES (%s)', (user_id,))
    
    conn.commit()
    conn.close()
    
    return {'success': True}


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
    if not all([nome, cognome, email, data_nascita]):
        return {'success': False, 'error': 'Nome, cognome, email e data di nascita sono obbligatori'}
    
    if not validate_email(email):
        return {'success': False, 'error': 'Email non valida'}
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Check if email is used by another user (prepared statement)
    cursor.execute('SELECT id FROM users WHERE email = %s AND id != %s', (email, user_id))
    if cursor.fetchone():
        conn.close()
        return {'success': False, 'error': 'Questa email è già utilizzata'}
    
    # Update users table (prepared statement)
    cursor.execute(
        'UPDATE users SET nome = %s, cognome = %s, email = %s WHERE id = %s',
        (nome, cognome, email, user_id)
    )
    
    # Update cv_data (prepared statement)
    cursor.execute('SELECT id FROM cv_data WHERE user_id = %s', (user_id,))
    cv_exists = cursor.fetchone()
    
    if cv_exists:
        cursor.execute(
            'UPDATE cv_data SET telefono = %s, data_nascita = %s, citta = %s, indirizzo = %s, linkedin_url = %s WHERE user_id = %s',
            (telefono, data_nascita, citta, indirizzo, linkedin_url, user_id)
        )
    else:
        cursor.execute(
            'INSERT INTO cv_data (user_id, telefono, data_nascita, citta, indirizzo, linkedin_url) VALUES (%s, %s, %s, %s, %s, %s)',
            (user_id, telefono, data_nascita, citta, indirizzo, linkedin_url)
        )
    
    conn.commit()
    conn.close()
    
    return {'success': True, 'message': 'Profilo aggiornato con successo!'}

def add_cv_content(user_id, data):
    hobby = sanitize_input(data.get('summary', '').strip())
    skills = sanitize_input(data.get('skills', '').strip())
    languages = sanitize_input(data.get('languages', '').strip())
    
    # connessione al db
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    

    cursor.execute(
        'UPDATE cv_data SET hobby = %s, skills = %s, languages = %s WHERE user_id = %s',
        (hobby, skills, languages, user_id)
    )

    conn.commit()
    conn.close()

    return {'success': True, 'message': 'Contenuto CV aggiornato con successo!'}


def handle_add_experience(user_id, data):
    """Handle adding experience with prepared statements"""
    tipo = data.get('tipo', '').strip()
    titolo = sanitize_input(data.get('titolo', '').strip())
    azienda_istituto = sanitize_input((data.get('azienda_istituto') or data.get('azienda') or '').strip())
    data_inizio = data.get('data_inizio', '').strip()
    data_fine = data.get('data_fine', '').strip()
    if data_fine == "":
        is_current = 1
    else:
        is_current=0
    descrizione = sanitize_input(data.get('descrizione', '').strip())
    
    # Validation
    if tipo not in ['lavoro', 'formazione']:
        return {'success': False, 'error': 'Tipo di esperienza non valido'}
    
    if not all([titolo, azienda_istituto, data_inizio]):
        return {'success': False, 'error': 'Tutti i campi obbligatori devono essere compilati'}
    
    if is_current==0 and not data_fine:
        return {'success': False, 'error': 'Data di fine obbligatoria se non in corso'}
    
    if is_current:
        data_fine = None
    
    # Insert experience (prepared statement)
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        'INSERT INTO experiences (user_id, tipo, titolo, azienda_istituto, data_inizio, data_fine, is_current, descrizione) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
        (user_id, tipo, titolo, azienda_istituto, data_inizio, data_fine, is_current, descrizione)
    )
    
    conn.commit()
    conn.close()
    
    return {'success': True, 'message': 'Esperienza aggiunta con successo!'}


def handle_delete_experience(user_id, experience_id):
    """Handle deleting experience with prepared statements"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Verify ownership (prepared statement)
    cursor.execute('SELECT id FROM experiences WHERE id = %s AND user_id = %s', (experience_id, user_id))
    if not cursor.fetchone():
        conn.close()
        return {'success': False, 'error': 'Esperienza non trovata'}
    
    # Delete (prepared statement)
    cursor.execute('DELETE FROM experiences WHERE id = %s AND user_id = %s', (experience_id, user_id))
    
    conn.commit()
    conn.close()
    
    return {'success': True, 'message': 'Esperienza eliminata con successo!'}


def get_user_dashboard_data(user_id):
    """Get all data for user dashboard"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get user data (prepared statement)
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user = dict(cursor.fetchone())
    
    # Get CV data
    cursor.execute(
        'SELECT * FROM cv_data WHERE user_id = %s',
        (user_id,)
    )
    cv_data = cursor.fetchone()
    cv_data = dict(cv_data) if cv_data else {}
    
    # Get experiences
    cursor.execute(
        'SELECT * FROM experiences WHERE user_id = %s ORDER BY data_inizio DESC',
        (user_id,)
    )
    experiences = [dict(row) for row in cursor.fetchall()]
    

    conn.close()
    
    # Sanitize output
    for key in user:
        if isinstance(user[key], str):
            user[key] = sanitize_input(user[key])
    
    for key in cv_data:
        if isinstance(cv_data[key], str):
            cv_data[key] = sanitize_input(cv_data[key])

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
        'cv_hobby': cv_data.get('hobby', ''),
        'cv_skills': cv_data.get('skills', ''),
        'cv_languages': cv_data.get('languages', ''),
        'esperienze_lavorative': _render_experiences(experiences, 'lavoro'),
        'esperienze_formative': _render_experiences(experiences, 'formazione')
    }
    
    return context





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
    cursor = conn.cursor(dictionary=True)
    #cv.cv_file_path, cv.cv_uploaded_at, 
    # Get all students with their data
    cursor.execute(
        """
        SELECT u.id, u.email, u.password_hash, u.salt, u.nome, u.cognome, u.role,
               cv.telefono, cv.data_nascita, cv.indirizzo,
               COUNT(e.id) as total_experiences
        FROM users u
        LEFT JOIN cv_data cv ON u.id = cv.user_id
        LEFT JOIN experiences e ON u.id = e.user_id
        WHERE u.role = 'student'
        GROUP BY u.id, u.email, u.password_hash, u.salt, u.nome, u.cognome, u.role,
                 cv.telefono, cv.data_nascita, cv.indirizzo
        """
    )
    students = cursor.fetchall()
    
    # Get statistics
    cursor.execute("SELECT COUNT(*) as total FROM users WHERE role = 'student'")
    total_students = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(DISTINCT user_id) as total FROM cv_data ") #WHERE cv_file_path IS NOT NULL
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
        return '<tr><td colspan="8" class="text-center">Nessuno studente registrato</td></tr>'
    
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
                <div style="display:flex;gap:0.5rem;">
                    <a href="/admin-view-student?id={student.get('id')}" class="btn btn-primary btn-sm">Visualizza</a>
                    <button onclick="deleteStudent({student.get('id')}, '{sanitize_input(student.get('nome', ''))} {sanitize_input(student.get('cognome', ''))}')" class="btn btn-danger btn-sm">Elimina</button>
                </div>
            </td>
        </tr>
        '''
    
    return html





def get_admin_view_student_data(student_id):
    """Get detailed data for a single student"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get user data
    cursor.execute('SELECT * FROM users WHERE id = %s AND role = "student"', (student_id,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return None
    
    # Get CV data
    cursor.execute('SELECT * FROM cv_data WHERE user_id = %s', (student_id,))
    cv_data = cursor.fetchone()
    cv_data = dict(cv_data) if cv_data else {}
    
    # Get experiences
    cursor.execute(
        'SELECT * FROM experiences WHERE user_id = %s ORDER BY data_inizio DESC',
        (student_id,)
    )
    experiences = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    # Render CV section
    cv_path = cv_data.get('cv_file_path', '')
    if cv_path:
        cv_section_html = f'''
        <div class="alert alert-success">
            <strong>✓ CV caricato:</strong> {cv_path.split('/')[-1]}
            <br>
            <a href="/{cv_path}" class="btn btn-secondary btn-sm" target="_blank">Visualizza CV</a>
            <a href="/{cv_path}" class="btn btn-primary btn-sm" download>Scarica CV</a>
        </div>
        '''
    else:
        cv_section_html = '<p class="text-muted">Nessun CV caricato ancora.</p>'
    
    # Render work experiences
    work_exp = [exp for exp in experiences if exp.get('tipo') == 'lavoro']
    if work_exp:
        work_exp_html = '<div class="experiences-list">'
        for exp in work_exp:
            is_current = exp.get('is_current', 0)
            data_fine = exp.get('data_fine', '')
            periodo = f"{exp.get('data_inizio', '')} - {'In corso' if is_current else data_fine}"
            
            work_exp_html += f'''
            <div class="experience-card">
                <h4>{sanitize_input(exp.get('titolo', ''))}</h4>
                <p class="company">{sanitize_input(exp.get('azienda_istituto', ''))}</p>
                <p class="period">{periodo}</p>
                <p class="description">{sanitize_input(exp.get('descrizione', ''))}</p>
            </div>
            '''
        work_exp_html += '</div>'
    else:
        work_exp_html = '<p class="text-muted">Nessuna esperienza lavorativa.</p>'
    
    # Render education experiences
    edu_exp = [exp for exp in experiences if exp.get('tipo') == 'formazione']
    if edu_exp:
        edu_exp_html = '<div class="experiences-list">'
        for exp in edu_exp:
            is_current = exp.get('is_current', 0)
            data_fine = exp.get('data_fine', '')
            periodo = f"{exp.get('data_inizio', '')} - {'In corso' if is_current else data_fine}"
            
            edu_exp_html += f'''
            <div class="experience-card">
                <h4>{sanitize_input(exp.get('titolo', ''))}</h4>
                <p class="company">{sanitize_input(exp.get('azienda_istituto', ''))}</p>
                <p class="period">{periodo}</p>
                <p class="description">{sanitize_input(exp.get('descrizione', ''))}</p>
            </div>
            '''
        edu_exp_html += '</div>'
    else:
        edu_exp_html = '<p class="text-muted">Nessuna esperienza formativa.</p>'
    
    return {
        'student_id': user.get('id'),
        'nome': sanitize_input(user.get('nome', '')),
        'cognome': sanitize_input(user.get('cognome', '')),
        'email': sanitize_input(user.get('email', '')),
        'telefono': cv_data.get('telefono', 'N/A'),
        'data_nascita': str(cv_data.get('data_nascita', 'N/A')) if cv_data.get('data_nascita') else 'N/A',
        'citta': cv_data.get('citta', 'N/A'),
        'indirizzo': cv_data.get('indirizzo', 'N/A'),
        'linkedin_url': cv_data.get('linkedin_url', 'N/A'),
        'cv_section': cv_section_html,
        'esperienze_lavorative': work_exp_html,
        'esperienze_formative': edu_exp_html
    }




####################################### UPLOAD CV ##################################################################



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
    cursor = conn.cursor(dictionary=True)
    
    # Get old CV path to delete it
    cursor.execute('SELECT cv_file_path FROM cv_data WHERE user_id = %s', (user_id,))
    old_cv = cursor.fetchone()
    
    if old_cv and old_cv['cv_file_path']:
        old_path = Path(__file__).parent / old_cv['cv_file_path']
        if old_path.exists():
            old_path.unlink()
    
    # Update database
    relative_path = f'uploads/cv/{secure_filename}'
    cursor.execute(
        'UPDATE cv_data SET cv_file_path = %s, cv_uploaded_at = CURRENT_TIMESTAMP WHERE user_id = %s',
        (relative_path, user_id)
    )
    
    conn.commit()
    conn.close()
    
    return {'success': True, 'message': 'CV caricato con successo!'}

####################################### fine UPLOAD CV ################################################################## 



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




def handle_admin_delete_user(user_id):
    """Admin: Delete a student user"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Verify user exists and is a student
    cursor.execute('SELECT id, role FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return {'success': False, 'error': 'Utente non trovato'}
    
    if user['role'] != 'student':
        conn.close()
        return {'success': False, 'error': 'Non è possibile eliminare amministratori'}
    
    # Delete user (CASCADE will handle related records)
    cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
    
    conn.commit()
    conn.close()
    
    return {'success': True, 'message': 'Utente eliminato con successo'}



############################## GESTIONE CV PDF ############################################

# handlers.py
from pdf_generator import generate_cv_pdf

def handle_download_cv(user_id):
    try:
        pdf_bytes = generate_cv_pdf(user_id)
        return {'success': True, 'pdf_bytes': pdf_bytes}
    except Exception as e:
        return {'success': False, 'error': str(e)}

################################################################################################

def get_cv_data(user_id):
    """Get CV data for a specific user"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get user data
        cursor.execute(
            'SELECT u.*, cv.* FROM users u LEFT JOIN cv_data cv ON u.id = cv.user_id WHERE u.id = %s',
            (user_id,)
        )
        user_data = cursor.fetchone()
        
        # Get experiences
        cursor.execute(
            'SELECT * FROM experiences WHERE user_id = %s ORDER BY data_inizio DESC',
            (user_id,)
        )
        experiences = cursor.fetchall()
        
        return {
            'success': True,
            'user_data': user_data,
            'experiences': experiences
        }
    
    except Exception as e:
        return {'success': False, 'error': str(e)}
    
    finally:
        conn.close()

def handle_edit_guided_cv(user_id, data, regenerate=True):
    """Aggiorna i dati del CV guidato e opzionalmente rigenera il PDF"""
    # Estraggo e sanitizzo input
    nome = sanitize_input(data.get('nome', '').strip())
    cognome = sanitize_input(data.get('cognome', '').strip())
    email = data.get('email', '').strip()
    telefono = sanitize_input(data.get('telefono', '').strip())
    data_nascita = data.get('data_nascita', '').strip()
    citta = sanitize_input(data.get('citta', '').strip())
    indirizzo = sanitize_input(data.get('indirizzo', '').strip())
    linkedin_url = data.get('linkedin_url', '').strip()

    if not all([nome, cognome, email]):
        return {'success': False, 'error': 'Nome, cognome e email sono obbligatori'}

    if not validate_email(email):
        return {'success': False, 'error': 'Email non valida'}

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Aggiorno tabella users
        cursor.execute(
            'UPDATE users SET nome = %s, cognome = %s, email = %s WHERE id = %s',
            (nome, cognome, email, user_id)
        )

        # Assicuro che esista la riga in cv_data
        cursor.execute('SELECT id, cv_file_path FROM cv_data WHERE user_id = %s', (user_id,))
        cv_row = cursor.fetchone()
        if cv_row:
            cursor.execute(
                'UPDATE cv_data SET telefono = %s, data_nascita = %s, citta = %s, indirizzo = %s, linkedin_url = %s WHERE user_id = %s',
                (telefono, data_nascita, citta, indirizzo, linkedin_url, user_id)
            )
            old_cv_path = cv_row.get('cv_file_path')
        else:
            cursor.execute(
                'INSERT INTO cv_data (user_id, telefono, data_nascita, citta, indirizzo, linkedin_url) VALUES (%s, %s, %s, %s, %s, %s)',
                (user_id, telefono, data_nascita, citta, indirizzo, linkedin_url)
            )
            old_cv_path = None

        # Se richiesto rigenero il PDF usando esperienze correnti
        pdf_relative_path = None
        if regenerate:
            cursor.execute('SELECT * FROM experiences WHERE user_id = %s ORDER BY data_inizio DESC', (user_id,))
            experiences = cursor.fetchall() or []

            # Preparo dati personali per il generatore
            personal_data = {
                'nome': nome,
                'cognome': cognome,
                'email': email,
                'telefono': telefono,
                'data_nascita': data_nascita,
                'citta': citta,
                'indirizzo': indirizzo,
                'linkedin_url': linkedin_url
            }

            from pdf_generator import generate_cv_pdf
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            pdf_filename = f'cv_generated_{user_id}_{timestamp}.pdf'
            UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
            pdf_path = UPLOAD_DIR / pdf_filename

            # Genero PDF
            generate_cv_pdf(pdf_path, personal_data, experiences)

            # Rimuovo vecchio file se presente
            if old_cv_path:
                old_fs_path = Path(__file__).parent / old_cv_path
                if old_fs_path.exists():
                    try:
                        old_fs_path.unlink()
                    except Exception:
                        pass

            pdf_relative_path = f'uploads/cv/{pdf_filename}'
            cursor.execute(
                'UPDATE cv_data SET cv_file_path = %s WHERE user_id = %s',
                (pdf_relative_path, user_id)
            )

        conn.commit()
        return {'success': True, 'message': 'CV aggiornato con successo!', 'pdf_path': pdf_relative_path}
    except Exception as e:
        conn.rollback()
        return {'success': False, 'error': f'Errore durante l\'aggiornamento: {str(e)}'}
    finally:
        conn.close()







def handle_update_experience(user_id, experience_id, data):
    """Aggiorna un'esperienza esistente (proprietà dell'utente obbligatoria)"""
    titolo = sanitize_input(data.get('titolo', '').strip())
    azienda_istituto = sanitize_input(data.get('azienda_istituto', '').strip())
    data_inizio = data.get('data_inizio', '').strip()
    data_fine = data.get('data_fine', '').strip()
    is_current = 1 if data.get('is_current') else 0
    descrizione = sanitize_input(data.get('descrizione', '').strip())
    tipo = data.get('tipo', '').strip()

    if tipo not in ['lavoro', 'formazione']:
        return {'success': False, 'error': 'Tipo di esperienza non valido'}

    if not all([titolo, azienda_istituto, data_inizio]):
        return {'success': False, 'error': 'Titolo, azienda/istituto e data inizio sono obbligatori'}

    if not is_current and not data_fine:
        return {'success': False, 'error': 'Data di fine obbligatoria se non in corso'}

    if is_current:
        data_fine = None

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Verifico proprietà
        cursor.execute('SELECT id FROM experiences WHERE id = %s AND user_id = %s', (experience_id, user_id))
        if not cursor.fetchone():
            return {'success': False, 'error': 'Esperienza non trovata o non autorizzato'}

        # Aggiorno esperienza
        cursor.execute(
            'UPDATE experiences SET tipo = %s, titolo = %s, azienda_istituto = %s, data_inizio = %s, data_fine = %s, is_current = %s, descrizione = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s AND user_id = %s',
            (tipo, titolo, azienda_istituto, data_inizio, data_fine, is_current, descrizione, experience_id, user_id)
        )

        conn.commit()
        return {'success': True, 'message': 'Esperienza aggiornata con successo!'}
    except Exception as e:
        conn.rollback()
        return {'success': False, 'error': str(e)}
    finally:
        conn.close()
