# SmartSpend — Personal Finance & Expense Tracker

> **A Complete Full-Stack Python & Flask Web Application**  
> Designed, built, and optimized for B.Tech Computer Science College Project & Viva Demonstration.

---

## 1. Project Overview

**SmartSpend** is a full-featured, secure, and intuitive personal finance management web application. It empowers users to track their daily incomes and expenditures, categorize financial movements, configure monthly category budgets with automated warning thresholds, visualize spending patterns via interactive Chart.js visualizations, and export filtered financial statements to CSV.

### Key Highlights
- **100% Offline Capable**: Bundled JavaScript assets (`Chart.js`) — renders charts and features seamlessly during in-person viva demonstrations without requiring internet connectivity.
- **Enterprise-Grade Security Architecture**: Password hashing with Werkzeug, parameterized SQL queries against SQL injection, strict user-data isolation, and custom session-based CSRF protection.
- **Dynamic Multi-Currency Support**: Switch between Indian Rupee (`₹`), US Dollar (`$`), Euro (`€`), British Pound (`£`), Japanese Yen (`¥`), and others with a single click in account settings.
- **Automated Demo Seeder**: Includes a one-command data seeding utility (`python seed_demo.py`) that instantly generates a 3-month portfolio for demonstration.

---

## 2. Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Backend** | Python 3.10+ / Flask 3.x | Lightweight, modular WSGI application server |
| **Database** | SQLite 3 | Zero-configuration, persistent relational storage with foreign keys |
| **Frontend UI** | HTML5, Modern CSS3, Vanilla JS | Lightweight, responsive design system without bulky external frameworks |
| **Visualizations** | Chart.js 4.4.x (Local UMD bundle) | Doughnut, Bar, and Line charts for financial trend analysis |
| **Security** | Werkzeug Security & Secrets | Cryptographic password hashing (`scrypt`/`pbkdf2`) and CSRF tokens |
| **Testing** | pytest | Automated test suite covering auth, CRUD, isolation, and exports |
| **Version Control**| Git | Clean version-controlled repository structure |

---

## 3. Core Features

### A. Authentication & User Management
- Secure user registration, credential validation, login, and logout.
- Password hashing using industry-standard Werkzeug cryptographic algorithms.
- Protected routes guarded by `@login_required` decorators.
- Complete data isolation: Users can only view and manage their own financial data.
- Profile settings allowing full name updates, password changes, and currency preferences.

### B. Interactive Financial Dashboard
- **Lifetime Financial KPIs**: Total Balance, Total Income, and Total Expenses.
- **Monthly Summary Cards**: Current month income, expenses, and net savings rate percentage.
- **Visual Cashflow Charts**: 6-month comparative income vs. expense bar chart.
- **Category Doughnut Chart**: Interactive breakdown of expenditures by category.
- **Budget Health Gauges**: Visual progress bars and warning indicators for current month budgets.
- **Recent Activity Table**: Real-time listing of latest transactions with quick actions.
- **Modal Quick-Add**: Add transactions directly from the dashboard.

### C. Transaction Management
- Comprehensive income and expense tracking.
- Fields: Amount, Transaction Type (`income`/`expense`), Category, Date (`YYYY-MM-DD`), and Description.
- Input validation ensuring positive numbers, valid ISO dates, and sanitized strings.
- Dynamic filtering by **Transaction Type**, **Category**, and **Date Range**.
- Full-text search across descriptions and categories.
- Transaction modification (Edit) and deletion with confirmation dialogs.
- Instant filtered CSV export.

### D. Budget Management & Utilization Alerts
- Set monthly spending ceilings per expense category for any selected month (`YYYY-MM`).
- Real-time comparison between budgeted amount and actual transactions.
- Automated 3-stage status indicators:
  - 🟢 **On Track**: Spending is below 80% of budget.
  - 🟡 **Near Limit Warning**: Spending has reached 80% to 99.9% of budget.
  - 🔴 **Over Budget Alert**: Spending has equaled or exceeded 100% of budget limit.
- Edit and delete budgets safely with database ownership verification.

### E. Financial Reports & CSV Export
- View analytical reports for **3 months**, **6 months**, or **12 months**.
- Net Monthly Savings line chart showing month-over-month financial progress.
- Spending share table with percentage allocations and transaction counts.
- RFC 4180 compliant CSV export with timestamped filenames (`smartspend_transactions_YYYYMMDD_HHMMSS.csv`).

---

## 4. Project Directory Structure

