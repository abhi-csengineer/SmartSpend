// SmartSpend Core UI & Interactive Logic
document.addEventListener('DOMContentLoaded', () => {
  // 1. Mobile Menu Toggle
  const mobileToggle = document.getElementById('mobile-menu-toggle');
  const navMenu = document.getElementById('navbar-menu');
  if (mobileToggle && navMenu) {
    mobileToggle.addEventListener('click', () => {
      navMenu.classList.toggle('show');
    });
  }

  // 2. Alert Dismissal
  document.querySelectorAll('.alert-close').forEach(btn => {
    btn.addEventListener('click', () => {
      const alert = btn.closest('.alert');
      if (alert) {
        alert.style.opacity = '0';
        alert.style.transition = 'opacity 0.2s ease';
        setTimeout(() => alert.remove(), 200);
      }
    });
  });

  // 3. Modals
  window.openModal = function(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add('show');
      document.body.style.overflow = 'hidden';
    }
  };

  window.closeModal = function(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove('show');
      document.body.style.overflow = '';
    }
  };

  // Close modal when clicking on backdrop
  document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
    backdrop.addEventListener('click', (e) => {
      if (e.target === backdrop) {
        backdrop.classList.remove('show');
        document.body.style.overflow = '';
      }
    });
  });

  // Close modal on Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      document.querySelectorAll('.modal-backdrop.show').forEach(m => {
        m.classList.remove('show');
        document.body.style.overflow = '';
      });
    }
  });

  // 4. Dynamic category filtering based on transaction type selection
  const typeRadios = document.querySelectorAll('input[name="type"]');
  const categorySelect = document.getElementById('transaction-category');
  if (typeRadios.length > 0 && categorySelect) {
    function filterCategories() {
      const selectedType = document.querySelector('input[name="type"]:checked')?.value || 'expense';
      const options = categorySelect.querySelectorAll('option[data-type]');
      let firstVisibleSelected = false;

      options.forEach(opt => {
        const optType = opt.getAttribute('data-type');
        if (optType === selectedType || optType === 'both') {
          opt.style.display = '';
          opt.disabled = false;
          if (!firstVisibleSelected && opt.value) {
            if (!categorySelect.value || categorySelect.selectedOptions[0]?.disabled) {
              opt.selected = true;
            }
            firstVisibleSelected = true;
          }
        } else {
          opt.style.display = 'none';
          opt.disabled = true;
          if (opt.selected) {
            opt.selected = false;
          }
        }
      });
    }

    typeRadios.forEach(radio => radio.addEventListener('change', filterCategories));
    // Run on initial load
    filterCategories();
  }
});

