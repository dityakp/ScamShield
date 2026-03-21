"""
migrate_admin_columns.py
Safely adds is_admin and is_active columns to the users table.
Run with: python migrate_admin_columns.py
"""
from sqlalchemy import text
from app.database import engine, SessionLocal
from app.models import User
from app.auth import hash_password

def add_column_if_missing(conn, table, column, col_type, default):
    """Add a column only if it doesn't already exist."""
    result = conn.execute(text(
        f"""
        SELECT column_name FROM information_schema.columns
        WHERE table_name='{table}' AND column_name='{column}'
        """
    ))
    if result.fetchone() is None:
        conn.execute(text(
            f"ALTER TABLE {table} ADD COLUMN {column} {col_type} NOT NULL DEFAULT {default}"
        ))
        print(f"  [OK] Added column: {table}.{column}")
    else:
        print(f"  [--] Column already exists: {table}.{column}")

print("\n=== ScamShield – Admin Migration ===")
with engine.connect() as conn:
    add_column_if_missing(conn, "users", "is_admin", "BOOLEAN", "FALSE")
    add_column_if_missing(conn, "users", "is_active", "BOOLEAN", "TRUE")
    conn.commit()

print("\n[OK] Migration complete.\n")

# --- List existing users so user can pick which to promote ---
db = SessionLocal()
users = db.query(User).all()
if not users:
    print("No users found in the database yet.")
    print("Please register an account on the website first, then re-run this script.\n")
else:
    print("Registered users:")
    for u in users:
        role = " [ADMIN]" if u.is_admin else ""
        print(f"  ID={u.id}  {u.email}{role}")
    
    print()
    choice = input("Enter the email to promote to admin (or press Enter to skip): ").strip()
    if choice:
        target = db.query(User).filter(User.email == choice).first()
        if target:
            target.is_admin = True
            db.commit()
            print(f"\n  [OK] '{target.email}' is now an admin!")
            print(f"  --> Go to http://localhost:5500/admin-login.html and log in.\n")
        else:
            print(f"  [!] No user found with email: {choice}")
    else:
        print("  Skipped promotion. Run again anytime to promote a user.\n")

db.close()
