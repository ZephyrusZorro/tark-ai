/* Local draft storage and a text-only Python color layer; no code is executed. */
(() => {
  const storageKey = "tark.drafts.v1";
  let persistent = true;
  let entries = [];
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey) || "{}");
    if (saved && typeof saved === "object" && !Array.isArray(saved)) {
      entries = Object.entries(saved).filter(([key, value]) => key.length < 120 && typeof value === "string");
    }
  } catch (_) { persistent = false; }
  const cache = new Map(entries);
  const unsaved = new Set();
  function readLatest() {
    const saved = JSON.parse(localStorage.getItem(storageKey) || "{}");
    return new Map(saved && typeof saved === "object" && !Array.isArray(saved) ? Object.entries(saved).filter(([key, value]) => key.length < 120 && typeof value === "string") : []);
  }
  const updateStatus = () => {
    const label = document.getElementById("draft-status");
    const editor = document.getElementById("code-editor");
    if (label && editor) {
      const lines = editor.value.split("\n").length;
      label.textContent = `${persistent ? "Saved locally" : "Saved in this tab"} · ${lines} ${lines === 1 ? "line" : "lines"}`;
      label.dataset.persistent = String(persistent);
    }
  };
  const persist = (id, code, remove = false) => {
    try {
      // Merge the changed entry into the latest store rather than overwriting
      // other tabs' newer work with this tab's cached snapshot.
      let latest;
      try { latest = readLatest(); }
      catch (error) { if (error instanceof SyntaxError) latest = new Map(); else throw error; }
      if (remove) latest.delete(id); else latest.set(id, code);
      localStorage.setItem(storageKey, JSON.stringify(Object.fromEntries(latest)));
      persistent = true;
      unsaved.delete(id);
    }
    catch (_) { persistent = false; unsaved.add(id); }
    updateStatus();
  };
  window.TarkDrafts = {
    get: id => {
      if (unsaved.has(id)) return cache.get(id);
      try {
        const latest = readLatest();
        if (latest.has(id)) cache.set(id, latest.get(id)); else cache.delete(id);
      } catch (_) { persistent = false; }
      return cache.get(id);
    },
    set: (id, code) => { cache.set(id, code); persist(id, code); },
    delete: id => { cache.delete(id); persist(id, undefined, true); }
  };

  const tokenPattern = /("""[\s\S]*?(?:"""|$)|'''[\s\S]*?(?:'''|$)|"(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*'|#[^\n]*|\b(?:False|None|True|and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield)\b|\b(?:len|range|enumerate|zip|list|dict|set|tuple|str|int|float|bool|print|sum|min|max|sorted|reversed|isinstance|abs)\b|\b\d+(?:\.\d+)?\b)/g;
  function render(editor) {
    let layer = document.getElementById("code-highlight");
    if (!layer) {
      layer = document.createElement("pre");
      layer.id = "code-highlight";
      layer.setAttribute("aria-hidden", "true");
      editor.before(layer);
      editor.wrap = "off";
      editor.classList.add("syntax-ready");
      editor.addEventListener("scroll", () => { layer.scrollTop = editor.scrollTop; layer.scrollLeft = editor.scrollLeft; });
    }
    const source = editor.value;
    const fragment = document.createDocumentFragment();
    let position = 0;
    for (const match of source.matchAll(tokenPattern)) {
      fragment.append(document.createTextNode(source.slice(position, match.index)));
      const token = document.createElement("span");
      const value = match[0];
      token.className = value.startsWith("#") ? "token-comment" : /^["']/.test(value) ? "token-string" : /^\d/.test(value) ? "token-number" : /^(len|range|enumerate|zip|list|dict|set|tuple|str|int|float|bool|print|sum|min|max|sorted|reversed|isinstance|abs)$/.test(value) ? "token-builtin" : "token-keyword";
      token.textContent = value;
      fragment.append(token);
      position = match.index + value.length;
    }
    fragment.append(document.createTextNode(source.slice(position) + "\n"));
    layer.replaceChildren(fragment);
    layer.scrollTop = editor.scrollTop;
    layer.scrollLeft = editor.scrollLeft;
    updateStatus();
  }
  window.TarkEditor = { render };
})();
