from config import get_db_connection

conn   = get_db_connection()
cursor = conn.cursor()

print("Checking predictions table columns...")

# Check existing columns
cursor.execute("SHOW COLUMNS FROM predictions")
cols = [row["Field"] for row in cursor.fetchall()]
print(f"Current columns: {cols}")

# Add missing columns one by one (ignore if already exists)
fixes = [
    ("bedrooms",         "ALTER TABLE predictions ADD COLUMN bedrooms INT NOT NULL DEFAULT 0 AFTER area"),
    ("bathrooms_check",  None),  # already exists, skip
    ("guest_room",       "ALTER TABLE predictions ADD COLUMN guest_room ENUM('yes','no') NOT NULL DEFAULT 'no'"),
    ("basement",         "ALTER TABLE predictions ADD COLUMN basement ENUM('yes','no') NOT NULL DEFAULT 'no'"),
    ("air_conditioning", "ALTER TABLE predictions ADD COLUMN air_conditioning ENUM('yes','no') NOT NULL DEFAULT 'no'"),
    ("parking",          "ALTER TABLE predictions ADD COLUMN parking INT NOT NULL DEFAULT 0"),
    ("furnishing_status","ALTER TABLE predictions ADD COLUMN furnishing_status ENUM('furnished','semi-furnished','unfurnished') NOT NULL DEFAULT 'unfurnished'"),
    ("city",             "ALTER TABLE predictions ADD COLUMN city VARCHAR(100) NOT NULL DEFAULT ''"),
    ("state",            "ALTER TABLE predictions ADD COLUMN state VARCHAR(100) NOT NULL DEFAULT ''"),
    ("price",            "ALTER TABLE predictions ADD COLUMN price DECIMAL(15,2) NOT NULL DEFAULT 0"),
]

for col_name, sql in fixes:
    if col_name == "bathrooms_check":
        continue
    if col_name not in cols:
        try:
            cursor.execute(sql)
            conn.commit()
            print(f"  ✅ Added column: {col_name}")
        except Exception as e:
            print(f"  ⚠️  {col_name}: {e}")
    else:
        print(f"  ✓  Column already exists: {col_name}")

# Rename bhk → bedrooms if bhk exists and bedrooms doesn't
if "bhk" in cols and "bedrooms" not in cols:
    try:
        cursor.execute("ALTER TABLE predictions CHANGE bhk bedrooms INT NOT NULL DEFAULT 0")
        conn.commit()
        print("  ✅ Renamed bhk → bedrooms")
    except Exception as e:
        print(f"  ⚠️  rename bhk: {e}")

# Handle location column - copy to city/state if exists
if "location" in cols:
    # Make sure city and state exist first
    for col, sql in [("city", "ALTER TABLE predictions ADD COLUMN city VARCHAR(100) NOT NULL DEFAULT ''"),
                     ("state","ALTER TABLE predictions ADD COLUMN state VARCHAR(100) NOT NULL DEFAULT ''")]:
        if col not in cols:
            try:
                cursor.execute(sql)
                conn.commit()
            except: pass
    # Copy location data to city
    try:
        cursor.execute("UPDATE predictions SET city = location WHERE city = ''")
        conn.commit()
        print("  ✅ Copied location → city")
    except Exception as e:
        print(f"  ⚠️  copy location: {e}")

conn.commit()

# Show final columns
cursor.execute("SHOW COLUMNS FROM predictions")
final_cols = [row["Field"] for row in cursor.fetchall()]
print(f"\nFinal columns: {final_cols}")

cursor.close()
conn.close()

print("\n🎉 Done! Now restart Flask:  python app.py")
