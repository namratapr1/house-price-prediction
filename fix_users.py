from config import get_db_connection

conn   = get_db_connection()
cursor = conn.cursor()

print("Checking users table columns...")

cursor.execute("SHOW COLUMNS FROM users")
cols = [row["Field"] for row in cursor.fetchall()]
print(f"Current columns: {cols}")

# Add email if missing
if "email" not in cols:
    cursor.execute("ALTER TABLE users ADD COLUMN email VARCHAR(255) DEFAULT '' AFTER name")
    conn.commit()
    print("✅ Added email column to users table!")
else:
    print("✓  email column already exists")

# Show final
cursor.execute("SHOW COLUMNS FROM users")
final = [row["Field"] for row in cursor.fetchall()]
print(f"Final columns: {final}")

cursor.close()
conn.close()
print("\n🎉 Done! Restart Flask: python app.py")