```text
D:\Projects\SmartSpend\
│
├── app.py                      # Main application entry point
├── config.py                   # Environment configuration classes
├── requirements.txt            # Python dependencies (Flask, pytest)
├── seed_demo.py                # One-click demo data population script
├── verify_app.py               # End-to-end integration verification script
├── README.md                   # Complete documentation & viva defense guide
├── .gitignore                  # Git ignore rules for databases, cache, and venvs
├── .env.example                # Template for environment variables
│
├── instance/                   # Local instance directory (auto-created)
│   └── smartspend.db           # SQLite database file (ignored by Git)
│
├── app/                        # Application package
│   ├── __init__.py             # Flask Application Factory (create_app)
│   ├── database.py             # SQLite schema, connection lifecycle, and init
│   ├── utils.py                # Auth decorators, CSRF validator, Jinja filters
│   │
│   ├── routes/                 # Blueprint route controllers
│   │   ├── __init__.py
│   │   ├── auth.py             # Register, Login, Logout, Profile settings
│   │   ├── dashboard.py        # Dashboard KPIs and chart data
│   │   ├── transactions.py     # Transaction CRUD, filtering, CSV export
│   │   ├── budgets.py          # Budget CRUD, progress tracking, status alerts
│   │   └── reports.py          # Long-term analytics, trend charts
│   │
│   ├── services/               # Business logic & database query services
│   │   ├── __init__.py
│   │   ├── finance_service.py  # Aggregations, metrics, budget calculations
│   │   └── export_service.py   # In-memory CSV generation
│   │
│   ├── templates/              # Jinja2 HTML templates
│   │   ├── base.html           # Master layout with responsive navbar & icons
│   │   ├── auth/               # Login, Register, Profile templates
│   │   ├── dashboard/          # Dashboard template with Chart.js canvas
│   │   ├── transactions/       # Transaction list and add/edit forms
│   │   ├── budgets/            # Budget monitoring and management
│   │   ├── reports/            # Reports & analytics page
│   │   └── errors/             # Custom 400, 404, 500 error pages
│   │
│   └── static/                 # Static assets
│       ├── css/
│       │   └── style.css       # Unified modern financial design system
│       └── js/
│           ├── chart.umd.min.js# Offline bundled Chart.js 4.4.x library
│           ├── charts.js       # Chart initialization helpers
│           └── main.js         # Modal controllers, alert dismissals, dynamic forms
│
└── tests/                      # Automated test suite (pytest)
    ├── __init__.py
    ├── conftest.py             # Pytest fixtures and test client setup
    ├── test_auth.py            # Authentication & access control tests
    ├── test_transactions.py    # Transaction CRUD & user isolation tests
    ├── test_budgets.py         # Budget calculation & alert tests
    ├── test_dashboard_and_reports.py # Calculation & CSV export tests
    └── test_security_and_profile.py  # Password change, currency, validation tests
```

---

## 5. Getting Started (Windows Setup Guide)

### Prerequisites
- **Python 3.10 or higher** installed. (Check with `python --version` in PowerShell).
- **Git** installed.

### Step 1: Open Windows PowerShell
Navigate to the project directory:
```powershell
cd D:\Projects\SmartSpend
```

