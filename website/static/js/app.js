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

trendCard.addEventListener('click', () => {
  selectedIntelligence = 'trend';
  trendCard.classList.add('selected');
  frictionCard.classList.remove('selected');
  updateSelectionMessage();
});

frictionCard.addEventListener('click', () => {
  selectedIntelligence = 'friction';
  frictionCard.classList.add('selected');
  trendCard.classList.remove('selected');
  updateSelectionMessage();
});

function updateSelectionMessage() {
  if (selectedIntelligence) {
    selectionMessage.style.display = 'none';
  } else {
    selectionMessage.style.display = 'block';
  }
}

// View Reports Button
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
