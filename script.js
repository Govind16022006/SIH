document.getElementById('progressForm').addEventListener('submit', function(e) {
  e.preventDefault();

  const name = document.getElementById('studentName').value.trim();
  const score = parseInt(document.getElementById('score').value);
  const grade = getGrade(score);

  const tbody = document.querySelector('#progressTable tbody');
  const newRow = document.createElement('tr');
  newRow.classList.add('new-entry');

  newRow.innerHTML = `
    <td>${name}</td>
    <td>${score}</td>
    <td>${grade}</td>
  `;

  tbody.appendChild(newRow);

  // Clear form
  document.getElementById('progressForm').reset();
});

// Load progress data from localStorage and display in table
function loadProgressData() {
  const progressData = JSON.parse(localStorage.getItem('progressData')) || [];
  const tbody = document.querySelector('#progressTable tbody');
  tbody.innerHTML = ''; // Clear existing rows

  progressData.forEach(entry => {
    const grade = getGrade(entry.score);
    const newRow = document.createElement('tr');
    newRow.innerHTML = `
      <td>${entry.name}</td>
      <td>${entry.score}</td>
      <td>${grade}</td>
    `;
    tbody.appendChild(newRow);
  });
}

function getGrade(score) {
  if (score >= 90) return 'A+';
  else if (score >= 80) return 'A';
  else if (score >= 70) return 'B';
  else if (score >= 60) return 'C';
  else if (score >= 50) return 'D';
  else return 'F';
}

const backBtn = document.getElementById('back-btn');

backBtn.addEventListener('click', () => {
  window.location.href = '../PROJECT_OF_HACKATHON.html';
});

// Load progress data on page load
window.addEventListener('DOMContentLoaded', loadProgressData);
