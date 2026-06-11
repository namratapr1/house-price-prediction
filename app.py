from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from config import get_db_connection
import csv, os, traceback

app = Flask(__name__)
app.secret_key = "jyesta_secret_key_2025"

UPLOAD_FOLDER = os.path.join("static", "uploads")
ALLOWED_EXT   = {"png", "jpg", "jpeg", "gif", "webp"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


CHATBOT_RULES = [
    (["hello","hi","hey","namaste","good morning","good evening","howdy"],
     "👋 Hello! Welcome to Jyesta! I can help you with house price questions, prediction details, or platform info. What would you like to know?"),
    (["predict","prediction","how to predict","estimate price","calculate price","get price"],
     "🏠 To predict a house price, go to the 'How It Works' page, fill in Area, BHK, Bathrooms, Parking, Amenities and City — then click 'Predict Price'. Our model gives you an instant estimate!"),
    (["area","sq ft","square feet","size","sqft"],
     "📐 Area is the biggest price factor. Our model multiplies area (sq. ft.) by ₹5,000 as the base rate."),
    (["bhk","bedroom","bedrooms","1bhk","2bhk","3bhk","room"],
     "🛏 Each BHK adds ₹1,00,000 to the price."),
    (["bathroom","bathrooms","bath","washroom"],
     "🚿 Each bathroom adds ₹50,000 to the predicted price."),
    (["parking","garage","car parking","car space"],
     "🚗 Each parking spot adds ₹75,000."),
    (["furnish","furnished","semi-furnished","unfurnished","furniture","interior"],
     "🛋 Furnishing adds:\n• Furnished: +₹2,00,000\n• Semi-Furnished: +₹1,00,000\n• Unfurnished: ₹0 extra"),
    (["ac","air conditioning","air conditioner","cooling","climate"],
     "❄️ Air conditioning adds ₹1,20,000 to the price."),
    (["guest room","guestroom","guest","extra room"],
     "🏠 A guest room adds ₹1,50,000 to the value."),
    (["basement","underground","lower floor"],
     "🏗 A basement adds ₹1,00,000 to the price."),
    (["location","city","where","mumbai","delhi","bangalore","chennai","hyderabad",
      "pune","kolkata","ahmedabad","jaipur","surat","lucknow","kochi","indore"],
     "📍 We support 20 major Indian cities — Mumbai, Delhi, Bangalore, Hyderabad, Chennai, Pune, Kolkata, Ahmedabad, Jaipur, Surat, and more."),
    (["how","model","algorithm","regression","formula","works","calculation","logic"],
     "🔢 Price = (Area × ₹5,000) + (BHK × ₹1,00,000) + (Bath × ₹50,000) + (Parking × ₹75,000) + Guest Room + Basement + AC + Furnishing bonus"),
    (["accurate","accuracy","reliable","correct","trust","real"],
     "✅ Our model gives a solid estimate. For legal valuation, consult a certified property valuator."),
    (["register","signup","sign up","account","create account","new user"],
     "📝 Click 'Login' → 'Create Account' in the navigation bar to register for free."),
    (["login","sign in","signin","password","forgot"],
     "🔐 Click 'Login' in the top navigation to sign in."),
    (["contact","support","help","reach","email","phone","call"],
     "📞 Phone: +91 63605 84544 | Email: info@jyesta.com"),
    (["jyesta","company","about","who are you","what is jyesta","platform"],
     "🏢 Jyesta Corporate Entity is a technology-driven platform for real estate analytics and house price prediction across India."),
    (["price","cost","value","worth","expensive","cheap","affordable","rate","lakh","crore"],
     "💰 Example estimates:\n• 1000 sq.ft 2BHK Bangalore: ~₹55-70L\n• 2000 sq.ft 3BHK Mumbai: ~₹1.5-2Cr"),
    (["dashboard","history","my predictions","past","previous","record"],
     "📊 After logging in, visit your Dashboard to see all past predictions."),
    (["chart","graph","regression","scatter","visual","plot"],
     "📈 After each prediction, we show a Price vs Area linear regression chart with your property highlighted as a red star ⭐."),
    (["thank","thanks","thank you","helpful","great","awesome","nice","good"],
     "😊 You're welcome! Feel free to ask anything else."),
    (["bye","goodbye","see you","exit","quit","cya"],
     "👋 Goodbye! Good luck with your property search! 🏠"),
    (["property","buy","purchase","buying","sale","sell","enquiry","enquire"],
     "🏡 Visit our Property page to browse listings and submit a buying enquiry!"),
]

def get_bot_reply(user_message):
    msg = user_message.lower().strip()
    for keywords, reply in CHATBOT_RULES:
        if any(kw in msg for kw in keywords):
            return reply
    return ("🤔 I can help you with:\n• House price prediction\n• Area, BHK, bathrooms, amenities\n• How the model works\n• Platform features & login\n\nTry: 'How does prediction work?'")


# =============================================================================
# PUBLIC PAGES
# =============================================================================

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    conn = get_db_connection(); cursor = conn.cursor()
    cursor.execute("SELECT * FROM about_sections ORDER BY sort_order ASC")
    sections = cursor.fetchall()
    cursor.close(); conn.close()
    return render_template("about.html", sections=sections)

@app.route("/how-it-works")
def how_it_works():
    return render_template("how_it_works.html")

@app.route("/faq")
def faq():
    return render_template("faq.html")


# =============================================================================
# PROPERTY PAGE
# =============================================================================

@app.route("/property")
def property_page():
    return render_template("property.html")

@app.route("/property/enquiry", methods=["POST"])
def property_enquiry():
    try:
        name          = request.form["name"].strip()
        email         = request.form["email"].strip()
        phone         = request.form["phone"].strip()
        property_type = request.form["property_type"].strip()
        city          = request.form["city"].strip()
        budget        = request.form["budget"].strip()
        bedrooms      = request.form.get("bedrooms", "").strip()
        amenities     = ", ".join(request.form.getlist("amenities"))
        message       = request.form.get("message", "").strip()
        conn = get_db_connection(); cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO property_enquiries
            (name, email, phone, property_type, city, budget, bedrooms, amenities, message)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (name, email, phone, property_type, city, budget, bedrooms, amenities, message))
        conn.commit(); cursor.close(); conn.close()
        flash("✅ Enquiry submitted! Our team will contact you within 24 hours.", "success")
    except Exception as e:
        traceback.print_exc()
        flash(f"❌ Error: {str(e)}", "error")
    return redirect(url_for("property_page"))


