#!/usr/bin/env python3
"""
Script per inizializzare il database MySQL con tabelle e utenti di test.
Usa le funzioni già presenti in database.py.
"""

from database import create_tables, create_default_users


def init_database():
    print("Inizializzazione database MySQL...")
    create_tables()
    print("✓ Tabelle create/già esistenti")
    create_default_users()
    print("✓ Utenti di test presenti/creati")
    print("\n✅ Database inizializzato con successo!")
    print("\nCredenziali di accesso:")
    print("  Admin:    admin@cvmanagement.it / admin123")
    print("  Studente: student@test.it / student123")


if __name__ == "__main__":
    init_database()
