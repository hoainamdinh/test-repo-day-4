(() => {
  "use strict";

  const checks = [...document.querySelectorAll("[data-progress]")];
  const progressLabel = document.querySelector("[data-progress-label]");
  const progressBar = document.querySelector("[data-progress-bar]");
  const printButton = document.querySelector("[data-print]");

  function updateProgress() {
    const completed = checks.filter((checkbox) => checkbox.checked).length;
    const total = checks.length;
    const percentage = total ? (completed / total) * 100 : 0;

    if (progressLabel) progressLabel.textContent = `${completed}/${total}`;
    if (progressBar) progressBar.style.setProperty("--progress", `${percentage}%`);
  }

  checks.forEach((checkbox) => checkbox.addEventListener("change", updateProgress));
  printButton?.addEventListener("click", () => window.print());
  updateProgress();
})();
