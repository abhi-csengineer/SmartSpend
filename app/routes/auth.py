import re
from urllib.parse import urlsplit
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import get_db
from app.utils import login_required

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def is_valid_email(email):
    """Validate email pattern."""
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route."""
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        username = request.form.get('username', '').strip().lower()
        email = request.form.get('email', '').strip().lower()
        currency = request.form.get('currency', '$').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Input validation
        errors = []
        if not full_name:
            errors.append("Full name is required.")
        if not username or len(username) < 3 or len(username) > 30:
            errors.append("Username must be between 3 and 30 characters.")
        elif not re.match(r'^[a-zA-Z0-9_.-]+$', username):
            errors.append("Username may only contain letters, numbers, dots, and underscores.")
        if not email or not is_valid_email(email):
            errors.append("A valid email address is required.")
        if not password or len(password) < 6:
            errors.append("Password must be at least 6 characters long.")
        if password != confirm_password:
            errors.append("Passwords do not match.")

        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template(
                'auth/register.html',
                full_name=full_name,
                username=username,
                email=email,
                currency=currency
            )

        db = get_db()
        # Check for existing username or email
        existing_user = db.execute(
            "SELECT id, username, email FROM users WHERE username = ? OR email = ?",
            (username, email)
        ).fetchone()

        if existing_user:
            if existing_user['username'].lower() == username:
                flash("Username is already taken. Please choose another.", "danger")
            else:
                flash("Email is already registered. Please log in or use another email.", "danger")
            return render_template(
                'auth/register.html',
                full_name=full_name,
                username=username,
                email=email,
                currency=currency
            )

        # Hash password securely
        password_hash = generate_password_hash(password)
        cursor = db.execute(
            """
            INSERT INTO users (username, email, password_hash, full_name, currency)
            VALUES (?, ?, ?, ?, ?)
            """,
            (username, email, password_hash, full_name, currency or '$')
        )
        db.commit()

        new_user_id = cursor.lastrowid
        # Automatically log user into session
        session.clear()
        session['user_id'] = new_user_id
        session['username'] = username

        flash(f"Welcome to SmartSpend, {full_name}! Your account has been created successfully.", "success")
        return redirect(url_for('dashboard.index'))

    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login route."""
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    next_url = request.args.get('next', '')

    if request.method == 'POST':
        login_input = request.form.get('login_input', '').strip().lower()
        password = request.form.get('password', '')

        if not login_input or not password:
            flash("Please provide both username/email and password.", "danger")
            return render_template('auth/login.html', login_input=login_input, next=next_url)

        db = get_db()
        user = db.execute(
            "SELECT id, username, email, password_hash, full_name FROM users WHERE username = ? OR email = ?",
            (login_input, login_input)
        ).fetchone()

        if user is None or not check_password_hash(user['password_hash'], password):
            flash("Invalid username/email or password.", "danger")
            return render_template('auth/login.html', login_input=login_input, next=next_url)

        # Successful login
        session.clear()
        session['user_id'] = user['id']
        session['username'] = user['username']

        flash(f"Welcome back, {user['full_name']}!", "success")
        
        # Prevent open redirect vulnerabilities
        # Only allow a local absolute path; values such as //evil.example are
        # network-path URLs and would otherwise redirect away from this site.
        if next_url and next_url.startswith('/') and not next_url.startswith('//') and not urlsplit(next_url).netloc:
            return redirect(next_url)
        return redirect(url_for('dashboard.index'))

    return render_template('auth/login.html', next=next_url)

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Clear session and log user out."""
    session.clear()
    flash("You have been securely logged out.", "info")
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile and account settings route."""
    db = get_db()
    user_id = g.current_user['id']

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_profile':
            full_name = request.form.get('full_name', '').strip()
            currency = request.form.get('currency', '$').strip()

            if not full_name:
                flash("Full name cannot be empty.", "danger")
            else:
                db.execute(
                    "UPDATE users SET full_name = ?, currency = ? WHERE id = ?",
                    (full_name, currency, user_id)
                )
                db.commit()
                flash("Profile details updated successfully.", "success")
                return redirect(url_for('auth.profile'))

        elif action == 'change_password':
            current_password = request.form.get('current_password', '')
            new_password = request.form.get('new_password', '')
            confirm_new_password = request.form.get('confirm_new_password', '')

            # Verify current password
            user_row = db.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,)).fetchone()
            if not check_password_hash(user_row['password_hash'], current_password):
                flash("Current password is incorrect.", "danger")
            elif len(new_password) < 6:
                flash("New password must be at least 6 characters.", "danger")
            elif new_password != confirm_new_password:
                flash("New passwords do not match.", "danger")
            else:
                new_hash = generate_password_hash(new_password)
                db.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user_id))
                db.commit()
                flash("Password changed successfully.", "success")
                return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html')

