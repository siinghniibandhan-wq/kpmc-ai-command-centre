const form = document.querySelector("#task-form");
const input = document.querySelector("#task-input");

form.addEventListener("submit", (event) => {
  event.preventDefault();
  if (!input.value.trim()) return;
  window.alert("This is the initial UI scaffold. Task execution will be enabled when the backend coordinator is implemented.");
});
