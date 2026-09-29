// Yandex.Metrika, loaded after the page has finished loading so it never
// competes with the main content for bandwidth (LCP / INP).
(function () {
  "use strict";
  var script = document.currentScript;
  var id = Number(script && script.dataset.counterId);
  if (!id) return;

  window.ym = window.ym || function () { (window.ym.a = window.ym.a || []).push(arguments); };
  window.ym.l = Date.now();
  window.ym(id, "init", {
    clickmap: true,
    trackLinks: true,
    accurateTrackBounce: true,
    webvisor: false,
  });

  window.temirGoal = function (goal) { window.ym(id, "reachGoal", goal); };

  document.addEventListener("click", function (event) {
    var link = event.target.closest && event.target.closest('a[href^="tel:"], a[href^="mailto:"]');
    if (link) window.temirGoal(link.href.indexOf("tel:") === 0 ? "phone_click" : "email_click");
  });

  function load() {
    var tag = document.createElement("script");
    tag.async = true;
    tag.src = "https://mc.yandex.ru/metrika/tag.js";
    document.head.appendChild(tag);
  }
  if (document.readyState === "complete") load();
  else window.addEventListener("load", load);
})();
