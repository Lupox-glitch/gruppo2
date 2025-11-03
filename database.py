"""
Database module for CV Management System
Switched from SQLite to MySQL.

Configuration via environment variables (with sensible defaults):
  - MYSQL_HOST (default: localhost)
  - MYSQL_PORT (default: 3306)
  - MYSQL_USER (default: root)
  - MYSQL_PASSWORD (default: empty)
  - MYSQL_DB (default: cv_management)
"""

import os
import hashlib
from datetime import datetime


# MySQL configuration from environment
import mysql.connector

MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', '3306'))
MYSQL_USER = os.getenv('MYSQL_USER', 'root')                    # dipende da come lo setti nel sistema  
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '110605')          # dipende da come lo setti nel sistema 
MYSQL_DB = os.getenv('MYSQL_DB', 'cv_management')

def get_db_connection():
    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        port=MYSQL_PORT,
        autocommit=False
    )
    return conn
        
# genera salt randomico
def salt_generation (length=16):     
    return os.urandom(length).hex()


def hash_password(password,salt):
    """Hash password using SHA-256 (in production, use bcrypt)"""
    # Simple hash for demo - in production use bcrypt or argon2
    return hashlib.sha256((password + salt).encode()).hexdigest()


def verify_password(password, hashed , salt):
    """Verify password against hash"""
    return hash_password(password,salt) == hashed


def create_tables():
    """Create database tables in MySQL (if they don't exist)."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # --- Tabella utenti ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            salt VARCHAR(255) NOT NULL,
            nome VARCHAR(100) NOT NULL,
            cognome VARCHAR(100) NOT NULL,
            role ENUM('student','admin') DEFAULT 'student',
            INDEX idx_email (email),
            INDEX idx_role (role)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

    # --- Tabella dati del CV ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cv_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            telefono VARCHAR(20),
            indirizzo VARCHAR(255),
            data_nascita DATE,
            citta VARCHAR(100),
            nazionalita VARCHAR(100),
            linkedin_url VARCHAR(255),
            hobby TEXT,
            skills TEXT,
            languages TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_user_id (user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

    # --- Tabella esperienze ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS experiences (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            tipo ENUM('lavoro','formazione') NOT NULL,
            titolo VARCHAR(255) NOT NULL,
            azienda_istituto VARCHAR(255) NOT NULL,
            data_inizio DATE NOT NULL,
            data_fine DATE,
            descrizione TEXT,
            is_current BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_user_id (user_id),
            INDEX idx_tipo (tipo)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

    # --- tabella lista cv ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_cvs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            cv_file_path VARCHAR(255),
            uploaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_user_id (user_id),
            INDEX idx_uploaded_at (uploaded_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

    conn.commit()
    cursor.close()
    conn.close()



def create_default_users():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Controlla se ci sono già utenti
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    if count > 0:
        cursor.close()
        conn.close()
        return

        # Admin user
    salt=salt_generation()
    cursor.execute(
        'INSERT INTO users (email, password_hash,salt, nome, cognome, role) VALUES (%s, %s, %s, %s, %s, %s)',
        ('admin@cvmanagement.it', hash_password('Admin123!',salt), salt, 'Admin', 'Sistema', 'admin')
    )
    
    # Student user
    salt=salt_generation()
    cursor.execute(
        'INSERT INTO users (email, password_hash, salt, nome, cognome, role) VALUES (%s, %s, %s, %s, %s, %s)',
        ('student@test.it', hash_password('Student123!',salt), salt, 'Mario', 'Rossi', 'student')
    )
    
    student_id = cursor.lastrowid
    
    # Create cv_data entry for student
    cursor.execute(
        'INSERT INTO cv_data (user_id, telefono, citta) VALUES (%s, %s, %s)',
        (student_id, '+39 123 456 7890', 'Milano')
    )
    
    conn.commit()
    conn.close()
    print("✓ Default users created")



# Query functions with prepared statements
def execute_query(query, params=None):
    """Execute a query safely with parameters"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    return result



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
        './': '&#x2F;',
        ';': '&#59;',
        ':': '&#58;'
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



# === Gestione eliminazione CV ===
def get_cv_by_id(cv_id):
    """Restituisce un singolo record CV"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_cvs WHERE id = %s", (cv_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row

def delete_cv(cv_id):
    """Elimina un CV dal database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_cvs WHERE id = %s", (cv_id,))
    conn.commit()
    cursor.close()
    conn.close()


def get_cv_file(user_id):
    """Restituisce l'ultimo CV caricato da un utente (user_cvs)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT cv_file_path FROM user_cvs WHERE user_id = %s ORDER BY uploaded_at DESC LIMIT 1",
        (user_id,)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row[0] if row else None

