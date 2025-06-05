let allArticles = [];
const filterSelect = document.getElementById("filter-select");
const tableBody = document.querySelector("#articles-table tbody");
const canvasCtx = document.getElementById("sentiment-chart").getContext("2d");

async function loadData() {
  await fetch(`${API_BASE}/fetch/${STUDENT_ID}`, { method: "POST" });
  const res = await fetch(`${API_BASE}/analyze/${STUDENT_ID}`, { method: "POST" });
  const data = await res.json();
  allArticles = data.articles.map(a => ({
    ...a,
    date: a.published ? new Date(a.published) : new Date()
  }));
  render();
}

function render() {
  const filter = filterSelect.value;
  const filtered = allArticles.filter(a => filter === "all" || a.sentiment === filter);
  tableBody.innerHTML = filtered.map(a => `
    <tr>
      <td>${a.date.toLocaleString()}</td>
      <td>${a.sentiment}</td>
      <td><a href="${a.link}" target="_blank">${a.title}</a></td>
    </tr>`).join("");

  const counts = { positive: 0, neutral: 0, negative: 0 };
  filtered.forEach(a => counts[a.sentiment]++);
  chart.data.datasets[0].data = [counts.positive, counts.neutral, counts.negative];
  chart.update();
}

const chart = new Chart(canvasCtx, {
  type: 'pie',
  data: {
    labels: ['Позитивні', 'Нейтральні', 'Негативні'],
    datasets: [{
      data: [0, 0, 0],
      backgroundColor: ['#4caf50', '#ffca28', '#f44336']
    }]
  }
});

filterSelect.addEventListener("change", render);
window.addEventListener("load", loadData);
