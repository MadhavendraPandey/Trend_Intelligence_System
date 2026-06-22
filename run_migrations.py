from core.storage.sqlite_storage import SQLiteStorage
import os
import sys

def main():
    db_file = "database/intelligence_platform.sqlite"
    migrations_dir = "database/migrations"

    if not os.path.exists(db_file):
        print(f"Database file not found at {db_file}")
        return

    sys.path.append(os.getcwd())
    storage = SQLiteStorage(db_file=db_file, migrations_dir=migrations_dir)
    print("Applying migrations...")
    storage.initialize()
    print("Migrations applied successfully.")

if __name__ == "__main__":
    main()