# =============================================================================
# CONTACT
# =============================================================================

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name    = request.form["name"].strip()
        email   = request.form["email"].strip()
        subject = request.form["subject"].strip()
        message = request.form["message"].strip()
        try:
            conn = get_db_connection(); cursor = conn.cursor()
            cursor.execute("INSERT INTO contacts (name, email, subject, message) VALUES (%s,%s,%s,%s)",
                           (name, email, subject, message))
            conn.commit(); cursor.close(); conn.close()
            flash("✅ Message sent! We will get back to you soon.", "success")
        except Exception as e:
            traceback.print_exc()
            flash(f"❌ Error: {str(e)}", "error")
        return redirect(url_for("contact"))
    return render_template("contact.html")


# =============================================================================
# CHATBOT
# =============================================================================

@app.route("/chatbot", methods=["POST"])
def chatbot():
    data     = request.get_json()
    messages = data.get("messages", [])
    if not messages:
        return jsonify({"reply": "Please send a message."}), 400
    reply = get_bot_reply(messages[-1].get("content", ""))
    return jsonify({"reply": reply})


# =============================================================================
# AUTH
# =============================================================================

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name             = request.form["name"].strip()
        email            = request.form.get("email", "").strip()
        password         = request.form["password"]
        confirm_password = request.form["confirm_password"]
        if password != confirm_password:
            flash("❌ Passwords do not match!", "error")
            return render_template("register.html")
        hashed = generate_password_hash(password)
        conn = get_db_connection(); cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (name, email, password) VALUES (%s,%s,%s)", (name, email, hashed))
            conn.commit()
            flash("✅ Registration successful! Please login.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            err = str(e)
            if "Duplicate entry" in err and "users.name" in err:
                flash(f"❌ Username '{name}' is already taken. Please choose a different username.", "error")
            elif "Duplicate entry" in err and "users.email" in err:
                flash(f"❌ This email is already registered. Please use a different email.", "error")
            else:
                flash(f"❌ Error: {err}", "error")
        finally:
            cursor.close(); conn.close()
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name     = request.form["name"]
        password = request.form["password"]
        conn = get_db_connection(); cursor = conn.cursor()
        cursor.execute("SELECT user_id, name, password FROM users WHERE name=%s", (name,))
        user = cursor.fetchone()
        cursor.close(); conn.close()
        if user is None:
            flash("❌ User does not exist!", "error")
            return render_template("login.html")
        if check_password_hash(user["password"], password):
            session["user_id"]   = user["user_id"]
            session["user_name"] = user["name"]
            flash(f"✅ Welcome back, {user['name']}!", "success")
            return redirect(url_for("how_it_works"))
        flash("❌ Invalid Username or Password!", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# =============================================================================
# USER DASHBOARD
# =============================================================================

@app.route("/user-dashboard")
def user_dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = get_db_connection(); cursor = conn.cursor()
    cursor.execute("""
        SELECT prediction_id, area, bedrooms, bathrooms,
               guest_room, basement, air_conditioning, parking,
               furnishing_status, city, state, predicted_price
        FROM predictions WHERE user_id=%s ORDER BY prediction_id DESC
    """, (session["user_id"],))
    predictions = cursor.fetchall()
    cursor.close(); conn.close()
    return render_template("user_dashboard.html", predictions=predictions)


# =============================================================================
# COMPARE
# =============================================================================

@app.route("/compare")
def compare():
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = get_db_connection(); cursor = conn.cursor()
    cursor.execute("""
        SELECT prediction_id, area, bedrooms, bathrooms,
               guest_room, basement, air_conditioning, parking,
               furnishing_status, city, state, predicted_price
        FROM predictions WHERE user_id=%s ORDER BY prediction_id DESC
    """, (session["user_id"],))
    predictions = cursor.fetchall()

    p1 = p2 = None
    pid1 = request.args.get("p1", type=int)
    pid2 = request.args.get("p2", type=int)
    if pid1 and pid2:
        for p in predictions:
            if p["prediction_id"] == pid1:
                p1 = p
            if p["prediction_id"] == pid2:
                p2 = p

    cursor.close(); conn.close()
    return render_template("compare.html", predictions=predictions, p1=p1, p2=p2)

# =============================================================================
# PREDICT
# =============================================================================

@app.route("/predict", methods=["POST"])
def predict():
    if "user_id" not in session:
        flash("❌ Please login first.", "error")
        return redirect(url_for("login"))
    try:
        area             = float(request.form["area"])
        bedrooms         = int(request.form["bedrooms"])
        bathrooms        = int(request.form["bathrooms"])
        parking          = int(request.form["parking"])
        guestroom        = request.form["guestroom"]
        basement         = request.form["basement"]
        airconditioning  = request.form["airconditioning"]
        furnishingstatus = request.form["furnishingstatus"]
        city             = request.form["city"]
        state            = request.form["state"]

        furnish_score = {"furnished": 200000, "semi-furnished": 100000, "unfurnished": 0}
        predicted_price = (
            area * 5000
            + bedrooms   * 100000
            + bathrooms  * 50000
            + parking    * 75000
            + (150000 if guestroom       == "yes" else 0)
            + (100000 if basement        == "yes" else 0)
            + (120000 if airconditioning == "yes" else 0)
            + furnish_score.get(furnishingstatus, 0)
        )

        conn = get_db_connection(); cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO predictions
            (user_id, area, bedrooms, bathrooms,
             guest_room, basement, air_conditioning, parking,
             furnishing_status, city, state, predicted_price)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (session["user_id"],
              area, bedrooms, bathrooms,
              guestroom, basement, airconditioning, parking,
              furnishingstatus, city, state,
              round(predicted_price, 2)))
        conn.commit(); cursor.close(); conn.close()

        scatter_data = []
        csv_path = os.path.join(app.root_path, "Housing_India.csv")
        if os.path.exists(csv_path):
            with open(csv_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        scatter_data.append({"x": float(row["area"]), "y": float(row["price"])})
                    except (ValueError, KeyError):
                        pass

        return render_template("result.html",
            predicted_price  = "{:,.0f}".format(round(predicted_price, 2)),
            area=int(area), bedrooms=bedrooms, bathrooms=bathrooms,
            parking=parking, furnishingstatus=furnishingstatus,
            airconditioning=airconditioning, city=city, state=state,
            scatter_data=scatter_data,
            user_point={"x": area, "y": round(predicted_price, 2)})
    except Exception as e:
        traceback.print_exc()
        flash(f"❌ Prediction error: {str(e)}", "error")
        return redirect(url_for("how_it_works"))


# =============================================================================
# ADMIN AUTH
# =============================================================================

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db_connection(); cursor = conn.cursor()
        cursor.execute("SELECT admin_id, username, password FROM admin WHERE username=%s", (username,))
        admin = cursor.fetchone()
        cursor.close(); conn.close()
        if admin is None:
            flash("❌ Admin does not exist!", "error")
            return render_template("admin_login.html")
        if check_password_hash(admin["password"], password):
            session["admin_id"]   = admin["admin_id"]
            session["admin_name"] = admin["username"]
            return redirect(url_for("admin_dashboard"))
        flash("❌ Invalid Admin Credentials!", "error")
    return render_template("admin_login.html")

@app.route("/admin-logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


# =============================================================================
# ADMIN DASHBOARD
# =============================================================================

@app.route("/admin-dashboard")
def admin_dashboard():
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))
    conn = get_db_connection(); cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) AS cnt FROM users")
    total_users = cursor.fetchone()["cnt"]
    cursor.execute("SELECT COUNT(*) AS cnt FROM predictions")
    total_preds = cursor.fetchone()["cnt"]
    cursor.execute("SELECT COUNT(*) AS cnt FROM contacts")
    total_contacts = cursor.fetchone()["cnt"]
    try:
        cursor.execute("SELECT COUNT(*) AS cnt FROM property_enquiries")
        total_enquiries = cursor.fetchone()["cnt"]
    except Exception:
        total_enquiries = 0
    cursor.execute("""
        SELECT p.prediction_id, u.name AS user_name, p.area, p.bedrooms,
               p.bathrooms, p.city, p.state, p.furnishing_status,
               p.guest_room, p.basement, p.air_conditioning,
               p.parking, p.predicted_price
        FROM predictions p JOIN users u ON p.user_id=u.user_id
        ORDER BY p.prediction_id DESC
    """)
    predictions = cursor.fetchall()
    cursor.execute("SELECT user_id, name, email FROM users ORDER BY user_id DESC")
    users = cursor.fetchall()
    cursor.execute("SELECT * FROM contacts ORDER BY contact_id DESC")
    contacts = cursor.fetchall()
    cursor.execute("SELECT * FROM about_sections ORDER BY sort_order ASC")
    about_sections = cursor.fetchall()
    try:
        cursor.execute("SELECT * FROM property_enquiries ORDER BY enquiry_id DESC")
        enquiries = cursor.fetchall()
    except Exception:
        enquiries = []
    cursor.close(); conn.close()
    return render_template("admin_dashboard.html",
        total_users=total_users, total_preds=total_preds,
        total_contacts=total_contacts, total_enquiries=total_enquiries,
        predictions=predictions, users=users,
        contacts=contacts, about_sections=about_sections, enquiries=enquiries)


