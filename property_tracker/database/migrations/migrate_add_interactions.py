"""Add property interaction fields to database.

Adds: favorite, viewed, hidden, notes columns
"""

import sys

from sqlmodel import Session, create_engine, text


def add_interaction_fields(db_path: str) -> bool:
    """Add interaction fields to property table.

    Args:
        db_path: Path to the SQLite database file

    Returns:
        True if successful, False otherwise
    """
    try:
        engine = create_engine(f"sqlite:///{db_path}")
        print(f"\nAdding interaction fields to: {db_path}")

        with Session(engine) as session:
            # Check existing columns
            result = session.exec(text("PRAGMA table_info(property)"))
            columns = {row[1] for row in result.fetchall()}

            added = []

            # Add missing columns
            if "favorite" not in columns:
                session.exec(text("ALTER TABLE property ADD COLUMN favorite INTEGER DEFAULT 0"))
                added.append("favorite")

            if "viewed" not in columns:
                session.exec(text("ALTER TABLE property ADD COLUMN viewed INTEGER DEFAULT 0"))
                added.append("viewed")

            if "hidden" not in columns:
                session.exec(text("ALTER TABLE property ADD COLUMN hidden INTEGER DEFAULT 0"))
                added.append("hidden")

            if "notes" not in columns:
                session.exec(text("ALTER TABLE property ADD COLUMN notes TEXT"))
                added.append("notes")

            session.commit()

            if added:
                print(f"✓ Added columns: {', '.join(added)}")
            else:
                print("✓ All interaction fields already exist")

            return True

    except Exception as e:
        print(f"✗ Error adding interaction fields to {db_path}: {e}")
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Add interaction fields to property database")
    parser.add_argument("--prod", action="store_true", help="Also add to database.db (production)")
    args = parser.parse_args()

    print("=" * 60)
    print("Add Property Interaction Fields Migration")
    print("=" * 60)

    # Run on test database
    success_test = add_interaction_fields("test.db")

    # Optionally run on production database
    if args.prod:
        print()
        success_prod = add_interaction_fields("database.db")
    else:
        success_prod = True

    print()
    print("=" * 60)
    if success_test and success_prod:
        print("✓ Migration completed successfully!")
        print()
        print("New fields added:")
        print("  - favorite (INTEGER, default 0)")
        print("  - viewed (INTEGER, default 0)")
        print("  - hidden (INTEGER, default 0)")
        print("  - notes (TEXT, nullable)")
        sys.exit(0)
    else:
        print("✗ Migration failed. Check errors above.")
        sys.exit(1)
