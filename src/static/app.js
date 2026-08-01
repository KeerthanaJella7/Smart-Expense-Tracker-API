/**
 * Smart Expense Tracker - Frontend Application Engine
 * Communicates with FastAPI REST API endpoints.
 */

class ExpenseTrackerApp {
  constructor() {
    this.expenses = [];
    this.selectedCategory = '';
    this.searchQuery = '';
    this.sortBy = 'date-desc';

    this.categoryIcons = {
      'Food': 'fa-utensils',
      'Transport': 'fa-car',
      'Utilities': 'fa-lightbulb',
      'Entertainment': 'fa-film',
      'Health': 'fa-heart-pulse',
      'Shopping': 'fa-bag-shopping',
      'Other': 'fa-box'
    };

    this.categoryColors = {
      'Food': '#f43f5e',
      'Transport': '#06b6d4',
      'Utilities': '#f59e0b',
      'Entertainment': '#8b5cf6',
      'Health': '#10b981',
      'Shopping': '#ec4899',
      'Other': '#9ca3af'
    };

    this.initDOM();
    this.bindEvents();
    this.loadData();
  }

  initDOM() {
    this.expenseListEl = document.getElementById('expense-list');
    this.categoryBreakdownEl = document.getElementById('category-breakdown-list');
    this.statTotalEl = document.getElementById('stat-total-value');
    this.statCountEl = document.getElementById('stat-count-value');
    this.statTopEl = document.getElementById('stat-top-value');
    this.statAvgEl = document.getElementById('stat-avg-value');
    this.resultsCountEl = document.getElementById('results-count');
    this.searchInput = document.getElementById('search-input');
    this.sortSelect = document.getElementById('sort-select');
    this.modalOverlay = document.getElementById('modal-overlay');
    this.expenseForm = document.getElementById('expense-form');
    this.toastContainer = document.getElementById('toast-container');

    // Default modal date to today
    document.getElementById('expense-date').value = new Date().toISOString().split('T')[0];
  }

  bindEvents() {
    // Open / Close Modal
    document.getElementById('btn-open-modal').addEventListener('click', () => this.openModal());
    document.getElementById('btn-close-modal').addEventListener('click', () => this.closeModal());
    document.getElementById('btn-cancel-modal').addEventListener('click', () => this.closeModal());

    // Submit Form
    this.expenseForm.addEventListener('submit', (e) => this.handleFormSubmit(e));

    // Search & Sort
    this.searchInput.addEventListener('input', (e) => {
      this.searchQuery = e.target.value.toLowerCase().trim();
      this.render();
    });

    this.sortSelect.addEventListener('change', (e) => {
      this.sortBy = e.target.value;
      this.render();
    });

    // Category Pill Filters
    const pills = document.querySelectorAll('.category-pills .pill');
    pills.forEach(pill => {
      pill.addEventListener('click', () => {
        pills.forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        this.selectedCategory = pill.getAttribute('data-category');
        this.loadData();
      });
    });
  }

  openModal() {
    this.modalOverlay.classList.add('active');
  }

  closeModal() {
    this.modalOverlay.classList.remove('active');
    this.expenseForm.reset();
    document.getElementById('expense-date').value = new Date().toISOString().split('T')[0];
  }

  showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
      <i class="fa-solid ${type === 'success' ? 'fa-circle-check' : 'fa-circle-exclamation'}" style="color: ${type === 'success' ? 'var(--accent-emerald)' : 'var(--accent-rose)'};"></i>
      <span>${message}</span>
    `;
    this.toastContainer.appendChild(toast);
    setTimeout(() => toast.remove(), 3500);
  }

  async loadData() {
    try {
      let url = '/expenses';
      if (this.selectedCategory) {
        url += `?category=${encodeURIComponent(this.selectedCategory)}`;
      }
      const response = await fetch(url);
      if (!response.ok) throw new Error('Failed to load expenses');
      this.expenses = await response.json();
      this.render();
    } catch (err) {
      this.showToast(err.message, 'error');
    }
  }

  async handleFormSubmit(e) {
    e.preventDefault();
    const title = document.getElementById('expense-title').value.trim();
    const amount = parseFloat(document.getElementById('expense-amount').value);
    const category = document.getElementById('expense-category').value;
    const date = document.getElementById('expense-date').value;

    if (!title || isNaN(amount) || amount <= 0 || !category || !date) {
      this.showToast('Please provide valid values for all fields', 'error');
      return;
    }

    try {
      const response = await fetch('/expenses', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, amount, category, date })
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.error || 'Failed to create expense');
      }

      this.showToast('Expense created successfully!');
      this.closeModal();
      this.loadData();
    } catch (err) {
      this.showToast(err.message, 'error');
    }
  }

  async deleteExpense(id) {
    try {
      const response = await fetch(`/expenses/${id}`, { method: 'DELETE' });
      if (!response.ok) throw new Error('Failed to delete expense');
      this.showToast('Expense deleted');
      this.loadData();
    } catch (err) {
      this.showToast(err.message, 'error');
    }
  }

  getFilteredAndSortedExpenses() {
    let list = [...this.expenses];

    if (this.searchQuery) {
      list = list.filter(exp => exp.title.toLowerCase().includes(this.searchQuery));
    }

    list.sort((a, b) => {
      if (this.sortBy === 'date-desc') return new Date(b.date) - new Date(a.date);
      if (this.sortBy === 'date-asc') return new Date(a.date) - new Date(b.date);
      if (this.sortBy === 'amount-desc') return b.amount - a.amount;
      if (this.sortBy === 'amount-asc') return a.amount - b.amount;
      return 0;
    });

    return list;
  }

  render() {
    const filtered = this.getFilteredAndSortedExpenses();
    this.renderStats(filtered);
    this.renderList(filtered);
    this.renderCategoryBreakdown();
  }

  renderStats(filteredList) {
    const total = filteredList.reduce((sum, item) => sum + item.amount, 0);
    const count = filteredList.length;
    const avg = count > 0 ? total / count : 0;

    // Find top category
    const categoryTotals = {};
    this.expenses.forEach(exp => {
      categoryTotals[exp.category] = (categoryTotals[exp.category] || 0) + exp.amount;
    });

    let topCat = 'N/A';
    let maxVal = 0;
    for (const [cat, sum] of Object.entries(categoryTotals)) {
      if (sum > maxVal) {
        maxVal = sum;
        topCat = cat;
      }
    }

    this.statTotalEl.textContent = `$${total.toFixed(2)}`;
    this.statCountEl.textContent = count;
    this.statTopEl.textContent = topCat;
    this.statAvgEl.textContent = `$${avg.toFixed(2)}`;
    this.resultsCountEl.textContent = `${filteredList.length} items`;
  }

  renderList(filteredList) {
    this.expenseListEl.innerHTML = '';

    if (filteredList.length === 0) {
      this.expenseListEl.innerHTML = `
        <div class="empty-state">
          <i class="fa-solid fa-folder-open empty-icon"></i>
          <h3>No expenses found</h3>
          <p style="color: var(--text-muted); font-size: 0.9rem;">Add a new expense or clear your search filter.</p>
        </div>
      `;
      return;
    }

    filteredList.forEach(exp => {
      const card = document.createElement('div');
      card.className = 'expense-card';
      const catClass = `cat-${exp.category}`;
      const icon = this.categoryIcons[exp.category] || 'fa-tag';

      card.innerHTML = `
        <div class="expense-left">
          <div class="category-avatar ${catClass}">
            <i class="fa-solid ${icon}"></i>
          </div>
          <div class="expense-info">
            <span class="expense-title-text">${this.escapeHTML(exp.title)}</span>
            <div class="expense-meta">
              <span class="expense-date"><i class="fa-regular fa-calendar"></i> ${exp.date}</span>
              <span>•</span>
              <span class="expense-category-badge">${exp.category}</span>
            </div>
          </div>
        </div>

        <div class="expense-right">
          <div class="expense-amount">$${exp.amount.toFixed(2)}</div>
          <button class="btn-delete" title="Delete Expense" onclick="app.deleteExpense(${exp.id})">
            <i class="fa-solid fa-trash"></i>
          </button>
        </div>
      `;

      this.expenseListEl.appendChild(card);
    });
  }

  renderCategoryBreakdown() {
    this.categoryBreakdownEl.innerHTML = '';
    const overallTotal = this.expenses.reduce((sum, e) => sum + e.amount, 0);

    if (overallTotal === 0) {
      this.categoryBreakdownEl.innerHTML = '<p style="color: var(--text-muted); font-size: 0.85rem;">No category data yet.</p>';
      return;
    }

    const categorySums = {};
    this.expenses.forEach(exp => {
      categorySums[exp.category] = (categorySums[exp.category] || 0) + exp.amount;
    });

    Object.entries(categorySums)
      .sort((a, b) => b[1] - a[1])
      .forEach(([cat, sum]) => {
        const percent = ((sum / overallTotal) * 100).toFixed(1);
        const color = this.categoryColors[cat] || '#8b5cf6';

        const item = document.createElement('div');
        item.className = 'category-bar-item';
        item.innerHTML = `
          <div class="bar-meta">
            <span class="bar-name">${cat}</span>
            <span class="bar-amount">$${sum.toFixed(2)} (${percent}%)</span>
          </div>
          <div class="progress-track">
            <div class="progress-fill" style="width: ${percent}%; background: ${color};"></div>
          </div>
        `;
        this.categoryBreakdownEl.appendChild(item);
      });
  }

  escapeHTML(str) {
    return str.replace(/[&<>'"]/g, 
      tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
    );
  }
}

// Initialize Application on DOM Ready
let app;
document.addEventListener('DOMContentLoaded', () => {
  app = new ExpenseTrackerApp();
});
