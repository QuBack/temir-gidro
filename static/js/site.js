// Progressive enhancements only: the site works without this file.
(function () {
  "use strict";

  // Mobile menu. Without JS the toggle is a plain link to the footer navigation.
  var toggle = document.querySelector("[data-nav-toggle]");
  var header = document.querySelector("[data-header]");
  if (toggle && header) {
    toggle.setAttribute("role", "button");
    toggle.addEventListener("click", function (event) {
      event.preventDefault();
      var open = header.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", String(open));
    });
  }

  // Hero video: starts after the page (and the LCP poster) has loaded.
  var video = document.querySelector("[data-hero-video]");
  if (video) {
    var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var saveData = navigator.connection && navigator.connection.saveData;
    if (!reduceMotion && !saveData) {
      var start = function () {
        video.preload = "auto";
        video.addEventListener("playing", function () { video.classList.add("is-playing"); }, { once: true });
        var played = video.play();
        if (played && played.catch) played.catch(function () {});
      };
      if (document.readyState === "complete") start();
      else window.addEventListener("load", start, { once: true });
    }
  }
})();