# =============================================================================
# ADMIN – USERS CRUD
# =============================================================================

@app.route("/admin/user/add", methods=["POST"])
def admin_add_user():
    if "admin_id" not in session: return redirect(url_for("admin_login"))
    name = request.form["name"].strip()
    email = request.form.get("email", "").strip()
    password = request.form["password"]
    hashed = generate_password_hash(password)
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (name,email,password) VALUES (%s,%s,%s)", (name, email, hashed))
        conn.commit()
        flash(f"✅ User '{name}' added successfully.", "success")
    except Exception as e:
        err = str(e)
        if "Duplicate entry" in err and "users.name" in err:
            flash(f"❌ Username '{name}' already exists.", "error")
        elif "Duplicate entry" in err and "users.email" in err:
            flash(f"❌ Email '{email}' is already registered.", "error")
        else:
            flash(f"❌ Error adding user: {err}", "error")
    finally:
        cursor.close(); conn.close()
    return redirect(url_for("admin_dashboard") + "#users")

@app.route("/admin/user/edit/<int:user_id>", methods=["POST"])
def admin_edit_user(user_id):
    if "admin_id" not in session: return redirect(url_for("admin_login"))
    name = request.form["name"].strip()
    email = request.form.get("email", "").strip()
    new_password = request.form.get("new_password", "").strip()
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        if new_password:
            hashed = generate_password_hash(new_password)
            cursor.execute("UPDATE users SET name=%s,email=%s,password=%s WHERE user_id=%s",
                           (name, email, hashed, user_id))
        else:
            cursor.execute("UPDATE users SET name=%s,email=%s WHERE user_id=%s",
                           (name, email, user_id))
        conn.commit()
        flash("✅ User updated successfully.", "success")
    except Exception as e:
        flash(f"❌ Error updating user: {str(e)}", "error")
    finally:
        cursor.close(); conn.close()
    return redirect(url_for("admin_dashboard") + "#users")

