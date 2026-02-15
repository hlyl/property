"""Normalize legacy float-like price fields to integers.

This migration updates `price` and `price_m` in the `property` table by
rounding numeric values to the nearest integer.

Why:
- Existing rows may contain float values (e.g. 52681.64) in fields expected
  to be integers by the Pydantic/SQLModel schema.
- This can produce runtime serializer warnings.

Safe to run multiple times.
"""

import argparse
import os
import sqlite3
from typing import Any


def _to_int_or_none(value: Any) -> int | None:
    """Convert incoming value to rounded int, or None if not parseable."""
    if value is None:
        return None
    try:
        if isinstance(value, str):
            cleaned = value.strip().replace(",", ".")
            if cleaned == "":
                return None
            return int(round(float(cleaned)))
        return int(round(float(value)))
    except (TypeError, ValueError):
        return None


def migrate_database(db_path: str) -> None:
    """Normalize price fields in property table for a single database."""
    if not os.path.exists(db_path):
        print(f"Database {db_path} does not exist. Skipping.")
        return

    print(f"Normalizing price fields in: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, price, price_m FROM property")
        rows = cursor.fetchall()

        updated_rows = 0
        updated_price = 0
        updated_price_m = 0

        for row_id, price, price_m in rows:
            new_price = _to_int_or_none(price)
            new_price_m = _to_int_or_none(price_m)

            price_changed = new_price != price
            price_m_changed = new_price_m != price_m

            if price_changed or price_m_changed:
                cursor.execute(
                    "UPDATE property SET price = ?, price_m = ? WHERE id = ?",
                    (new_price, new_price_m, row_id),
                )
                updated_rows += 1
                if price_changed:
                    updated_price += 1
                if price_m_changed:
                    updated_price_m += 1

        conn.commit()
        print(f"✓ Updated {updated_rows} rows (price changed: {updated_price}, price_m changed: {updated_price_m})")

    except Exception as exc:
        conn.rollback()
        print(f"✗ Migration failed for {db_path}: {exc}")
        raise
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize property.price/property.price_m to integers")
    parser.add_argument("--prod", action="store_true", help="Migrate production database (database.db)")
    parser.add_argument("--test", action="store_true", help="Migrate test database (test.db)")
    parser.add_argument("--all", action="store_true", help="Migrate both production and test databases")

    args = parser.parse_args()

    if not (args.prod or args.test or args.all):
        args.prod = True

    if args.all or args.prod:
        migrate_database("database.db")

    if args.all or args.test:
        migrate_database("test.db")


if __name__ == "__main__":
    main()
