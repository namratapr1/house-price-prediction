"""
Run this ONCE after running House_db.sql.
It sets a properly hashed password for the admin account.

Command: python set_admin_password.py
"""
from werkzeug.security import generate_password_hash
from config import get_db_connection

ADMIN_PASSWORD = "admin123"   # Change this if you want a different password

hashed = generate_password_hash(ADMIN_PASSWORD)

conn   = get_db_connection()
cursor = conn.cursor()
cursor.execute("UPDATE admin SET password=%s WHERE username='admin'", (hashed,))
conn.commit()
cursor.close()
conn.close()

print("✅ Admin password set successfully!")
print(f"   Username : admin")
print(f"   Password : {ADMIN_PASSWORD}")