@app.route("/admin/user/delete/<int:user_id>")
def admin_delete_user(user_id):
    if "admin_id" not in session: return redirect(url_for("admin_login"))
    conn = get_db_connection(); cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE user_id=%s", (user_id,))
    conn.commit(); cursor.close(); conn.close()
    flash("✅ User deleted.", "success")
    return redirect(url_for("admin_dashboard") + "#users")


# =============================================================================
# ADMIN – PREDICTIONS CRUD
# =============================================================================

@app.route("/admin/prediction/add", methods=["POST"])
def admin_add_prediction():
    if "admin_id" not in session: return redirect(url_for("admin_login"))
    try:
        user_id          = int(request.form["user_id"])
        area             = float(request.form["area"])
        bedrooms         = int(request.form["bedrooms"])
        bathrooms        = int(request.form["bathrooms"])
        parking          = int(request.form["parking"])
        guestroom        = request.form.get("guestroom", "no")
        basement         = request.form.get("basement", "no")
        airconditioning  = request.form.get("airconditioning", "no")
        furnishingstatus = request.form["furnishingstatus"]
        city             = request.form["city"]
        state            = request.form["state"]

        furnish_score = {"furnished": 200000, "semi-furnished": 100000, "unfurnished": 0}
        predicted_price = (
            area * 5000
            + bedrooms  * 100000
            + bathrooms * 50000
            + parking   * 75000
            + (150000 if guestroom       == "yes" else 0)
            + (100000 if basement        == "yes" else 0)
            + (120000 if airconditioning == "yes" else 0)
            + furnish_score.get(furnishingstatus, 0)
        )

        conn = get_db_connection(); cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO predictions
            (user_id, area, bedrooms, bathrooms, guest_room, basement,
             air_conditioning, parking, furnishing_status, city, state, predicted_price)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (user_id, area, bedrooms, bathrooms, guestroom, basement,
              airconditioning, parking, furnishingstatus, city, state,
              round(predicted_price, 2)))
        conn.commit(); cursor.close(); conn.close()
        flash(f"✅ Prediction added. Estimated price: ₹{predicted_price:,.0f}", "success")
    except Exception as e:
        traceback.print_exc()
        flash(f"❌ Error adding prediction: {str(e)}", "error")
    return redirect(url_for("admin_dashboard") + "#predictions")

