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

import mysql.connector
from mysql.connector import Error, errorcode

# MySQL configuration from environment
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', '3306'))
MYSQL_USER = os.getenv('MYSQL_USER', 'root')                    # dipende da come lo setti nel sistema  
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'admin') # dipende da come lo setti nel sistema 
MYSQL_DB = os.getenv('MYSQL_DB', 'cv_management')


def _ensure_database_exists():
    """Ensure the target MySQL database exists; create it if missing."""
    try:
        # Connect to server without selecting a database
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            autocommit=True,
        )
        cur = conn.cursor()
        cur.execute(
            f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DB}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        cur.close()
        conn.close()
        print(f"✓ Verified database exists: {MYSQL_DB}")
    except Error as err:
        # Surface a clear, actionable message
        msg = (
            f"Failed to ensure database exists (host={MYSQL_HOST} port={MYSQL_PORT} user={MYSQL_USER}). "
            f"MySQL error {getattr(err, 'errno', '?')}: {err}"
        )
        raise RuntimeError(msg) from err


def get_db_connection():
    """Get MySQL database connection, auto-creating the DB if missing, with helpful errors."""
    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            autocommit=False,
        )
        return conn
    except Error as err:
        # Handle "Unknown database" by creating it, then retry once
        if getattr(err, 'errno', None) == errorcode.ER_BAD_DB_ERROR:
            _ensure_database_exists()
            conn = mysql.connector.connect(
                host=MYSQL_HOST,
                port=MYSQL_PORT,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DB,
                autocommit=False,
            )
            return conn
        elif getattr(err, 'errno', None) in (errorcode.ER_ACCESS_DENIED_ERROR, errorcode.ER_DBACCESS_DENIED_ERROR):
            raise RuntimeError(
                "Access denied when connecting to MySQL. Check MYSQL_USER and MYSQL_PASSWORD environment variables."
            ) from err
        elif getattr(err, 'errno', None) in (errorcode.CR_CONN_HOST_ERROR, errorcode.CR_CONNECTION_ERROR, errorcode.CR_CONN_UNKNOW_PROTOCOL):
            raise RuntimeError(
                f"Cannot connect to MySQL at {MYSQL_HOST}:{MYSQL_PORT}. Ensure the server is running and reachable."
            ) from err
        else:
            raise

def salt_generation(length=16):    # genera salt randomico (stringa esadecimale)
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

    # Ensure UTF8MB4 for connection
    cursor.execute("SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci")

    # Users table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            salt VARCHAR(255) NOT NULL,
            nome VARCHAR(100) NOT NULL,
            cognome VARCHAR(100) NOT NULL,
            role ENUM('student','admin') DEFAULT 'student',
            -- created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            -- updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_email (email),
            INDEX idx_role (role)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    )

    # CV Data table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS cv_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            telefono VARCHAR(20),
            indirizzo VARCHAR(255),
            data_nascita DATE,
            citta VARCHAR(100),
            nazionalita VARCHAR(100),
            linkedin_url VARCHAR(255),
            cv_file_path VARCHAR(255),
        --    cv_uploaded_at TIMESTAMP NULL,
        --   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        --    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_user_id (user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    )

    # Experiences table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS experiences (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            tipo ENUM('lavoro','formazione') NOT NULL,
            titolo VARCHAR(255) NOT NULL,
            azienda_istituto VARCHAR(255) NOT NULL,
            data_inizio DATE NOT NULL,
            data_fine DATE,
            descrizione TEXT,
            is_current TINYINT(1) DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_user_id (user_id),
            INDEX idx_tipo (tipo)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    )

    conn.commit()
    conn.close()


def create_default_users():
    """Create default admin and student users"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Check if users already exist
    cursor.execute('SELECT COUNT(*) as count FROM users')
    if cursor.fetchone()['count'] > 0:
        conn.close()
        return  # Users already exist
    
    # Admin user
    salt = salt_generation()
    cursor.execute(
        'INSERT INTO users (email, password_hash, salt, nome, cognome, role) VALUES (%s, %s, %s, %s, %s, %s)',
        ('admin@cvmanagement.it', hash_password('admin123', salt), salt, 'Admin', 'Sistema', 'admin')
    )
    
    # Student user
    salt = salt_generation()
    cursor.execute(
        'INSERT INTO users (email, password_hash, salt, nome, cognome, role) VALUES (%s, %s, %s, %s, %s, %s)',
        ('student@test.it', hash_password('student123', salt), salt, 'Mario', 'Rossi', 'student')
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


def execute_insert(query, params=None):
    """Execute an INSERT query and return last insert ID"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
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
    cursor = conn.cursor(dictionary=True)
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
        '/': '&#x2F;',
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
