/* Accueil — boutons pause/lecture des vidéos (WCAG 2.2.2) et respect de prefers-reduced-motion. */
(() => {
  const connection = navigator.connection || {};
  const reduceMotion =
    window.matchMedia("(prefers-reduced-motion: reduce)").matches || connection.saveData === true;

  const render = (toggle, video) => {
    const paused = video.paused;
    toggle.setAttribute("aria-pressed", String(paused));
    const icon = toggle.querySelector("[data-icon]");
    if (icon) icon.setAttribute("href", paused ? "#i-play" : "#i-pause");
    const text = toggle.querySelector(".sr-only");
    if (text) text.textContent = paused ? toggle.dataset.labelPlay : toggle.dataset.labelPause;
  };

  document.querySelectorAll("[data-hero-video]").forEach((video) => {
    if (reduceMotion) video.pause();
  });

  document.querySelectorAll("[data-video-toggle]").forEach((toggle) => {
    const video = toggle.dataset.videoTarget
      ? document.getElementById(toggle.dataset.videoTarget)
      : toggle.closest(".video-hero").querySelector("video");
    if (!video) return;
    if (reduceMotion) video.pause();
    render(toggle, video);
    video.addEventListener("play", () => render(toggle, video));
    video.addEventListener("pause", () => render(toggle, video));
    toggle.addEventListener("click", () => {
      if (video.paused) {
        const attempt = video.play();
        if (attempt) attempt.then(() => render(toggle, video)).catch(() => render(toggle, video));
      } else {
        video.pause();
      }
      render(toggle, video);
    });
  });
})();

/* Apparition au défilement (titre mot à mot, blocs en cascade) — désactivée si l'utilisateur
   réduit les animations ; sans JavaScript, tout reste visible. */
(() => {
  const reduce =
    window.matchMedia("(prefers-reduced-motion: reduce)").matches ||
    !("IntersectionObserver" in window);

  document.querySelectorAll("[data-reveal-words]").forEach((title) => {
    if (reduce) return;
    const words = title.textContent.trim().split(/\s+/);
    title.textContent = "";
    words.forEach((word, index) => {
      const outer = document.createElement("span");
      outer.className = "reveal-word";
      const inner = document.createElement("span");
      inner.textContent = word;
      inner.style.transitionDelay = `${index * Math.min(70, 900 / words.length)}ms`;
      outer.appendChild(inner);
      title.appendChild(outer);
      if (index < words.length - 1) title.appendChild(document.createTextNode(" "));
    });
  });

  const targets = document.querySelectorAll("[data-reveal], [data-reveal-words]");
  if (reduce) {
    targets.forEach((el) => el.classList.add("is-visible"));
    return;
  }
  document.querySelectorAll(".hm-pillars").forEach((list) => {
    list.querySelectorAll("[data-reveal]").forEach((item, index) => {
      item.style.transitionDelay = `${index * 120}ms`;
    });
  });
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    },
    { threshold: 0.15, rootMargin: "0px 0px -8% 0px" }
  );
  targets.forEach((el) => observer.observe(el));
})();