@app.route("/admin/prediction/edit/<int:pid>", methods=["POST"])
def admin_edit_prediction(pid):
    if "admin_id" not in session: return redirect(url_for("admin_login"))
    try:
        area             = float(request.form["area"])
        bedrooms         = int(request.form["bedrooms"])
        bathrooms        = int(request.form["bathrooms"])
        parking          = int(request.form["parking"])
        guestroom        = request.form.get("guestroom", "no")
        basement         = request.form.get("basement", "no")
        airconditioning  = request.form.get("airconditioning", "no")
        furnishingstatus = request.form["furnishingstatus"]
        city             = request.form["city"]
        state            = request.form["state"]

        furnish_score = {"furnished": 200000, "semi-furnished": 100000, "unfurnished": 0}
        predicted_price = (
            area * 5000
            + bedrooms  * 100000
            + bathrooms * 50000
            + parking   * 75000
            + (150000 if guestroom       == "yes" else 0)
            + (100000 if basement        == "yes" else 0)
            + (120000 if airconditioning == "yes" else 0)
            + furnish_score.get(furnishingstatus, 0)
        )

        conn = get_db_connection(); cursor = conn.cursor()
        cursor.execute("""
            UPDATE predictions SET
                area=%s, bedrooms=%s, bathrooms=%s, parking=%s,
                guest_room=%s, basement=%s, air_conditioning=%s,
                furnishing_status=%s, city=%s, state=%s, predicted_price=%s
            WHERE prediction_id=%s
        """, (area, bedrooms, bathrooms, parking, guestroom, basement,
              airconditioning, furnishingstatus, city, state,
              round(predicted_price, 2), pid))
        conn.commit(); cursor.close(); conn.close()
        flash(f"✅ Prediction #{pid} updated. New price: ₹{predicted_price:,.0f}", "success")
    except Exception as e:
        traceback.print_exc()
        flash(f"❌ Error updating prediction: {str(e)}", "error")
    return redirect(url_for("admin_dashboard") + "#predictions")

