import functools
import secrets
from datetime import datetime
from flask import session, request, abort, redirect, url_for, flash, g
from app.database import get_db

def generate_csrf_token():
    """Generate or retrieve unique CSRF token stored in user session."""
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)
    return session['csrf_token']

def validate_csrf():
    """Verify CSRF token for state-changing requests."""
    # Allow safe read-only methods
    if request.method in ('GET', 'HEAD', 'OPTIONS'):
        return

    # Check for CSRF token in form data or headers
    token = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token')
    session_token = session.get('csrf_token')

    if not session_token or not token or not secrets.compare_digest(token, session_token):
        abort(400, description="Invalid or missing CSRF token. Please refresh the page and try again.")

def login_required(view):
    """Decorator to require login for protected routes."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('auth.login', next=request.path))
        return view(**kwargs)
    return wrapped_view

def load_logged_in_user():
    """Before-request hook to populate g.current_user."""
    user_id = session.get('user_id')
    if user_id is None:
        g.current_user = None
    else:
        db = get_db()
        user = db.execute(
            "SELECT id, username, email, full_name, currency, created_at FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
        if user is None:
            # Session exists for deleted user
            session.clear()
            g.current_user = None
        else:
            g.current_user = dict(user)

def format_currency(value, currency=None):
    """Format numeric value as localized currency."""
    if value is None:
        value = 0.0
    try:
        val = float(value)
    except (ValueError, TypeError):
        val = 0.0
    
    if currency is None:
        if hasattr(g, 'current_user') and g.current_user:
            currency = g.current_user.get('currency', '$')
        else:
            currency = '$'
            
    is_negative = val < 0
    abs_val = abs(val)
    formatted = f"{currency}{abs_val:,.2f}"
    return f"-{formatted}" if is_negative else formatted

def format_date(date_str):
    """Format YYYY-MM-DD to readable 'MMM DD, YYYY'."""
    if not date_str:
        return ""
    try:
        dt = datetime.strptime(str(date_str)[:10], "%Y-%m-%d")
        return dt.strftime("%b %d, %Y")
    except ValueError:
        return str(date_str)

def format_month(month_str):
    """Format YYYY-MM to readable 'Month Year' (e.g. October 2026)."""
    if not month_str:
        return ""
    try:
        dt = datetime.strptime(str(month_str)[:7], "%Y-%m")
        return dt.strftime("%B %Y")
    except ValueError:
        return str(month_str)

