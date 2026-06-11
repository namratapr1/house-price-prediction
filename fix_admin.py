from werkzeug.security import generate_password_hash
from config import get_db_connection

conn   = get_db_connection()
cursor = conn.cursor()

# Step 1: Check admin table exists and has data
cursor.execute("SHOW TABLES LIKE 'admin'")
if not cursor.fetchone():
    print("❌ admin table does not exist! Creating it...")
    cursor.execute("""
        CREATE TABLE admin (
            admin_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    """)
    conn.commit()
    print("✅ admin table created!")

# Step 2: Check if admin row exists
cursor.execute("SELECT * FROM admin WHERE username='admin'")
row = cursor.fetchone()

new_password = "admin123"
hashed = generate_password_hash(new_password)

if row:
    # Update existing
    cursor.execute("UPDATE admin SET password=%s WHERE username='admin'", (hashed,))
    print("✅ Admin password updated!")
else:
    # Insert new
    cursor.execute("INSERT INTO admin (username, password) VALUES ('admin', %s)", (hashed,))
    print("✅ Admin account created!")

conn.commit()

# Step 3: Verify
cursor.execute("SELECT admin_id, username FROM admin")
admins = cursor.fetchall()
print(f"✅ Admin table now has: {admins}")

cursor.close()
conn.close()

print("")
print("=" * 40)
print("  Login at: http://127.0.0.1:5000/admin-login")
print("  Username : admin")
print("  Password : admin123")
print("=" * 40)
