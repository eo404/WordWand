function parseJsonScript(id, fallback) {
  const node = document.getElementById(id);
  if (!node) return fallback;

  try {
    return JSON.parse(node.textContent);
  } catch (error) {
    return fallback;
  }
}

function getHeatmapColor(hours, maxHours) {
  const normalizedMax = maxHours > 0 ? maxHours : 1;
  const intensity = hours / normalizedMax;

  if (hours === 0) return "#E8E3FF";
  if (intensity < 0.25) return "#C4B5FD";
  if (intensity < 0.5) return "#A78BFA";
  if (intensity < 0.75) return "#8B6FE8";
  return "#5B3FBF";
}

const heatmapData = parseJsonScript("heatmap-data", []);
const maxHours = parseJsonScript("max-hours", 1);
const chartCoursesRaw = parseJsonScript("chart-courses-data", {});
const days = parseJsonScript("days-data", ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]);
const completedPct = parseJsonScript("completed-pct-data", 0);
const inProgressPct = parseJsonScript("inprogress-pct-data", 0);

// Heatmap
const heatmapContainer = document.getElementById("heatmap");
if (heatmapContainer && Array.isArray(heatmapData)) {
  heatmapData.forEach((day) => {
    const cell = document.createElement("div");
    cell.classList.add("heatmap-cell");
    cell.style.backgroundColor = getHeatmapColor(day.hours, maxHours);
    cell.title = `${day.date} - ${day.hours} hours`;
    heatmapContainer.appendChild(cell);
  });
}

// Hours Chart
if (Object.keys(chartCoursesRaw).length > 0) {

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
  const completed = !isNaN(completedPct) ? completedPct : 0;
  const inProgress = !isNaN(inProgressPct) ? inProgressPct : 0;

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