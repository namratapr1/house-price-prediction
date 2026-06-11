"""
fix_predictions_table.py
Run this ONCE to fix your existing predictions table.
It renames/adds columns to match the current app.py schema.

Command: python fix_predictions_table.py
"""
from config import get_db_connection

conn   = get_db_connection()
cursor = conn.cursor()

print("=" * 50)
print("Fixing predictions table schema...")
print("=" * 50)

# Step 1: Show current columns
cursor.execute("SHOW COLUMNS FROM predictions")
cols = [row["Field"] for row in cursor.fetchall()]
print(f"\nCurrent columns: {cols}\n")

fixes_applied = []

# Step 2: Rename 'bhk' -> 'bedrooms' if needed
if "bhk" in cols and "bedrooms" not in cols:
    cursor.execute("ALTER TABLE predictions CHANGE bhk bedrooms INT NOT NULL DEFAULT 0")
    conn.commit()
    fixes_applied.append("✅ Renamed 'bhk' → 'bedrooms'")
elif "bedrooms" in cols:
    fixes_applied.append("✓  'bedrooms' column already exists")
else:
    cursor.execute("ALTER TABLE predictions ADD COLUMN bedrooms INT NOT NULL DEFAULT 0 AFTER area")
    conn.commit()
    fixes_applied.append("✅ Added 'bedrooms' column")

# Step 3: Rename 'location' -> 'city' if needed
if "location" in cols and "city" not in cols:
    cursor.execute("ALTER TABLE predictions CHANGE location city VARCHAR(100) NOT NULL DEFAULT ''")
    conn.commit()
    fixes_applied.append("✅ Renamed 'location' → 'city'")
elif "city" in cols:
    fixes_applied.append("✓  'city' column already exists")

# Step 4: Add 'state' if missing
cursor.execute("SHOW COLUMNS FROM predictions")
cols = [row["Field"] for row in cursor.fetchall()]
if "state" not in cols:
    cursor.execute("ALTER TABLE predictions ADD COLUMN state VARCHAR(100) NOT NULL DEFAULT ''")
    conn.commit()
    fixes_applied.append("✅ Added 'state' column")
else:
    fixes_applied.append("✓  'state' column already exists")

# Step 5: Add 'guest_room' if missing
if "guest_room" not in cols:
    cursor.execute("ALTER TABLE predictions ADD COLUMN guest_room ENUM('yes','no') NOT NULL DEFAULT 'no'")
    conn.commit()
    fixes_applied.append("✅ Added 'guest_room' column")
else:
    fixes_applied.append("✓  'guest_room' column already exists")

# Step 6: Add 'basement' if missing
if "basement" not in cols:
    cursor.execute("ALTER TABLE predictions ADD COLUMN basement ENUM('yes','no') NOT NULL DEFAULT 'no'")
    conn.commit()
    fixes_applied.append("✅ Added 'basement' column")
else:
    fixes_applied.append("✓  'basement' column already exists")

# Step 7: Add 'air_conditioning' if missing
if "air_conditioning" not in cols:
    cursor.execute("ALTER TABLE predictions ADD COLUMN air_conditioning ENUM('yes','no') NOT NULL DEFAULT 'no'")
    conn.commit()
    fixes_applied.append("✅ Added 'air_conditioning' column")
else:
    fixes_applied.append("✓  'air_conditioning' column already exists")

# Step 8: Add 'parking' if missing
if "parking" not in cols:
    cursor.execute("ALTER TABLE predictions ADD COLUMN parking INT NOT NULL DEFAULT 0")
    conn.commit()
    fixes_applied.append("✅ Added 'parking' column")
else:
    fixes_applied.append("✓  'parking' column already exists")

# Step 9: Add 'furnishing_status' if missing
if "furnishing_status" not in cols:
    cursor.execute("""
        ALTER TABLE predictions 
        ADD COLUMN furnishing_status 
        ENUM('furnished','semi-furnished','unfurnished') NOT NULL DEFAULT 'unfurnished'
    """)
    conn.commit()
    fixes_applied.append("✅ Added 'furnishing_status' column")
else:
    fixes_applied.append("✓  'furnishing_status' column already exists")

# Step 10: Drop 'price' column if it exists (we don't use it)
cursor.execute("SHOW COLUMNS FROM predictions")
cols = [row["Field"] for row in cursor.fetchall()]
if "price" in cols:
    cursor.execute("ALTER TABLE predictions DROP COLUMN price")
    conn.commit()
    fixes_applied.append("✅ Dropped unused 'price' column")

# Step 11: Drop 'bhk' if it still exists alongside bedrooms
if "bhk" in cols:
    cursor.execute("ALTER TABLE predictions DROP COLUMN bhk")
    conn.commit()
    fixes_applied.append("✅ Dropped old 'bhk' column")

# Step 12: Drop 'location' if it still exists alongside city
if "location" in cols:
    cursor.execute("ALTER TABLE predictions DROP COLUMN location")
    conn.commit()
    fixes_applied.append("✅ Dropped old 'location' column")

# Print results
print("Changes made:")
for f in fixes_applied:
    print(" ", f)

# Final state
cursor.execute("SHOW COLUMNS FROM predictions")
final_cols = [row["Field"] for row in cursor.fetchall()]
print(f"\nFinal columns: {final_cols}")

cursor.close()
conn.close()

print("\n" + "=" * 50)
print("✅ Done! Now run:  python app.py")
print("=" * 50)
