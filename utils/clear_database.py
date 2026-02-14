"""Clear all properties from the database.

Use this when you want to reset the database and fetch fresh data with new search criteria.
"""

import sys

from sqlmodel import Session, create_engine, text


def clear_properties(db_path: str) -> bool:
    """Delete all property records from the database.

    Args:
        db_path: Path to the SQLite database file

    Returns:
        True if successful, False otherwise
    """
    try:
        engine = create_engine(f"sqlite:///{db_path}")
        print(f"Clearing properties from: {db_path}")

        with Session(engine) as session:
            # Count existing properties
            result = session.exec(text("SELECT COUNT(*) FROM property"))
            count = result.fetchone()[0]
            print(f"Found {count} properties in database")

            if count == 0:
                print("Database is already empty")
                return True

            # Delete all properties
            session.exec(text("DELETE FROM property"))
            session.commit()

            # Verify deletion
            result = session.exec(text("SELECT COUNT(*) FROM property"))
            remaining = result.fetchone()[0]

            if remaining == 0:
                print(f"✓ Successfully deleted {count} properties")
                print("✓ Database is now empty and ready for fresh data")
                return True
            else:
                print(f"✗ Warning: {remaining} properties still remain")
                return False

    except Exception as e:
        print(f"✗ Error clearing database {db_path}: {e}")
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Clear property database")
    parser.add_argument("--prod", action="store_true", help="Also clear database.db (production)")
    args = parser.parse_args()

    print("=" * 60)
    print("Clear Property Database")
    print("=" * 60)
    print()

    # Clear test database
    success_test = clear_properties("test.db")

    # Optionally clear production database
    if args.prod:
        print()
        success_prod = clear_properties("database.db")
    else:
        success_prod = True

    print()
    print("=" * 60)
    if success_test and success_prod:
        print("✓ Database clearing completed!")
        print()
        print("Next steps:")
        print("1. Update your search criteria in main.py if needed")
        print("2. Run: uv run python main.py")
        print("3. Run: uv run streamlit run 01_Home.py")
        sys.exit(0)
    else:
        print("✗ Some operations failed. Check errors above.")
        sys.exit(1)
