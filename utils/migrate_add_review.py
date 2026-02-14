"""Database migration script to add review tracking fields.

Adds review_status and reviewed_date columns to the property table.
Safe to run multiple times - checks if columns exist before adding.
"""

import sys

from sqlmodel import Session, create_engine, text


def migrate_add_review_fields(db_path: str) -> bool:
    """Add review_status and reviewed_date fields to existing database.

    Args:
        db_path: Path to the SQLite database file

    Returns:
        True if migration successful, False otherwise
    """
    try:
        engine = create_engine(f"sqlite:///{db_path}")
        print(f"Migrating database: {db_path}")

        with Session(engine) as session:
            # Check existing columns
            result = session.exec(text("PRAGMA table_info(property)"))
            columns = [row[1] for row in result.fetchall()]
            print(f"Found {len(columns)} existing columns")

            # Add review_status if not exists
            if 'review_status' not in columns:
                session.exec(text(
                    "ALTER TABLE property ADD COLUMN review_status VARCHAR DEFAULT 'To Review'"
                ))
                print("✓ Added review_status column")
            else:
                print("→ review_status column already exists")

            # Add reviewed_date if not exists
            if 'reviewed_date' not in columns:
                session.exec(text(
                    "ALTER TABLE property ADD COLUMN reviewed_date VARCHAR"
                ))
                print("✓ Added reviewed_date column")
            else:
                print("→ reviewed_date column already exists")

            session.commit()
            print(f"✓ Migration completed successfully for {db_path}\n")
            return True

    except Exception as e:
        print(f"✗ Migration failed for {db_path}: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Property Review Tracking - Database Migration")
    print("=" * 60)
    print()

    # Migrate test database
    success_test = migrate_add_review_fields("test.db")

    # Migrate production database
    success_prod = migrate_add_review_fields("database.db")

    print("=" * 60)
    if success_test and success_prod:
        print("✓ All migrations completed successfully!")
        sys.exit(0)
    else:
        print("✗ Some migrations failed. Check errors above.")
        sys.exit(1)
