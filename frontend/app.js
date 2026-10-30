const form = document.querySelector("#task-form");
const input = document.querySelector("#task-input");
const submitButton = form.querySelector("button");
const resultPanel = document.querySelector("#plan-result");
const apiBaseUrl = (window.KPMC_API_BASE_URL || "").replace(/\/$/, "");

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[character]);
}

function renderPlan(result) {
  const plan = result.plan;
  const tasks = plan.tasks.map((task) => `
    <article class="planned-task">
      <div class="planned-task-top"><strong>${escapeHtml(task.id)} · ${escapeHtml(task.title)}</strong><span class="status">${escapeHtml(task.role)}</span></div>
      <p>${escapeHtml(task.description)}</p>
      <small>Priority: ${escapeHtml(task.priority)} · Depends on: ${task.depends_on.length ? escapeHtml(task.depends_on.join(", ")) : "None"}</small>
    </article>
  `).join("");

  resultPanel.innerHTML = `
    <div class="plan-heading"><div><p class="eyebrow">PROPOSED PLAN</p><h2>Review before approval</h2></div><span class="status">Awaiting approval</span></div>
    <p class="plan-summary">${escapeHtml(plan.summary)}</p>
    <p class="hint">Model: ${escapeHtml(result.model)} · ${plan.tasks.length} tasks · No execution has started.</p>
    <div class="planned-tasks">${tasks}</div>
    <p class="hint">This version creates a plan only. Approval and execution controls are not enabled yet.</p>
  `;
  resultPanel.hidden = false;
  resultPanel.scrollIntoView({ behavior: "smooth", block: "start" });
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const task = input.value.trim();
  if (task.length < 10) {
    resultPanel.hidden = false;
    resultPanel.textContent = "Please describe the task in at least 10 characters.";
    return;
  }

  submitButton.disabled = true;
  submitButton.textContent = "Planning…";
  resultPanel.hidden = false;
  resultPanel.textContent = "The coordinator is breaking your request into specialist tasks…";

  try {
    const response = await fetch(`${apiBaseUrl}/api/v1/plans`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ task }),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || "Planning request failed.");
    renderPlan(payload);
  } catch (error) {
    resultPanel.textContent = `${error.message} Check that the FastAPI backend is running and its URL is configured.`;
  } finally {
    submitButton.disabled = false;
    submitButton.innerHTML = 'Create task <span aria-hidden="true">→</span>';
  }
});
