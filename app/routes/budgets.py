import re
import math
from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from app.database import get_db
from app.utils import login_required
from app.services.finance_service import (
    get_current_month,
    get_budget_status,
    get_categories
)

budgets_bp = Blueprint('budgets', __name__, url_prefix='/budgets')

def is_valid_month(month_str):
    """Validate YYYY-MM format."""
    return bool(re.match(r'^\d{4}-(0[1-9]|1[0-2])$', str(month_str)))

@budgets_bp.route('/', methods=['GET'])
@login_required
def index():
    user_id = g.current_user['id']
    selected_month = request.args.get('month', get_current_month()).strip()

    if not is_valid_month(selected_month):
        selected_month = get_current_month()

    # Budget status calculation (budget vs actual spending)
    budget_data = get_budget_status(user_id, selected_month)

    # Categories for setting new budgets (expense categories)
    expense_categories = get_categories(user_id, trans_type='expense')
    
    # Identify which categories already have a budget this month
    budgeted_cat_names = {b['category'] for b in budget_data['budgets']}
    available_categories = [c for c in expense_categories if c['name'] not in budgeted_cat_names]

    return render_template(
        'budgets/index.html',
        budget_data=budget_data,
        selected_month=selected_month,
        available_categories=available_categories,
        all_expense_categories=expense_categories
    )

@budgets_bp.route('/add', methods=['POST'])
@login_required
def add():
    user_id = g.current_user['id']
    category = request.form.get('category', '').strip()
    month = request.form.get('month', '').strip()
    amount_raw = request.form.get('amount', '').strip()

    errors = []
    if not category:
        errors.append("Category is required.")
    if not is_valid_month(month):
        errors.append("Invalid month format. Please select a valid month (YYYY-MM).")
    
    amount = 0.0
    try:
        amount = float(amount_raw)
        if not math.isfinite(amount) or amount <= 0:
            errors.append("Budget amount must be greater than 0.")
        if amount > 100_000_000:
            errors.append("Budget amount exceeds maximum limit.")
    except (ValueError, TypeError):
        errors.append("Please enter a valid numeric budget amount.")

    if not errors and round(amount, 2) <= 0:
        errors.append("Budget amount must be at least 0.01.")

    if errors:
        for err in errors:
            flash(err, "danger")
        return redirect(url_for('budgets.index', month=month or get_current_month()))

    db = get_db()
    # Check if budget already exists for this category and month
    existing = db.execute(
        "SELECT id FROM budgets WHERE user_id = ? AND category = ? AND month = ?",
        (user_id, category, month)
    ).fetchone()

    if existing:
        # Update existing budget
        db.execute(
            "UPDATE budgets SET amount = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?",
            (amount, existing['id'], user_id)
        )
        db.commit()
        flash(f"Updated budget for {category} to {g.current_user['currency']}{amount:,.2f}.", "success")
    else:
        # Insert new budget
        db.execute(
            """
            INSERT INTO budgets (user_id, category, month, amount)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, category, month, amount)
        )
        db.commit()
        flash(f"Budget for {category} set to {g.current_user['currency']}{amount:,.2f}.", "success")

    return redirect(url_for('budgets.index', month=month))

@budgets_bp.route('/edit/<int:budget_id>', methods=['POST'])
@login_required
def edit(budget_id):
    user_id = g.current_user['id']
    amount_raw = request.form.get('amount', '').strip()
    month = request.form.get('month', get_current_month()).strip()

    try:
        amount = float(amount_raw)
        if not math.isfinite(amount) or amount <= 0:
            flash("Budget amount must be greater than 0.", "danger")
            return redirect(url_for('budgets.index', month=month))
        if round(amount, 2) <= 0 or amount > 100_000_000:
            flash("Budget amount must be at least 0.01 and no more than 100,000,000.", "danger")
            return redirect(url_for('budgets.index', month=month))
    except (ValueError, TypeError):
        flash("Please enter a valid numeric amount.", "danger")
        return redirect(url_for('budgets.index', month=month))

    db = get_db()
    result = db.execute(
        """
        UPDATE budgets 
        SET amount = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND user_id = ?
        """,
        (amount, budget_id, user_id)
    )
    db.commit()

    if result.rowcount > 0:
        flash("Budget updated successfully.", "success")
    else:
        flash("Budget not found or access denied.", "danger")

    return redirect(url_for('budgets.index', month=month))

@budgets_bp.route('/delete/<int:budget_id>', methods=['POST'])
@login_required
def delete(budget_id):
    user_id = g.current_user['id']
    month = request.form.get('month', get_current_month()).strip()

    db = get_db()
    result = db.execute(
        "DELETE FROM budgets WHERE id = ? AND user_id = ?",
        (budget_id, user_id)
    )
    db.commit()

    if result.rowcount > 0:
        flash("Budget removed successfully.", "success")
    else:
        flash("Budget not found or access denied.", "danger")

    return redirect(url_for('budgets.index', month=month))

