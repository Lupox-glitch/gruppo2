#!/usr/bin/env python3
"""
Script per inizializzare il database con utenti di test
"""

import database

def init_database():
    """Inizializza il database con le tabelle e gli utenti di test"""
    print("Inizializzazione database...")
    
    # Crea le tabelle
    database.create_tables()
    print("✓ Tabelle create")
    
    # Crea utente admin
    admin_password = database.hash_password("admin123")
    try:
        database.execute_insert(
            "INSERT INTO users (nome, cognome, email, password, ruolo) VALUES (?, ?, ?, ?, ?)",
            ("Admin", "Sistema", "admin@cvmanagement.it", admin_password, "admin")
        )
        print("✓ Utente admin creato (email: admin@cvmanagement.it, password: admin123)")
    except Exception as e:
        print(f"  Admin già esistente o errore: {e}")
    
    # Crea utente studente di test
    student_password = database.hash_password("student123")
    try:
        user_id = database.execute_insert(
            "INSERT INTO users (nome, cognome, email, password, ruolo) VALUES (?, ?, ?, ?, ?)",
            ("Mario", "Rossi", "student@test.it", student_password, "studente")
        )
        
        # Aggiungi dati CV per lo studente
        database.execute_insert(
            "INSERT INTO cv_data (user_id, data_nascita, telefono, indirizzo) VALUES (?, ?, ?, ?)",
            (user_id, "1995-05-15", "3331234567", "Via Roma 123, Milano")
        )
        print("✓ Studente di test creato (email: student@test.it, password: student123)")
    except Exception as e:
        print(f"  Studente di test già esistente o errore: {e}")
    
    print("\n✅ Database inizializzato con successo!")
    print("\nCredenziali di accesso:")
    print("  Admin:    admin@cvmanagement.it / admin123")
    print("  Studente: student@test.it / student123")

if __name__ == "__main__":
    init_database()
