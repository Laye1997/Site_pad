/* Écran de chargement : masqué dès que la page est prête (ou après 2,5 s au plus tard),
   jamais affiché sans JavaScript ni si l'utilisateur réduit les animations.
   L'attribut HTML `hidden` (pas une classe CSS) garde l'élément invisible dès le premier octet
   du document, sans dépendre du chargement du fichier CSS externe : c'est lui qui évitait un
   bref affichage sans style (logo en taille normale, hors de sa mise en page) avant que la
   feuille de styles ne soit appliquée. */
(() => {
  const el = document.getElementById("preloader");
  if (!el) return;

  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    el.remove();
    return;
  }

  el.hidden = false;

  let hidden = false;
  const hide = () => {
    if (hidden) return;
    hidden = true;
    el.classList.add("is-hidden");
    el.addEventListener("transitionend", () => el.remove(), { once: true });
  };

  if (document.readyState === "complete") hide();
  else window.addEventListener("load", hide, { once: true });
  setTimeout(hide, 2500);
})();
