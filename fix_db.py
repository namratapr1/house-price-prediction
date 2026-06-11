from config import get_db_connection

conn   = get_db_connection()
cursor = conn.cursor()

print("Connecting to database...")

# Create about_sections table
cursor.execute("""
CREATE TABLE IF NOT EXISTS about_sections (
    section_id  INT AUTO_INCREMENT PRIMARY KEY,
    title       VARCHAR(200)  NOT NULL,
    body        TEXT          NOT NULL,
    image_path  VARCHAR(300)  DEFAULT '',
    sort_order  INT           DEFAULT 0
)
""")
print("✅ about_sections table created!")

# Seed default data only if table is empty
cursor.execute("SELECT COUNT(*) AS cnt FROM about_sections")
count = cursor.fetchone()["cnt"]

if count == 0:
    cursor.executemany(
        "INSERT INTO about_sections (title, body, sort_order) VALUES (%s, %s, %s)",
        [
            ('Mission ✨',
             'Our mission is to bridge the gap between education and industry by delivering high-quality, accessible learning experiences that inspire innovation and foster practical skills. We aim to build inclusive pathways where every learner can explore, grow, and succeed through personalised and interactive programs.',
             1),
            ('Vision 👁',
             'To be a global leader in innovative education, empowering learners with future-ready skills, industry exposure, and the confidence to thrive in an ever-changing world of work.',
             2),
            ('Aim 🙂',
             'Provide industry-relevant education and hands-on training across diverse fields. Leverage advanced technology to create an engaging and interactive learning platform. Foster critical thinking, creativity, and problem-solving skills in every student.',
             3),
            ('Key Feature 🛠',
             'Incorporates the latest trends and technologies in its curriculum, preparing students for future challenges in their respective industries. Offers a mix of online and in-person classes, allowing students to choose the learning mode that best fits their schedules and preferences.',
             4),
        ]
    )
    print("✅ Default sections inserted!")
else:
    print(f"ℹ️  Table already has {count} rows — skipping seed.")

# Also fix contacts table just in case
cursor.execute("""
CREATE TABLE IF NOT EXISTS contacts (
    contact_id INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    email      VARCHAR(255) NOT NULL,
    subject    VARCHAR(255) NOT NULL,
    message    TEXT         NOT NULL
)
""")
print("✅ contacts table OK!")

# Also fix predictions table just in case
cursor.execute("""
CREATE TABLE IF NOT EXISTS predictions (
    prediction_id      INT AUTO_INCREMENT PRIMARY KEY,
    user_id            INT NOT NULL,
    area               DOUBLE          NOT NULL,
    bedrooms           INT             NOT NULL,
    bathrooms          INT             NOT NULL,
    guest_room         ENUM('yes','no') NOT NULL DEFAULT 'no',
    basement           ENUM('yes','no') NOT NULL DEFAULT 'no',
    air_conditioning   ENUM('yes','no') NOT NULL DEFAULT 'no',
    parking            INT             NOT NULL DEFAULT 0,
    furnishing_status  ENUM('furnished','semi-furnished','unfurnished') NOT NULL,
    city               VARCHAR(100)    NOT NULL,
    state              VARCHAR(100)    NOT NULL,
    predicted_price    DECIMAL(15,2)   NOT NULL,
    CONSTRAINT fk_user_pred
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
)
""")
print("✅ predictions table OK!")

conn.commit()
cursor.close()
conn.close()

print("")
print("🎉 All done! Now run:  python app.py")