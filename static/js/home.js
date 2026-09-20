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
