# Jyesta Corporate Entity – House Price Prediction

# House Price Prediction System

A machine learning based web application built using Flask and MySQL that predicts house prices based on user inputs such as area, bedrooms, furnishing status, and location.

## Tech Stack
- Python
- Flask
- MySQL
- Scikit-learn
- HTML/CSS
- JavaScript


## Setup Instructions

### 1. Install Python dependencies
```
pip install -r requirements.txt
```

### 2. Setup MySQL Database
- Open MySQL and run the `House.sql` file:
```
mysql -u root -p < House.sql
```
- Or paste the contents of `House.sql` into MySQL Workbench and run it.

### 3. Update Database Password
- Open `config.py`
- Change the `password` field to your MySQL root password

### 4. Run the App
```
python app.py
```
- Open browser at: http://127.0.0.1:5000

---

## What's New (Upgraded Version)

### ✅ Bug Fixes
- Fixed chatbot route causing 405 error on GET requests
- Fixed nav showing wrong Login/Logout based on session state
- Fixed `about` page crash when table is empty (try/except added)
- Added `@login_required` and `@admin_required` decorators — no repeated if-checks
- Shared `calculate_price()` function used everywhere (no duplicate code)

### 🆕 New Pages
- **404 Page** – Custom "Page Not Found" with friendly design
- **500 Page** – Custom "Server Error" page
- **403 Page** – Custom "Forbidden" page
- **Profile Page** (`/profile`) – Users can update name, email, password
- **Compare Page** (`/compare`) – Side-by-side comparison of two predictions

### 🆕 New Features
- **Admin: Export CSV** – Download all predictions or users as CSV
- **Timestamps** – Predictions now show date created in dashboard & admin
- **Smart Nav** – Login/Dashboard/Logout shown based on login state
- **CTA Buttons** – Home page has "Predict" and "Register/Dashboard" buttons

### 👥 Person 1 (Frontend)
- 404, 500, 403 error pages
- Profile page
- Compare predictions page
- Home page CTA buttons
- Smart navigation

### 👥 Person 2 (Backend)
- `@login_required` / `@admin_required` decorators
- Shared `calculate_price()` function
- Admin CSV export routes
- `created_at` timestamps in all tables
- Chatbot GET route fix
- Updated `House.sql` with all tables and email column