@app.route("/admin/prediction/delete/<int:pid>")
def admin_delete_prediction(pid):
    if "admin_id" not in session: return redirect(url_for("admin_login"))
    conn = get_db_connection(); cursor = conn.cursor()
    cursor.execute("DELETE FROM predictions WHERE prediction_id=%s", (pid,))
    conn.commit(); cursor.close(); conn.close()
    flash("✅ Prediction deleted.", "success")
    return redirect(url_for("admin_dashboard") + "#predictions")


# =============================================================================
# ADMIN – CONTACTS CRUD
# =============================================================================

@app.route("/admin/contact/add", methods=["POST"])
def admin_add_contact():
    if "admin_id" not in session: return redirect(url_for("admin_login"))
    try:
        name    = request.form["name"].strip()
        email   = request.form["email"].strip()
        subject = request.form["subject"].strip()
        message = request.form["message"].strip()
        conn = get_db_connection(); cursor = conn.cursor()
        cursor.execute("INSERT INTO contacts (name,email,subject,message) VALUES (%s,%s,%s,%s)",
                       (name, email, subject, message))
        conn.commit(); cursor.close(); conn.close()
        flash(f"✅ Contact message from '{name}' added.", "success")
    except Exception as e:
        flash(f"❌ Error: {str(e)}", "error")
    return redirect(url_for("admin_dashboard") + "#contacts")

@app.route("/admin/contact/edit/<int:cid>", methods=["POST"])
def admin_edit_contact(cid):
    if "admin_id" not in session: return redirect(url_for("admin_login"))
    try:
        name    = request.form["name"].strip()
        email   = request.form["email"].strip()
        subject = request.form["subject"].strip()
        message = request.form["message"].strip()
        conn = get_db_connection(); cursor = conn.cursor()
        cursor.execute("""
            UPDATE contacts SET name=%s, email=%s, subject=%s, message=%s
            WHERE contact_id=%s
        """, (name, email, subject, message, cid))
        conn.commit(); cursor.close(); conn.close()
        flash("✅ Contact message updated.", "success")
    except Exception as e:
        flash(f"❌ Error updating contact: {str(e)}", "error")
    return redirect(url_for("admin_dashboard") + "#contacts")

@app.route("/admin/contact/delete/<int:cid>")
def admin_delete_contact(cid):
    if "admin_id" not in session: return redirect(url_for("admin_login"))
    conn = get_db_connection(); cursor = conn.cursor()
    cursor.execute("DELETE FROM contacts WHERE contact_id=%s", (cid,))
    conn.commit(); cursor.close(); conn.close()
    flash("✅ Contact deleted.", "success")
    return redirect(url_for("admin_dashboard") + "#contacts")


# =============================================================================
# ADMIN – ENQUIRIES CRUD
# =============================================================================

@app.route("/admin/enquiry/add", methods=["POST"])
def admin_add_enquiry():
    if "admin_id" not in session: return redirect(url_for("admin_login"))
    try:
        name          = request.form["name"].strip()
        email         = request.form["email"].strip()
        phone         = request.form["phone"].strip()
        property_type = request.form["property_type"].strip()
        city          = request.form["city"].strip()
        budget        = request.form["budget"].strip()
        bedrooms      = request.form.get("bedrooms", "").strip()
        message       = request.form.get("message", "").strip()
        conn = get_db_connection(); cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO property_enquiries
            (name, email, phone, property_type, city, budget, bedrooms, message)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (name, email, phone, property_type, city, budget, bedrooms, message))
        conn.commit(); cursor.close(); conn.close()
        flash(f"✅ Enquiry from '{name}' added successfully.", "success")
    except Exception as e:
        traceback.print_exc()
        flash(f"❌ Error adding enquiry: {str(e)}", "error")
    return redirect(url_for("admin_dashboard") + "#enquiries")

