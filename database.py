"""
Database module for CV Management System
Using SQLite for simplicity (no MySQL required)
"""

import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / 'cv_management.db'


def get_db_connection():
    """Get database connection with proper settings"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn


def hash_password(password):
    """Hash password using SHA-256 (in production, use bcrypt)"""
    # Simple hash for demo - in production use bcrypt or argon2
    salt = "cv_management_salt_2025"
    return hashlib.sha256((password + salt).encode()).hexdigest()


def verify_password(password, hashed):
    """Verify password against hash"""
    return hash_password(password) == hashed


def create_tables():
    """Create database tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            nome TEXT NOT NULL,
            cognome TEXT NOT NULL,
            role TEXT DEFAULT 'student' CHECK(role IN ('student', 'admin')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # CV Data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cv_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            telefono TEXT,
            indirizzo TEXT,
            data_nascita DATE,
            citta TEXT,
            linkedin_url TEXT,
            cv_file_path TEXT,
            cv_uploaded_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Experiences table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS experiences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            tipo TEXT NOT NULL CHECK(tipo IN ('lavoro', 'formazione')),
            titolo TEXT NOT NULL,
            azienda_istituto TEXT NOT NULL,
            data_inizio DATE NOT NULL,
            data_fine DATE,
            descrizione TEXT,
            is_current INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()


def create_default_users():
    """Create default admin and student users"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if users already exist
    cursor.execute('SELECT COUNT(*) as count FROM users')
    if cursor.fetchone()['count'] > 0:
        conn.close()
        return  # Users already exist
    
    # Admin user
    cursor.execute('''
        INSERT INTO users (email, password_hash, nome, cognome, role)
        VALUES (?, ?, ?, ?, ?)
    ''', ('admin@cvmanagement.it', hash_password('admin123'), 'Admin', 'Sistema', 'admin'))
    
    # Student user
    cursor.execute('''
        INSERT INTO users (email, password_hash, nome, cognome, role)
        VALUES (?, ?, ?, ?, ?)
    ''', ('student@test.it', hash_password('student123'), 'Mario', 'Rossi', 'student'))
    
    student_id = cursor.lastrowid
    
    # Create cv_data entry for student
    cursor.execute('''
        INSERT INTO cv_data (user_id, telefono, citta)
        VALUES (?, ?, ?)
    ''', (student_id, '+39 123 456 7890', 'Milano'))
    
    conn.commit()
    conn.close()
    print("✓ Default users created")


# Query functions with prepared statements
def execute_query(query, params=None):
    """Execute a query safely with parameters"""
    conn = get_db_connection()
    cursor = conn.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    return result


def execute_insert(query, params=None):
    """Execute an INSERT query and return last insert ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    last_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return last_id


def execute_update(query, params=None):
    """Execute an UPDATE/DELETE query"""
    conn = get_db_connection()
    cursor = conn.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected


# Security functions
def sanitize_input(text):
    """Sanitize user input (basic XSS prevention)"""
    if not text:
        return ''
    # Replace dangerous characters
    replacements = {
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;',
        '/': '&#x2F;'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def validate_email(email):
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "La password deve contenere almeno 8 caratteri"
    if not any(c.isupper() for c in password):
        return False, "La password deve contenere almeno una lettera maiuscola"
    if not any(c.islower() for c in password):
        return False, "La password deve contenere almeno una lettera minuscola"
    if not any(c.isdigit() for c in password):
        return False, "La password deve contenere almeno un numero"
    return True, ""
