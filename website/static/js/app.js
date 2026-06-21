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

// View Evidence Button
const viewEvidenceBtns = document.querySelectorAll('.view-evidence-btn');
if (viewEvidenceBtns.length > 0) {
  viewEvidenceBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const evidenceId = btn.getAttribute('data-evidence-id');
      // In a real implementation, this would navigate to the evidence detail page
      console.log(`Viewing evidence: ${evidenceId}`);
    });
  });
}

// Open Report Button
const openReportBtns = document.querySelectorAll('.open-report-btn');
if (openReportBtns.length > 0) {
  openReportBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const reportId = btn.getAttribute('data-report-id');
      // In a real implementation, this would navigate to the report detail page
      console.log(`Opening report: ${reportId}`);
    });
  });
}

// Open Source Button
const openSourceBtns = document.querySelectorAll('.open-source-btn');
if (openSourceBtns.length > 0) {
  openSourceBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const sourceId = btn.getAttribute('data-source-id');
      // In a real implementation, this would navigate to the source detail page
      console.log(`Opening source: ${sourceId}`);
    });
  });
}

// View Original Button
const viewOriginalBtns = document.querySelectorAll('.view-original-btn');
if (viewOriginalBtns.length > 0) {
  viewOriginalBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const postId = btn.getAttribute('data-post-id');
      // In a real implementation, this would navigate to the original post
      console.log(`Viewing original post: ${postId}`);
    });
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

// Evidence Card Interaction
const evidenceCards = document.querySelectorAll('.evidence-card');
if (evidenceCards.length > 0) {
  evidenceCards.forEach(card => {
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

// Source Card Interaction
const sourceCards = document.querySelectorAll('.source-card');
if (sourceCards.length > 0) {
  sourceCards.forEach(card => {
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
