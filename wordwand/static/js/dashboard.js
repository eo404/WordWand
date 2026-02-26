if (typeof chartCoursesRaw !== "undefined" && Object.keys(chartCoursesRaw).length > 0) {

  const colors = ['#8B6FE8', '#C4B5FD', '#5B3FBF', '#A78BFA'];

  const courseNames = Object.keys(chartCoursesRaw);

  const datasets = courseNames.map((name, i) => ({
    label: name,
    data: chartCoursesRaw[name],
    backgroundColor: colors[i % colors.length],
    borderRadius: 6,
    barThickness: 18,
  }));

  const legend = document.getElementById('chartLegend');
  courseNames.forEach((name, i) => {
    legend.innerHTML += `
      <div>
        <span style="display:inline-block;width:10px;height:10px;background:${colors[i%colors.length]};border-radius:50%;margin-right:5px;"></span>
        ${name}
      </div>
    `;
  });

  new Chart(document.getElementById('hoursChart'), {
    type: 'bar',
    data: { labels: days, datasets },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true } }
    }
  });
}

new Chart(document.getElementById('progressChart'), {
  type: 'doughnut',
  data: {
    datasets: [{
      data: [completedPct, inProgressPct],
      backgroundColor: ['#5B3FBF', '#C4B5FD'],
      borderWidth: 0
    }]
  },
  options: {
    cutout: '70%',
    plugins: { legend: { display: false } }
  }
});