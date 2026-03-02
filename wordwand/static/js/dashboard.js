// Hours Chart
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

  // Build legend
  const legend = document.getElementById('chartLegend');
  if (legend) {
    legend.innerHTML = '';
    courseNames.forEach((name, i) => {
      legend.innerHTML += `
        <div>
          <span style="display:inline-block;width:10px;height:10px;background:${colors[i % colors.length]};border-radius:50%;margin-right:5px;"></span>
          ${name}
        </div>
      `;
    });
  }

  // Create chart
  const ctx = document.getElementById('hoursChart');
  if (ctx) {
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: days,
        datasets
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: 'white',
            titleColor: '#1A1035',
            bodyColor: '#7C6FAB',
            borderColor: '#E8E3FF',
            borderWidth: 1,
            padding: 10,
            displayColors: true,
            callbacks: {
              label: function (context) {
                return `${context.dataset.label}: ${context.raw} hours`;
              }
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              color: '#E8E3FF',
              drawBorder: false
            },
            title: {
              display: true,
              text: 'Hours',
              color: '#7C6FAB',
              font: {
                size: 11
              }
            }
          },
          x: {
            grid: {
              display: false
            }
          }
        }
      }
    });
  }
}

// Progress Donut Chart
const progressCtx = document.getElementById('progressChart');
if (progressCtx) {
  // Ensure percentages are valid numbers
  const completed = typeof completedPct !== 'undefined' && !isNaN(completedPct) ? completedPct : 0;
  const inProgress = typeof inProgressPct !== 'undefined' && !isNaN(inProgressPct) ? inProgressPct : 0;

  // If both are 0 (no courses), show empty state (all gray)
  const data = (completed === 0 && inProgress === 0) ? [100] : [completed, inProgress];
  const backgroundColor = (completed === 0 && inProgress === 0)
    ? ['#E8E3FF']
    : ['#5B3FBF', '#C4B5FD'];

  new Chart(progressCtx, {
    type: 'doughnut',
    data: {
      datasets: [{
        data: data,
        backgroundColor: backgroundColor,
        borderWidth: 0,
        borderRadius: 0
      }]
    },
    options: {
      cutout: '70%',
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          enabled: !(completed === 0 && inProgress === 0),
          callbacks: {
            label: function (context) {
              const labels = ['Completed', 'In Progress'];
              return `${labels[context.dataIndex]}: ${context.raw}%`;
            }
          }
        }
      },
      layout: {
        padding: 0
      }
    }
  });
}