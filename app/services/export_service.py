import csv
import io
from datetime import datetime

def generate_transactions_csv(transactions, currency='$'):
    """
    Generate RFC 4180 compliant CSV string from list of transaction dicts.
    """
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

    # Header row
    writer.writerow([
        'Transaction ID',
        'Type',
        'Category',
        f'Amount ({currency})',
        'Date',
        'Description',
        'Created At'
    ])

    for t in transactions:
        amount_val = float(t.get('amount', 0.0))
        writer.writerow([
            t.get('id', ''),
            t.get('type', '').capitalize(),
            t.get('category', ''),
            f"{amount_val:.2f}",
            t.get('date', ''),
            t.get('description', '') or '',
            t.get('created_at', '') or ''
        ])

    return output.getvalue()

def get_export_filename(prefix="transactions"):
    """Generate timestamped filename for downloaded report."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"smartspend_{prefix}_{timestamp}.csv"

