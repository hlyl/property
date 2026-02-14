"""Migration to add province and city columns to property table.

This migration adds the province and city columns that are missing from older
database schemas.
"""

import argparse
import os
import sqlite3


def check_column_exists(cursor, table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table.

    Args:
        cursor: SQLite cursor
        table_name: Name of the table
        column_name: Name of the column to check

    Returns:
        True if column exists, False otherwise
    """
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns


def migrate_database(db_path: str) -> None:
    """Add province and city columns to property table if they don't exist.

    Args:
        db_path: Path to the database file
    """
    if not os.path.exists(db_path):
        print(f"Database {db_path} does not exist. No migration needed.")
        return

    print(f"Migrating database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if columns already exist
        has_province = check_column_exists(cursor, "property", "province")
        has_city = check_column_exists(cursor, "property", "city")

        if has_province and has_city:
            print("✓ Database already has province and city columns. No migration needed.")
            return

        # Add province column if missing
        if not has_province:
            print("Adding province column...")
            cursor.execute("ALTER TABLE property ADD COLUMN province TEXT")
            print("✓ Added province column")
        else:
            print("✓ Province column already exists")

        # Add city column if missing
        if not has_city:
            print("Adding city column...")
            cursor.execute("ALTER TABLE property ADD COLUMN city TEXT")
            print("✓ Added city column")
        else:
            print("✓ City column already exists")

        conn.commit()
        print(f"\n✓ Migration completed successfully for {db_path}")

    except Exception as e:
        conn.rollback()
        print(f"✗ Migration failed: {e}")
        raise
    finally:
        conn.close()


def main():
    """Run migration on production and/or test databases."""
    parser = argparse.ArgumentParser(description="Add province and city columns to property table")
    parser.add_argument(
        "--prod",
        action="store_true",
        help="Migrate production database (database.db)",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Migrate test database (test.db)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Migrate both production and test databases",
    )

    args = parser.parse_args()

    # Default to production if no flags specified
    if not (args.prod or args.test or args.all):
        args.prod = True

    # Migrate databases
    if args.all or args.prod:
        migrate_database("database.db")

    if args.all or args.test:
        migrate_database("test.db")


if __name__ == "__main__":
    main()
