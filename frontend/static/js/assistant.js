/* Assistant virtuel du PAD — fenêtre de discussion flottante (amélioration progressive).
   Balisage et textes traduits : templates/includes/assistant.html. Aucun code inline (ADR 0002).
   La conversation est conservée le temps de l'onglet (sessionStorage, fonction strictement
   nécessaire, aucun traceur) et n'est jamais envoyée ailleurs qu'au serveur du site. */
(() => {
  const root = document.querySelector("[data-assistant]");
  if (!root || !window.fetch || !window.TextDecoder) return;

  const $ = (sel) => root.querySelector(sel);
  const panel = $("#assistant-panel");
  const log = $("[data-assistant-log]");
  const form = $("[data-assistant-form]");
  const input = $("#assistant-input");
  const send = $(".assistant-send");
  const launcher = $("[data-assistant-launcher]");
  const launcherLabel = $("[data-assistant-launcher-label]");
  const teaser = $("[data-assistant-teaser]");
  const msg = root.dataset;
  const STORE = "pad-assistant-v1";

  let history = [];
  let busy = false;
  let controller = null;

  try {
    history = JSON.parse(sessionStorage.getItem(STORE) || "[]");
  } catch (e) {
    history = [];
  }
  const save = () => {
    try {
      sessionStorage.setItem(STORE, JSON.stringify(history.slice(-20)));
    } catch (e) {
      /* stockage indisponible (navigation privée) : la conversation vit en mémoire */
    }
  };

  /* ---------- rendu : mini-Markdown sûr (texte échappé puis quelques balises autorisées) */
  const escapeHtml = (s) =>
    s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);

  const inline = (s) =>
    s
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/\[([^\]]+)\]\(((?:https?:\/\/|\/(?!\/))[^)\s]+)\)/g, (m, text, url) => {
        const external = /^https?:/.test(url) && !url.startsWith(location.origin);
        return `<a href="${url}"${external ? ' target="_blank" rel="noopener"' : ""}>${text}</a>`;
      })
      .replace(/(^|[\s(])(https?:\/\/[^\s<)]+[^\s<).,;:!?])/g, '$1<a href="$2" target="_blank" rel="noopener">$2</a>')
      .replace(/(^|[\s(>])([\w.+-]+@[\w-]+\.[\w.]+[a-z])/gi, '$1<a href="mailto:$2">$2</a>')
      .replace(/\b(800 ?801 ?802)\b/g, '<a href="tel:+221800801802">$1</a>');

  const markdown = (text) => {
    const out = [];
    let list = null;
    escapeHtml(text)
      .split("\n")
      .forEach((line) => {
        const item = line.match(/^\s*(?:[-•*]|\d+[.)])\s+(.*)/);
        if (item) {
          (list = list || []).push(`<li>${inline(item[1])}</li>`);
          return;
        }
        if (list) {
          out.push(`<ul>${list.join("")}</ul>`);
          list = null;
        }
        if (line.trim()) out.push(`<p>${inline(line.replace(/^#+\s*/, ""))}</p>`);
      });
    if (list) out.push(`<ul>${list.join("")}</ul>`);
    return out.join("");
  };

  const scrollDown = () => {
    log.scrollTop = log.scrollHeight;
  };

  const addRow = (role, text) => {
    const row = document.createElement("div");
    row.className = `assistant-row assistant-row-${role === "user" ? "user" : "bot"}`;
    const label = document.createElement("span");
    label.className = "sr-only";
    label.textContent = `${role === "user" ? msg.msgYou : msg.msgBot} : `;
    const bubble = document.createElement("div");
    bubble.className = "assistant-bubble";
    if (text === null) {
      bubble.innerHTML = `<span class="assistant-typing"><i></i><i></i><i></i></span><span class="sr-only">${escapeHtml(msg.msgTyping)}</span>`;
    } else {
      bubble.innerHTML = markdown(text);
    }
    row.append(label, bubble);
    log.appendChild(row);
    scrollDown();
    return bubble;
  };

  const addSources = (bubble, sources) => {
    if (!sources || !sources.length) return;
    const box = document.createElement("div");
    box.className = "assistant-sources";
    const title = document.createElement("p");
    title.textContent = msg.msgSources;
    const list = document.createElement("ul");
    sources.forEach((s) => {
      if (typeof s.url !== "string" || !s.url.startsWith("/")) return;
      const li = document.createElement("li");
      const a = document.createElement("a");
      a.href = s.url;
      a.textContent = s.title;
      li.appendChild(a);
      list.appendChild(li);
    });
    box.append(title, list);
    bubble.appendChild(box);
  };

  const chips = $("[data-assistant-chips]");
  const renderHistory = () => {
    history.forEach((m) => addRow(m.role, m.content));
    if (chips) chips.hidden = history.length > 0;
  };

  /* ---------- envoi d'une question */
  const updateSend = () => {
    send.disabled = busy || !input.value.trim();
  };
  const autosize = () => {
    input.style.height = "auto";
    input.style.height = `${Math.min(input.scrollHeight, 120)}px`;
    updateSend();
  };

  const ask = async (text) => {
    const question = (text || "").trim();
    if (!question || busy) return;
    busy = true;
    if (chips) chips.hidden = true;
    history.push({ role: "user", content: question });
    addRow("user", question);
    input.value = "";
    autosize();
    const bubble = addRow("bot", null);
    let answer = "";
    controller = new AbortController();

    try {
      const response = await fetch(msg.endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: history, language: msg.lang }),
        signal: controller.signal,
        credentials: "same-origin",
      });
      if (!response.ok || !response.body) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.error || msg.msgError);
      }
      let sources = [];
      try {
        sources = JSON.parse(response.headers.get("X-Assistant-Sources") || "[]");
      } catch (e) {
        sources = [];
      }
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      for (;;) {
        const { value, done } = await reader.read();
        if (done) break;
        answer += decoder.decode(value, { stream: true });
        bubble.innerHTML = markdown(answer);
        scrollDown();
      }
      if (!answer.trim()) throw new Error(msg.msgError);
      addSources(bubble, sources);
      history.push({ role: "assistant", content: answer.trim() });
      save();
    } catch (error) {
      history.pop(); // la question sans réponse n'est pas conservée
      if (error.name === "AbortError") {
        bubble.parentElement.remove();
      } else {
        bubble.classList.add("assistant-bubble-error");
        bubble.textContent = error.message || msg.msgError;
      }
    } finally {
      busy = false;
      controller = null;
      updateSend();
      scrollDown();
    }
  };

  /* ---------- ouverture / fermeture */
  const setOpen = (open) => {
    panel.hidden = !open;
    root.classList.toggle("is-open", open);
    launcher.setAttribute("aria-expanded", String(open));
    launcherLabel.textContent = open ? msg.labelClose : msg.labelOpen;
    teaser.hidden = true;
    try {
      sessionStorage.setItem(`${STORE}-seen`, "1");
    } catch (e) {
      /* rien */
    }
    if (open) {
      scrollDown();
      input.focus();
    }
  };

  launcher.addEventListener("click", () => setOpen(panel.hidden));
  teaser.addEventListener("click", () => setOpen(true));
  $("[data-assistant-close]").addEventListener("click", () => {
    setOpen(false);
    launcher.focus();
  });
  $("[data-assistant-reset]").addEventListener("click", () => {
    if (controller) controller.abort();
    history = [];
    save();
    log.querySelectorAll(".assistant-row:not([data-assistant-welcome])").forEach((r) => r.remove());
    if (chips) chips.hidden = false;
    input.focus();
  });
  if (chips) {
    chips.addEventListener("click", (event) => {
      const chip = event.target.closest(".assistant-chip");
      if (chip) ask(chip.textContent);
    });
  }
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    ask(input.value);
  });
  input.addEventListener("input", autosize);
  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
      event.preventDefault();
      ask(input.value);
    }
  });
  panel.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      setOpen(false);
      launcher.focus();
    }
  });

  /* ---------- démarrage */
  renderHistory();
  root.hidden = false;
  let seen = false;
  try {
    seen = sessionStorage.getItem(`${STORE}-seen`) === "1";
  } catch (e) {
    seen = false;
  }
  if (!seen) {
    root.classList.add("is-new");
    window.setTimeout(() => {
      if (panel.hidden) teaser.hidden = false;
    }, 5000);
  }
})();
