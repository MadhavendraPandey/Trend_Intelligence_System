// Theme Toggle
const themeToggle = document.getElementById('themeToggle');
let isDarkTheme = true;

themeToggle.addEventListener('click', () => {
  isDarkTheme = !isDarkTheme;
  document.body.classList.toggle('light-theme', !isDarkTheme);
  
  // Update icon based on theme
  if (isDarkTheme) {
    themeToggle.innerHTML = '☀️';
  } else {
    themeToggle.innerHTML = '🌙';
  }
});

// Intelligence Card Selection
const trendCard = document.getElementById('trendCard');
const frictionCard = document.getElementById('frictionCard');
const viewReportsBtn = document.getElementById('viewReportsBtn');
const selectionMessage = document.getElementById('selectionMessage');

let selectedIntelligence = null;

if (trendCard) {
  trendCard.addEventListener('click', () => {
    selectedIntelligence = 'trend';
    trendCard.classList.add('selected');
    frictionCard.classList.remove('selected');
    updateSelectionMessage();
  });
}

if (frictionCard) {
  frictionCard.addEventListener('click', () => {
    selectedIntelligence = 'friction';
    frictionCard.classList.add('selected');
    trendCard.classList.remove('selected');
    updateSelectionMessage();
  });
}

function updateSelectionMessage() {
  if (selectedIntelligence) {
    selectionMessage.style.display = 'none';
  } else {
    selectionMessage.style.display = 'block';
  }
}

// View Reports Button
if (viewReportsBtn) {
  viewReportsBtn.addEventListener('click', () => {
    if (!selectedIntelligence) {
      selectionMessage.style.display = 'block';
      return;
    }

    if (selectedIntelligence === 'trend') {
      window.location.href = '/trend/reports';
    } else if (selectedIntelligence === 'friction') {
      window.location.href = '/friction/reports';
    }
  });
}

// Report Card Interaction
const reportCards = document.querySelectorAll('.report-card');
if (reportCards.length > 0) {
  reportCards.forEach(card => {
    card.addEventListener('mouseenter', () => {
      card.style.transform = 'translateY(-5px)';
      card.style.boxShadow = '0 10px 20px rgba(0, 0, 0, 0.2)';
      card.style.borderColor = 'var(--accent-color)';
    });
    
    card.addEventListener('mouseleave', () => {
      card.style.transform = 'translateY(0)';
      card.style.boxShadow = 'none';
      card.style.borderColor = 'rgba(255, 255, 255, 0.05)';
    });
  });
}
