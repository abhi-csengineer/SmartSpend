import json
from datetime import datetime
from flask import Blueprint, render_template, request, g
from app.utils import login_required
from app.services.finance_service import (
    get_category_breakdown,
    get_monthly_trend
)
from app.database import get_db

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/', methods=['GET'])
@login_required
def index():
    user_id = g.current_user['id']
    months_count = request.args.get('months', '6').strip()
    
    try:
        num_months = int(months_count)
        if num_months not in (3, 6, 12):
            num_months = 6
    except ValueError:
        num_months = 6

    # Monthly trend data
    trend_data = get_monthly_trend(user_id, num_months=num_months)

    # Category breakdown across the selected period
    db = get_db()
    # Get earliest month in period
    start_month = trend_data['months'][0] if trend_data['months'] else '2000-01'
    
    expense_rows = db.execute(
        """
        SELECT category, SUM(amount) AS total_amount, COUNT(id) AS count
        FROM transactions
        WHERE user_id = ? AND type = 'expense' AND strftime('%Y-%m', date) >= ?
        GROUP BY category
        ORDER BY total_amount DESC
        """,
        (user_id, start_month)
    ).fetchall()

    income_rows = db.execute(
        """
        SELECT category, SUM(amount) AS total_amount, COUNT(id) AS count
        FROM transactions
        WHERE user_id = ? AND type = 'income' AND strftime('%Y-%m', date) >= ?
        GROUP BY category
        ORDER BY total_amount DESC
        """,
        (user_id, start_month)
    ).fetchall()

    total_period_income = sum(trend_data['income'])
    total_period_expense = sum(trend_data['expense'])
    net_savings = total_period_income - total_period_expense
    savings_rate = (net_savings / total_period_income * 100.0) if total_period_income > 0 else 0.0
    avg_monthly_expense = (total_period_expense / num_months) if num_months > 0 else 0.0

    # Format expense breakdown table
    expense_categories = []
    for r in expense_rows:
        pct = (r['total_amount'] / total_period_expense * 100.0) if total_period_expense > 0 else 0.0
        expense_categories.append({
            'category': r['category'],
            'total_amount': float(r['total_amount']),
            'count': r['count'],
            'percentage': round(pct, 1)
        })

    # Top spending category
    top_category = expense_categories[0]['category'] if expense_categories else "None"

    # JSON for frontend Chart.js
    chart_category_labels = [c['category'] for c in expense_categories]
    chart_category_data = [c['total_amount'] for c in expense_categories]

    # Calculate net savings for each month in trend
    savings_data = [inc - exp for inc, exp in zip(trend_data['income'], trend_data['expense'])]

    return render_template(
        'reports/index.html',
        num_months=num_months,
        total_income=total_period_income,
        total_expense=total_period_expense,
        net_savings=net_savings,
        savings_rate=round(savings_rate, 1),
        avg_monthly_expense=round(avg_monthly_expense, 2),
        top_category=top_category,
        expense_categories=expense_categories,
        trend_data=trend_data,
        chart_category_labels_json=json.dumps(chart_category_labels),
        chart_category_data_json=json.dumps(chart_category_data),
        chart_trend_labels_json=json.dumps(trend_data['labels']),
        chart_trend_income_json=json.dumps(trend_data['income']),
        chart_trend_expense_json=json.dumps(trend_data['expense']),
        chart_savings_data_json=json.dumps(savings_data)
    )

