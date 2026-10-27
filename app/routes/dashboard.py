import json
from flask import Blueprint, render_template, request, g
from app.utils import login_required
from app.services.finance_service import (
    get_current_month,
    get_financial_summary,
    get_recent_transactions,
    get_budget_status,
    get_category_breakdown,
    get_monthly_trend,
    get_categories,
    get_today_date
)

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    user_id = g.current_user['id']
    selected_month = request.args.get('month', get_current_month()).strip()

    # Financial summary
    summary = get_financial_summary(user_id, selected_month)

    # Recent transactions
    recent_txs = get_recent_transactions(user_id, limit=6)

    # Budget status for selected month
    budget_data = get_budget_status(user_id, selected_month)

    # Expense breakdown for doughnut chart
    expense_breakdown, total_expense_breakdown = get_category_breakdown(
        user_id, month=selected_month, trans_type='expense'
    )

    # 6-month trend for bar chart
    trend_data = get_monthly_trend(user_id, num_months=6)

    # Preload categories for quick-add modal
    categories = get_categories(user_id)

    # Prepare JSON serializable chart data for frontend Chart.js
    chart_category_labels = [item['category'] for item in expense_breakdown]
    chart_category_data = [item['total_amount'] for item in expense_breakdown]

    return render_template(
        'dashboard/index.html',
        summary=summary,
        recent_transactions=recent_txs,
        budget_data=budget_data,
        expense_breakdown=expense_breakdown,
        trend_data=trend_data,
        categories=categories,
        selected_month=selected_month,
        today_date=get_today_date(),
        chart_category_labels_json=json.dumps(chart_category_labels),
        chart_category_data_json=json.dumps(chart_category_data),
        chart_trend_labels_json=json.dumps(trend_data['labels']),
        chart_trend_income_json=json.dumps(trend_data['income']),
        chart_trend_expense_json=json.dumps(trend_data['expense'])
    )

