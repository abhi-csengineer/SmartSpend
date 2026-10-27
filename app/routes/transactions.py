from datetime import datetime
import math
from flask import Blueprint, render_template, request, redirect, url_for, flash, g, Response, abort
from app.database import get_db
from app.utils import login_required
from app.services.finance_service import (
    get_filtered_transactions,
    get_categories,
    get_today_date
)
from app.services.export_service import generate_transactions_csv, get_export_filename

transactions_bp = Blueprint('transactions', __name__, url_prefix='/transactions')

def validate_transaction_data(form_data):
    """Validate and sanitize transaction inputs."""
    errors = []
    
    trans_type = form_data.get('type', '').strip().lower()
    if trans_type not in ('income', 'expense'):
        errors.append("Transaction type must be 'income' or 'expense'.")

    amount_raw = form_data.get('amount', '').strip()
    amount = 0.0
    try:
        amount = float(amount_raw)
        if not math.isfinite(amount) or amount <= 0:
            errors.append("Amount must be a positive number greater than 0.")
        if amount > 100_000_000:
            errors.append("Amount exceeds allowable transaction limit.")
    except (ValueError, TypeError):
        errors.append("Please enter a valid numeric amount.")

    if not errors and round(amount, 2) <= 0:
        errors.append("Amount must be at least 0.01.")

    category = form_data.get('category', '').strip()
    if not category:
        errors.append("Category is required.")

    trans_date = form_data.get('date', '').strip()
    if not trans_date:
        errors.append("Date is required.")
    else:
        try:
            parsed_date = datetime.strptime(trans_date, "%Y-%m-%d")
            if parsed_date.strftime('%Y-%m-%d') != trans_date:
                raise ValueError
        except ValueError:
            errors.append("Date must be in YYYY-MM-DD format.")

    description = form_data.get('description', '').strip()
    if len(description) > 255:
        errors.append("Description must be 255 characters or fewer.")

    return errors, {
        'type': trans_type,
        'amount': round(amount, 2),
        'category': category,
        'date': trans_date,
        'description': description
    }

@transactions_bp.route('/', methods=['GET'])
@login_required
def index():
    user_id = g.current_user['id']

    trans_type = request.args.get('type', 'all').strip()
    category = request.args.get('category', '').strip()
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()
    search = request.args.get('search', '').strip()

    # Normalize type filter
    filter_type = trans_type if trans_type in ('income', 'expense') else None

    # Fetch filtered transactions
    transactions = get_filtered_transactions(
        user_id=user_id,
        category=category or None,
        trans_type=filter_type,
        start_date=start_date or None,
        end_date=end_date or None,
        search=search or None
    )

    # Compute quick stats on filtered transactions
    filtered_income = sum(t['amount'] for t in transactions if t['type'] == 'income')
    filtered_expense = sum(t['amount'] for t in transactions if t['type'] == 'expense')
    filtered_net = filtered_income - filtered_expense

    # Categories for filter dropdown
    categories = get_categories(user_id)

    return render_template(
        'transactions/index.html',
        transactions=transactions,
        categories=categories,
        filters={
            'type': trans_type,
            'category': category,
            'start_date': start_date,
            'end_date': end_date,
            'search': search
        },
        stats={
            'count': len(transactions),
            'income': filtered_income,
            'expense': filtered_expense,
            'net': filtered_net
        },
        today_date=get_today_date()
    )

@transactions_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    user_id = g.current_user['id']

    if request.method == 'POST':
        errors, data = validate_transaction_data(request.form)

        if errors:
            for err in errors:
                flash(err, "danger")
            categories = get_categories(user_id)
            return render_template(
                'transactions/add_edit.html',
                is_edit=False,
                categories=categories,
                form_data=request.form,
                today_date=get_today_date()
            ), 400

        db = get_db()
        db.execute(
            """
            INSERT INTO transactions (user_id, type, category, amount, date, description)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, data['type'], data['category'], data['amount'], data['date'], data['description'])
        )
        db.commit()

        flash(f"Successfully recorded {data['type']} of {g.current_user['currency']}{data['amount']:,.2f}.", "success")
        return redirect(url_for('transactions.index'))

    categories = get_categories(user_id)
    return render_template(
        'transactions/add_edit.html',
        is_edit=False,
        categories=categories,
        form_data={'type': 'expense', 'date': get_today_date()},
        today_date=get_today_date()
    )

@transactions_bp.route('/edit/<int:transaction_id>', methods=['GET', 'POST'])
@login_required
def edit(transaction_id):
    user_id = g.current_user['id']
    db = get_db()

    # Security: Verify ownership
    tx = db.execute(
        "SELECT * FROM transactions WHERE id = ? AND user_id = ?",
        (transaction_id, user_id)
    ).fetchone()

    if not tx:
        flash("Transaction not found or access denied.", "danger")
        return redirect(url_for('transactions.index'))

    if request.method == 'POST':
        errors, data = validate_transaction_data(request.form)

        if errors:
            for err in errors:
                flash(err, "danger")
            categories = get_categories(user_id)
            return render_template(
                'transactions/add_edit.html',
                is_edit=True,
                transaction_id=transaction_id,
                categories=categories,
                form_data=request.form,
                today_date=get_today_date()
            ), 400

        db.execute(
            """
            UPDATE transactions 
            SET type = ?, category = ?, amount = ?, date = ?, description = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND user_id = ?
            """,
            (data['type'], data['category'], data['amount'], data['date'], data['description'], transaction_id, user_id)
        )
        db.commit()

        flash("Transaction updated successfully.", "success")
        return redirect(url_for('transactions.index'))

    categories = get_categories(user_id)
    return render_template(
        'transactions/add_edit.html',
        is_edit=True,
        transaction_id=transaction_id,
        categories=categories,
        form_data=dict(tx),
        today_date=get_today_date()
    )

@transactions_bp.route('/delete/<int:transaction_id>', methods=['POST'])
@login_required
def delete(transaction_id):
    user_id = g.current_user['id']
    db = get_db()

    # Parameterized delete with explicit user_id ownership check
    result = db.execute(
        "DELETE FROM transactions WHERE id = ? AND user_id = ?",
        (transaction_id, user_id)
    )
    db.commit()

    if result.rowcount > 0:
        flash("Transaction deleted successfully.", "success")
    else:
        flash("Transaction not found or could not be deleted.", "danger")

    # Redirect back to where the user came from or transactions index
    referer = request.referrer
    if referer and (url_for('transactions.index') in referer or url_for('dashboard.index') in referer):
        return redirect(referer)
    return redirect(url_for('transactions.index'))

@transactions_bp.route('/export', methods=['GET'])
@login_required
def export_csv():
    user_id = g.current_user['id']

    trans_type = request.args.get('type', 'all').strip()
    category = request.args.get('category', '').strip()
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()
    search = request.args.get('search', '').strip()

    filter_type = trans_type if trans_type in ('income', 'expense') else None

    transactions = get_filtered_transactions(
        user_id=user_id,
        category=category or None,
        trans_type=filter_type,
        start_date=start_date or None,
        end_date=end_date or None,
        search=search or None
    )

    csv_data = generate_transactions_csv(transactions, currency=g.current_user.get('currency', '$'))
    filename = get_export_filename(prefix="transactions")

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Cache-Control": "no-cache, no-store, must-revalidate"
        }
    )