### Step 2: Create and Activate a Virtual Environment
```powershell
# Create virtual environment named 'venv'
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\Activate.ps1
```
*(If PowerShell blocks execution of scripts, run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` and retry activation).*

### Step 3: Install Required Dependencies
```powershell
python -m pip install -r requirements.txt
```

### Step 4: Initialize the SQLite Database
```powershell
flask --app app init-db
```
*Output: `SmartSpend database initialized successfully.`*

### Step 5 (Recommended): Seed Demo Data for Viva
To immediately demonstrate the site with a full 3-month portfolio:
```powershell
python seed_demo.py
```
This creates an account ready for immediate demonstration. The username is `demo_student`; the script generates and prints a fresh password each time it runs. Keep that password locally and do not commit it.

### Step 6: Start the Flask Development Server
```powershell
python app.py
```
Or via Flask CLI:
```powershell
flask --app app run --port 5000 --debug
```

### Step 7: Open the Website in Your Browser
Open your browser and navigate to:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 6. Running Automated Tests

The application includes 33 automated unit and integration tests using `pytest`:

```powershell
# Run all tests with verbose output
python -m pytest -v

# Run tests with summary report
python -m pytest
```

### Running the Demo Verification Script

After running `python seed_demo.py`, copy the generated password from its output into the current PowerShell session, then run the verification script:

```powershell
$env:SMARTSPEND_DEMO_PASSWORD = "paste-the-generated-password-here"
python verify_app.py
Remove-Item Env:SMARTSPEND_DEMO_PASSWORD
```

### Verified Test Areas:
1. **User Registration & Validation**: Valid inputs, duplicate username checks, duplicate email checks, password mismatch verification.
2. **Authentication Flow**: Credential checks, password hashing verification, session handling, POST-only logout, CSRF enforcement, and rejection of external login redirects.
3. **Route Security**: Unauthenticated access to protected pages (`/`, `/transactions`, `/budgets`, `/reports`) redirects to `/auth/login`.
4. **Data Isolation (Crucial Security Check)**: Verified that User B cannot view, edit, or delete User A's transactions or budgets.
5. **Transaction Management**: Add income, add expense, invalid amount rejection (including non-finite and sub-cent amounts), edit, delete, and full filtering.
6. **Budget Management**: Calculation of spent amounts, remaining amounts, % utilization, Near Limit alerts (>=80%), and Over Budget alerts (>=100%).
7. **CSV Export**: Verified HTTP header `Content-Disposition`, MIME type `text/csv`, and RFC 4180 format.
8. **Error Handling**: Custom 400 and 404 error page responses.

---

## 7. Viva Defense & Python Concepts Guide

When defending this project in your college viva examination, use the following explanations:

### 1. Flask Application Factory Pattern (`create_app`)
- **What it is**: In [`app/__init__.py`](app/__init__.py), the `create_app(config_name)` function builds and configures the Flask instance dynamically.
- **Why we used it**: Decouples application configuration for different environments (`development`, `testing`, `production`). In testing, `TestingConfig` uses an isolated database and disables CSRF, allowing clean automated tests without affecting development data.

### 2. Relational Database Design & Foreign Keys (SQLite)
- **Tables**: `users`, `categories`, `transactions`, `budgets`.
- **Foreign Keys**: `FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE`.
- **Why `PRAGMA foreign_keys = ON;`**: By default, SQLite has foreign key constraints disabled for backwards compatibility. We explicitly enable it on every connection so that deleting a user safely cascades to delete their associated transactions and budgets.

### 3. Protection Against SQL Injection
- **Technique**: Parameterized SQL queries using placeholder `?` tuples.
- **Viva explanation**: *"We never concatenate user inputs directly into SQL strings. When executing `db.execute("SELECT * FROM transactions WHERE user_id = ? AND category = ?", (user_id, category))`, the database driver treats the parameters strictly as data literals, rendering SQL injection impossible."*

### 4. Password Security & Hashing
- **Algorithms**: `werkzeug.security.generate_password_hash` using salted hashes (scrypt / PBKDF2).
- **Viva explanation**: *"Plaintext passwords are never stored in the database. Even if an attacker obtains a database dump, they cannot reverse the password hash. During login, `check_password_hash(stored_hash, candidate_password)` hashes the candidate password with the original salt and compares the hashes in constant time."*

### 5. Session Management & Access Control
- **Mechanism**: Flask signed cookie sessions with `HttpOnly` and `SameSite=Lax`.
- **Decorator**: `@login_required` wraps protected route handlers. It inspects `session.get('user_id')`. If absent, it flashes an alert and redirects to the login screen with a `next` redirect query parameter.

### 6. CSRF (Cross-Site Request Forgery) Protection
- **Mechanism**: A cryptographically random token (`secrets.token_hex(32)`) is stored in the user's session and embedded into every HTML `<form>` via `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">`.
- **Validation**: On every state-changing request (`POST`), the `before_request` hook validates that the form's token matches the session token using `secrets.compare_digest`. External malicious sites cannot forge requests because they cannot access the user's session token.

### 7. Multi-Tenant User Isolation
- Every SELECT, UPDATE, and DELETE query incorporates an explicit `WHERE user_id = ?` clause derived strictly from the server-side `session['user_id']`, not from client-supplied form parameters.

---

## 8. Security & Production Deployment Considerations

1. **Secret Key**: In production, set the `SECRET_KEY` environment variable to a secure random string (e.g. `python -c "import secrets; print(secrets.token_hex(32))"`). Never commit production secret keys to version control.
2. **WSGI Server**: Flask's built-in server is designed for development and demonstration. For a high-traffic production deployment, deploy behind a production WSGI server such as **Gunicorn** or **Waitress** with **Nginx** reverse proxy and HTTPS/TLS encryption enabled.
3. **Database Scalability**: SQLite is optimal for single-server, embedded, and college project deployments. For multi-server concurrent deployments, the modular service layer can seamlessly transition to PostgreSQL or MySQL by swapping the connection layer.

---

## 9. License & Project Ownership

This project is developed independently by a B.Tech Computer Science student for academic project submission and software engineering viva evaluation.

