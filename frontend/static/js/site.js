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

/* Galerie photo en carrousel : défilement automatique (une photo à la fois), navigation au
   clavier/tactile native (scroll-snap), pause au survol/focus et respect du mouvement réduit. */
(() => {
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  document.querySelectorAll("[data-photo-carousel]").forEach((carousel) => {
    const track = carousel.querySelector("[data-carousel-track]");
    const items = track ? Array.from(track.children) : [];
    const status = carousel.querySelector("[data-carousel-status]");
    const prev = carousel.querySelector("[data-carousel-prev]");
    const next = carousel.querySelector("[data-carousel-next]");
    if (!track || items.length < 2) return;

    let index = 0;
    let timer = null;

    const announce = () => {
      if (status) status.textContent = `${index + 1} / ${items.length}`;
    };

    const goTo = (target) => {
      index = (target + items.length) % items.length;
      items[index].scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", inline: "start", block: "nearest" });
      announce();
    };

    const start = () => {
      if (reduceMotion || timer) return;
      timer = window.setInterval(() => goTo(index + 1), 4000);
    };
    const stop = () => {
      window.clearInterval(timer);
      timer = null;
    };

    prev?.addEventListener("click", () => {
      stop();
      goTo(index - 1);
    });
    next?.addEventListener("click", () => {
      stop();
      goTo(index + 1);
    });
    carousel.addEventListener("mouseenter", stop);
    carousel.addEventListener("mouseleave", start);
    carousel.addEventListener("focusin", stop);
    carousel.addEventListener("focusout", stop);

    let scrollTimeout;
    track.addEventListener("scroll", () => {
      stop();
      window.clearTimeout(scrollTimeout);
      scrollTimeout = window.setTimeout(() => {
        const nearest = items.reduce((best, item, i) => {
          const d = Math.abs(item.offsetLeft - track.scrollLeft);
          return d < best.d ? { i, d } : best;
        }, { i: 0, d: Infinity }).i;
        index = nearest;
        announce();
      }, 150);
    });

    announce();
    start();
  });
})();

/* Bandeau de campagne (ex. Octobre Rose) : fermeture mémorisée, pas de traceur. */
(() => {
  const KEY = "pad_campaign_dismissed";
  const banner = document.getElementById("campaign-banner");
  if (!banner) return;

  let dismissed = false;
  try {
    dismissed = localStorage.getItem(KEY) === "1";
  } catch (error) {
    dismissed = false;
  }
  if (!dismissed) banner.hidden = false;

  banner.querySelector("[data-campaign-dismiss]").addEventListener("click", () => {
    banner.hidden = true;
    try {
      localStorage.setItem(KEY, "1");
    } catch (error) {
      /* stockage indisponible (navigation privée) : le bandeau reviendra à la prochaine page */
    }
  });
})();
