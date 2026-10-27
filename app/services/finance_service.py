from datetime import datetime, date
from app.database import get_db

def get_current_month():
    """Return current month in YYYY-MM format."""
    return datetime.now().strftime("%Y-%m")

def get_today_date():
    """Return today's date in YYYY-MM-DD format."""
    return date.today().isoformat()

def get_financial_summary(user_id, month=None):
    """
    Calculate lifetime and current month totals:
    - Total balance, total income, total expense
    - Selected month income, expense, net savings, savings rate %
    """
    db = get_db()
    if month is None:
        month = get_current_month()

    # Lifetime totals
    totals = db.execute(
        """
        SELECT 
            COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) AS total_income,
            COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) AS total_expense
        FROM transactions
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()

    total_income = float(totals['total_income']) if totals else 0.0
    total_expense = float(totals['total_expense']) if totals else 0.0
    current_balance = total_income - total_expense

    # Monthly totals for selected month (YYYY-MM)
    monthly = db.execute(
        """
        SELECT 
            COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) AS month_income,
            COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) AS month_expense
        FROM transactions
        WHERE user_id = ? AND strftime('%Y-%m', date) = ?
        """,
        (user_id, month)
    ).fetchone()

    month_income = float(monthly['month_income']) if monthly else 0.0
    month_expense = float(monthly['month_expense']) if monthly else 0.0
    month_savings = month_income - month_expense
    savings_rate = (month_savings / month_income * 100.0) if month_income > 0 else 0.0

    return {
        'total_income': total_income,
        'total_expense': total_expense,
        'current_balance': current_balance,
        'month_income': month_income,
        'month_expense': month_expense,
        'month_savings': month_savings,
        'savings_rate': round(savings_rate, 1),
        'month': month
    }

def get_recent_transactions(user_id, limit=6):
    """Fetch the most recent transactions for the user."""
    db = get_db()
    rows = db.execute(
        """
        SELECT id, type, category, amount, date, description, created_at
        FROM transactions
        WHERE user_id = ?
        ORDER BY date DESC, id DESC
        LIMIT ?
        """,
        (user_id, limit)
    ).fetchall()
    return [dict(row) for row in rows]

def get_filtered_transactions(user_id, category=None, trans_type=None, start_date=None, end_date=None, search=None):
    """
    Fetch filtered transactions for transaction management and export.
    Uses parameterized SQL to guarantee security.
    """
    db = get_db()
    query = """
        SELECT id, type, category, amount, date, description, created_at
        FROM transactions
        WHERE user_id = ?
    """
    params = [user_id]

    if trans_type and trans_type.lower() in ('income', 'expense'):
        query += " AND type = ?"
        params.append(trans_type.lower())

    if category and category.strip():
        query += " AND category = ?"
        params.append(category.strip())

    if start_date and start_date.strip():
        query += " AND date >= ?"
        params.append(start_date.strip())

    if end_date and end_date.strip():
        query += " AND date <= ?"
        params.append(end_date.strip())

    if search and search.strip():
        query += " AND (description LIKE ? OR category LIKE ?)"
        like_term = f"%{search.strip()}%"
        params.extend([like_term, like_term])

    query += " ORDER BY date DESC, id DESC"

    rows = db.execute(query, tuple(params)).fetchall()
    return [dict(row) for row in rows]

def get_category_breakdown(user_id, month=None, trans_type='expense'):
    """
    Aggregate spending/income by category for charts and reports.
    """
    db = get_db()
    params = [user_id, trans_type]
    month_clause = ""
    if month and month.strip():
        month_clause = " AND strftime('%Y-%m', date) = ?"
        params.append(month.strip())

    query = f"""
        SELECT 
            category,
            SUM(amount) AS total_amount,
            COUNT(id) AS transaction_count
        FROM transactions
        WHERE user_id = ? AND type = ?{month_clause}
        GROUP BY category
        ORDER BY total_amount DESC
    """
    rows = db.execute(query, tuple(params)).fetchall()
    
    total_sum = sum(row['total_amount'] for row in rows) if rows else 0.0

    breakdown = []
    for row in rows:
        pct = (row['total_amount'] / total_sum * 100.0) if total_sum > 0 else 0.0
        breakdown.append({
            'category': row['category'],
            'total_amount': float(row['total_amount']),
            'count': row['transaction_count'],
            'percentage': round(pct, 1)
        })
    return breakdown, total_sum

def get_monthly_trend(user_id, num_months=6):
    """
    Return last N months income and expense data for charts.
    """
    db = get_db()
    # Find all monthly aggregates for user
    rows = db.execute(
        """
        SELECT 
            strftime('%Y-%m', date) AS month,
            SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) AS income,
            SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) AS expense
        FROM transactions
        WHERE user_id = ?
        GROUP BY strftime('%Y-%m', date)
        ORDER BY month DESC
        LIMIT ?
        """,
        (user_id, num_months)
    ).fetchall()

    # Reverse so months are in chronological order
    trend_rows = list(reversed(rows))
    
    # If no data or fewer than 6, create a continuous range of last N months
    from datetime import datetime
    today = datetime.now()
    
    # Generate list of past num_months YYYY-MM
    months_list = []
    year = today.year
    month = today.month
    for _ in range(num_months):
        months_list.append(f"{year:04d}-{month:02d}")
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    months_list.reverse()

    data_map = {row['month']: {'income': float(row['income']), 'expense': float(row['expense'])} for row in trend_rows}

    labels = []
    income_data = []
    expense_data = []

    for m in months_list:
        try:
            dt = datetime.strptime(m, "%Y-%m")
            label = dt.strftime("%b %Y")
        except ValueError:
            label = m
        labels.append(label)
        entry = data_map.get(m, {'income': 0.0, 'expense': 0.0})
        income_data.append(entry['income'])
        expense_data.append(entry['expense'])

    return {
        'months': months_list,
        'labels': labels,
        'income': income_data,
        'expense': expense_data
    }

def get_budget_status(user_id, month=None):
    """
    Calculate budget utilization and warning statuses for a given month.
    """
    if month is None:
        month = get_current_month()
        
    db = get_db()
    
    # Fetch all budgets set by user for this month
    budgets = db.execute(
        """
        SELECT id, category, month, amount
        FROM budgets
        WHERE user_id = ? AND month = ?
        ORDER BY amount DESC
        """,
        (user_id, month)
    ).fetchall()

    # Fetch actual spending for this month grouped by category
    spending_rows = db.execute(
        """
        SELECT category, SUM(amount) AS total_spent
        FROM transactions
        WHERE user_id = ? AND type = 'expense' AND strftime('%Y-%m', date) = ?
        GROUP BY category
        """,
        (user_id, month)
    ).fetchall()
    
    spent_map = {row['category']: float(row['total_spent']) for row in spending_rows}

    budget_list = []
    total_budgeted = 0.0
    total_spent = 0.0

    for b in budgets:
        cat = b['category']
        b_amount = float(b['amount'])
        spent = spent_map.get(cat, 0.0)
        remaining = b_amount - spent
        pct = (spent / b_amount * 100.0) if b_amount > 0 else 0.0

        if pct >= 100.0:
            status = 'danger'      # Over budget
            status_text = 'Over Budget'
        elif pct >= 80.0:
            status = 'warning'     # Near limit
            status_text = 'Near Limit'
        else:
            status = 'normal'      # Good
            status_text = 'On Track'

        budget_list.append({
            'id': b['id'],
            'category': cat,
            'month': b['month'],
            'amount': b_amount,
            'spent': spent,
            'remaining': remaining,
            'percentage': round(pct, 1),
            'status': status,
            'status_text': status_text
        })
        total_budgeted += b_amount
        total_spent += spent

    total_remaining = total_budgeted - total_spent
    overall_percentage = (total_spent / total_budgeted * 100.0) if total_budgeted > 0 else 0.0

    return {
        'month': month,
        'budgets': budget_list,
        'total_budgeted': total_budgeted,
        'total_spent': total_spent,
        'total_remaining': total_remaining,
        'overall_percentage': round(overall_percentage, 1),
        'has_warning': any(b['status'] in ('warning', 'danger') for b in budget_list)
    }

def get_categories(user_id, trans_type=None):
    """
    Get all unique categories available to a user:
    Default system categories + user's previously used categories.
    """
    db = get_db()
    type_filter = ""
    params = [user_id]
    if trans_type in ('income', 'expense'):
        type_filter = " AND (type = ? OR type IS NULL)"
        params.append(trans_type)

    # Categories from category table
    rows = db.execute(
        f"""
        SELECT DISTINCT name, type, icon, color
        FROM categories
        WHERE (user_id IS NULL OR user_id = ?){type_filter}
        ORDER BY name ASC
        """,
        tuple(params)
    ).fetchall()

    return [dict(row) for row in rows]

