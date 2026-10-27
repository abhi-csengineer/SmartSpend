// SmartSpend Financial Charts Engine (Powered by Chart.js)

const PALETTE = [
  '#f97316', '#3b82f6', '#06b6d4', '#eab308', '#a855f7',
  '#ec4899', '#14b8a6', '#6366f1', '#f43f5e', '#10b981',
  '#84cc16', '#64748b'
];

/**
 * Initialize Doughnut Chart for Spending Breakdown by Category
 */
function initCategoryDoughnut(canvasId, labels, data, currency) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;

  if (!data || data.length === 0 || data.every(v => v === 0)) {
    // Show empty state inside canvas container
    const parent = ctx.parentElement;
    parent.innerHTML = `
      <div class="empty-state" style="padding: 2rem 1rem;">
        <div class="empty-state-icon" style="width:48px;height:48px;font-size:1.25rem;">📊</div>
        <p style="color:var(--text-muted);font-size:0.9rem;">No expense data for this period.</p>
      </div>
    `;
    return null;
  }

  return new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: PALETTE.slice(0, labels.length),
        borderWidth: 2,
        borderColor: '#ffffff',
        hoverOffset: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'right',
          labels: {
            boxWidth: 12,
            font: { family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto', size: 12 },
            color: '#475569',
            padding: 10
          }
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const val = context.parsed;
              const total = context.dataset.data.reduce((a, b) => a + b, 0);
              const pct = total > 0 ? ((val / total) * 100).toFixed(1) : 0;
              return ` ${context.label}: ${currency}${val.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} (${pct}%)`;
            }
          }
        }
      },
      cutout: '68%'
    }
  });
}

/**
 * Initialize Grouped Bar Chart for Monthly Income vs Expense Trend
 */
function initMonthlyTrendBar(canvasId, labels, incomeData, expenseData, currency) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;

  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Income',
          data: incomeData,
          backgroundColor: '#10b981',
          borderRadius: 6,
          barPercentage: 0.65,
          categoryPercentage: 0.7
        },
        {
          label: 'Expenses',
          data: expenseData,
          backgroundColor: '#ef4444',
          borderRadius: 6,
          barPercentage: 0.65,
          categoryPercentage: 0.7
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { color: '#64748b', font: { size: 11 } }
        },
        y: {
          grid: { color: '#f1f5f9' },
          ticks: {
            color: '#64748b',
            font: { size: 11 },
            callback: function(value) {
              return currency + value.toLocaleString();
            }
          }
        }
      },
      plugins: {
        legend: {
          position: 'top',
          align: 'end',
          labels: {
            boxWidth: 12,
            color: '#475569',
            font: { size: 12, weight: '500' }
          }
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const val = context.parsed.y;
              return ` ${context.dataset.label}: ${currency}${val.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
            }
          }
        }
      }
    }
  });
}

/**
 * Initialize Savings Line Chart for Reports
 */
function initSavingsLineChart(canvasId, labels, savingsData, currency) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;

  return new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Net Monthly Savings',
        data: savingsData,
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.08)',
        fill: true,
        tension: 0.35,
        pointBackgroundColor: '#3b82f6',
        pointRadius: 4,
        pointHoverRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { grid: { display: false } },
        y: {
          grid: { color: '#f1f5f9' },
          ticks: {
            callback: function(val) {
              return currency + val.toLocaleString();
            }
          }
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: function(context) {
              const val = context.parsed.y;
              return ` Net Savings: ${currency}${val.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
            }
          }
        }
      }
    }
  });
}

