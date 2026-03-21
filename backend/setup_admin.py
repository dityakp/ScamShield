"""
setup_admin.py  –  Creates or promotes shantanu15feb0000@gmail.com as admin.
Run: .\venv\Scripts\python.exe setup_admin.py
"""
from app.database import SessionLocal
from app.models import User
from app.auth import hash_password

ADMIN_EMAIL    = "shantanu15feb0000@gmail.com"
ADMIN_NAME     = "Shantanu (Admin)"
ADMIN_PASSWORD = "ScamShield@Admin#2025"

db = SessionLocal()

user = db.query(User).filter(User.email == ADMIN_EMAIL).first()

if user:
    # Account already exists — just make sure it's admin
    user.is_admin = True
    user.is_active = True
    db.commit()
    print(f"\n  [OK] Existing account promoted to admin.")
    print(f"  Email   : {ADMIN_EMAIL}")
    print(f"  Password: (unchanged — use your original password)")
else:
    # Create a fresh admin account
    new_admin = User(
        name=ADMIN_NAME,
        email=ADMIN_EMAIL,
        password_hash=hash_password(ADMIN_PASSWORD),
        is_admin=True,
        is_active=True,
    )
    db.add(new_admin)
    db.commit()
    print(f"\n  [OK] New admin account created!")
    print(f"  Email   : {ADMIN_EMAIL}")
    print(f"  Password: {ADMIN_PASSWORD}")

db.close()
print(f"\n  --> Login at: http://localhost:5500/admin-login.html\n")
