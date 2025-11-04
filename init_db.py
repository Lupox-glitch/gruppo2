from database import create_tables, create_default_users


def init_database():
    print("Inizializzazione database MySQL...")
    create_tables()
    print("✓ Tabelle create/già esistenti")
    create_default_users()
    print("✓ Utenti di test presenti/creati")
    print("\n✅ Database inizializzato con successo!")
    print("\nCredenziali di accesso:")
    print("  Admin:    admin@cvmanagement.it / Admin123!")
    print("  Studente: student@test.it / Student123!")


if __name__ == "__main__":
    init_database()
