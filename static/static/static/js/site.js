/* Menu principal — amélioration progressive (le menu reste visible sans JS). */
(() => {
  document.documentElement.classList.add("js");
  const toggle = document.querySelector(".nav-toggle");
  const nav = document.querySelector("#primary-nav");
  if (!toggle || !nav) return;

  const desktop = window.matchMedia("(min-width: 1025px)");
  const label = toggle.querySelector(".sr-only");
  const labels = { open: toggle.dataset.labelOpen, close: toggle.dataset.labelClose };

  const setOpen = (open) => {
    nav.hidden = !open;
    toggle.setAttribute("aria-expanded", String(open));
    if (label) label.textContent = open ? labels.close : labels.open;
  };
  const closeGroups = (except) => {
    nav.querySelectorAll("details[open]").forEach((item) => {
      if (item !== except) item.removeAttribute("open");
    });
  };

  setOpen(desktop.matches);

  toggle.addEventListener("click", () => {
    const open = toggle.getAttribute("aria-expanded") !== "true";
    setOpen(open);
    if (open) nav.querySelector("summary")?.focus();
  });

  nav.addEventListener("click", (event) => {
    const summary = event.target.closest("summary");
    if (summary) closeGroups(summary.parentElement);
  });

  nav.querySelectorAll(".nav-group").forEach((group) => {
    group.addEventListener("mouseenter", () => {
      if (!desktop.matches) return;
      closeGroups(group);
      group.open = true;
    });
    group.addEventListener("mouseleave", () => {
      if (desktop.matches && !group.contains(document.activeElement)) group.open = false;
    });
    group.addEventListener("focusout", (event) => {
      if (desktop.matches && !group.contains(event.relatedTarget)) group.open = false;
    });
  });

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    const openGroup = nav.querySelector("details[open]");
    if (openGroup) {
      openGroup.removeAttribute("open");
      openGroup.querySelector("summary").focus();
      return;
    }
    if (!desktop.matches && toggle.getAttribute("aria-expanded") === "true") {
      setOpen(false);
      toggle.focus();
    }
  });

  desktop.addEventListener("change", (event) => setOpen(event.matches));
})();
