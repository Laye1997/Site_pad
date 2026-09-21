/* Consentement (loi 2008-12 / RGPD) : aucun traceur n'est chargé avant un choix explicite. */
(() => {
  const KEY = "pad_consent";
  const banner = document.getElementById("consent-banner");
  if (!banner) return;

  const read = () => {
    try {
      return JSON.parse(localStorage.getItem(KEY));
    } catch (error) {
      return null;
    }
  };
  const save = (analytics) => {
    localStorage.setItem(KEY, JSON.stringify({ analytics, date: new Date().toISOString() }));
    banner.hidden = true;
    document.dispatchEvent(new CustomEvent("pad:consent", { detail: { analytics } }));
  };

  if (read() === null) banner.hidden = false;
  banner.querySelector("[data-consent-accept]").addEventListener("click", () => save(true));
  banner.querySelector("[data-consent-refuse]").addEventListener("click", () => save(false));
  document.querySelectorAll("[data-consent-manage]").forEach((link) => {
    link.addEventListener("click", (event) => {
      event.preventDefault();
      banner.hidden = false;
      banner.querySelector("button").focus();
    });
  });
})();
