/* Workspace navigation and presentation independent of the code controller. */
document.addEventListener("DOMContentLoaded", () => {
  const search = document.getElementById("challenge-search");
  window.filterChallenges = () => {
    const query = search.value.trim().toLowerCase();
    const items = [...document.querySelectorAll(".challenge-item")];
    let count = 0;
    items.forEach(item => { item.hidden = !item.textContent.toLowerCase().includes(query); if (!item.hidden) count++; });
    document.getElementById("challenge-search-empty").hidden = count !== 0;
    document.getElementById("challenge-search-count").textContent = query ? `${count} of ${items.length}` : `${items.length} challenges`;
  };
  search.addEventListener("input", window.filterChallenges);
  document.addEventListener("keydown", event => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
      event.preventDefault();
      document.querySelector('[data-workspace="ws-code"]').click();
      search.focus();
      search.select();
    }
  });
  const titles = {
    "ws-code": ["Engineering studio", "Write with focus. Follow the logic. Find your next insight."],
    "ws-ast": ["Follow the logic", "See how your code moves, branches, and connects."],
    "ws-complexity": ["Under the surface", "Explore complexity, structure, and the cost of your approach."],
    "ws-leitner": ["Make it stick", "Return to what matters. Build understanding that lasts."],
    "ws-socrates": ["Room for a question", "Work toward the insight, one thoughtful question at a time."]
  };
  const tabs = [...document.querySelectorAll(".ws-btn")];
  const updateTitle = () => {
    const active = tabs.find(tab => tab.classList.contains("active"));
    if (!active) return;
    const [title, description] = titles[active.dataset.workspace];
    document.getElementById("studio-title").textContent = title + ".";
    document.getElementById("studio-description").textContent = description;
  };
  tabs.forEach((tab, index) => {
    new MutationObserver(updateTitle).observe(tab, { attributes: true, attributeFilter: ["class"] });
    tab.addEventListener("keydown", event => {
      if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
      event.preventDefault();
      const next = event.key === "Home" ? 0 : event.key === "End" ? tabs.length - 1 : (index + (event.key === "ArrowRight" ? 1 : -1) + tabs.length) % tabs.length;
      tabs[next].focus();
      tabs[next].click();
    });
  });
});