@app.route("/admin/enquiry/edit/<int:eid>", methods=["POST"])
def admin_edit_enquiry(eid):
    if "admin_id" not in session: return redirect(url_for("admin_login"))
    try:
        name          = request.form["name"].strip()
        email         = request.form["email"].strip()
        phone         = request.form["phone"].strip()
        property_type = request.form["property_type"].strip()
        city          = request.form["city"].strip()
        budget        = request.form["budget"].strip()
        bedrooms      = request.form.get("bedrooms", "").strip()
        message       = request.form.get("message", "").strip()
        conn = get_db_connection(); cursor = conn.cursor()
        cursor.execute("""
            UPDATE property_enquiries SET
                name=%s, email=%s, phone=%s, property_type=%s,
                city=%s, budget=%s, bedrooms=%s, message=%s
            WHERE enquiry_id=%s
        """, (name, email, phone, property_type, city, budget, bedrooms, message, eid))
        conn.commit(); cursor.close(); conn.close()
        flash("✅ Enquiry updated successfully.", "success")
    except Exception as e:
        traceback.print_exc()
        flash(f"❌ Error updating enquiry: {str(e)}", "error")
    return redirect(url_for("admin_dashboard") + "#enquiries")

@app.route("/admin/enquiry/delete/<int:eid>")
def admin_delete_enquiry(eid):
    if "admin_id" not in session: return redirect(url_for("admin_login"))
    conn = get_db_connection(); cursor = conn.cursor()
    cursor.execute("DELETE FROM property_enquiries WHERE enquiry_id=%s", (eid,))
    conn.commit(); cursor.close(); conn.close()
    flash("✅ Enquiry deleted.", "success")
    return redirect(url_for("admin_dashboard") + "#enquiries")


# =============================================================================
# ADMIN – ABOUT SECTIONS CRUD
# =============================================================================

@app.route("/admin/about/add", methods=["POST"])
def admin_about_add():
    if "admin_id" not in session: return redirect(url_for("admin_login"))
    title = request.form["title"].strip()
    body  = request.form["body"].strip()
    sort_order = int(request.form.get("sort_order", 0))
    image_path = ""
    file = request.files.get("image")
    if file and file.filename and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        image_path = "uploads/" + filename
    conn = get_db_connection(); cursor = conn.cursor()
    cursor.execute("INSERT INTO about_sections (title,body,image_path,sort_order) VALUES (%s,%s,%s,%s)",
                   (title, body, image_path, sort_order))
    conn.commit(); cursor.close(); conn.close()
    flash("✅ About section added.", "success")
    return redirect(url_for("admin_dashboard") + "#about")

@app.route("/admin/about/edit/<int:sid>", methods=["POST"])
def admin_about_edit(sid):
    if "admin_id" not in session: return redirect(url_for("admin_login"))
    title      = request.form["title"].strip()
    body       = request.form["body"].strip()
    sort_order = int(request.form.get("sort_order", 0))
    conn = get_db_connection(); cursor = conn.cursor()
    file = request.files.get("image")
    if file and file.filename and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        image_path = "uploads/" + filename
        cursor.execute("UPDATE about_sections SET title=%s,body=%s,image_path=%s,sort_order=%s WHERE section_id=%s",
                       (title, body, image_path, sort_order, sid))
    else:
        cursor.execute("UPDATE about_sections SET title=%s,body=%s,sort_order=%s WHERE section_id=%s",
                       (title, body, sort_order, sid))
    conn.commit(); cursor.close(); conn.close()
    flash("✅ About section updated.", "success")
    return redirect(url_for("admin_dashboard") + "#about")

@app.route("/admin/about/delete/<int:sid>")
def admin_about_delete(sid):
    if "admin_id" not in session: return redirect(url_for("admin_login"))
    conn = get_db_connection(); cursor = conn.cursor()
    cursor.execute("DELETE FROM about_sections WHERE section_id=%s", (sid,))
    conn.commit(); cursor.close(); conn.close()
    flash("✅ About section deleted.", "success")
    return redirect(url_for("admin_dashboard") + "#about")


# =============================================================================
# ERROR HANDLERS
# =============================================================================

# Replace your existing error handlers with these:
# Disable exception propagation so Flask uses custom error pages.
# In production, keep debug=False and let error handlers render the templates.
app.config['PROPAGATE_EXCEPTIONS'] = False

@app.errorhandler(403)
def forbidden(e):
    return render_template("403.html", error=str(e)), 403

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", error=str(e)), 404

@app.errorhandler(500)
@app.errorhandler(Exception) 
def handle_exception(e):
    traceback.print_exc()
    error_msg = str(e)
    return render_template("500.html", error=error_msg), 500



if __name__ == "__main__":
    app.run(debug=False) 