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

  // Pages with body.overlay start with a transparent header over the first
  // section. It fills in gradually over the first ~140px of scroll: CSS blends
  // background, text and logo from --scroll-solid (0…1).
  if (header && document.body.classList.contains("overlay")) {
    var ticking = false;
    var syncHeader = function () {
      ticking = false;
      var solid = Math.min(1, Math.max(0, window.scrollY / 140));
      header.style.setProperty("--scroll-solid", solid.toFixed(3));
    };
    syncHeader();
    window.addEventListener("scroll", function () {
      if (!ticking) { ticking = true; requestAnimationFrame(syncHeader); }
    }, { passive: true });
  }

  // Counters: numbers in [data-count] run up from zero once on load. The final
  // value is already in the HTML, so search engines and no-JS visitors get it as is.
  var counters = document.querySelectorAll("[data-count]");
  if (counters.length && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    counters.forEach(function (el, i) {
      var match = el.textContent.trim().match(/^(\d+)(.*)$/);
      if (!match) return;
      var target = parseInt(match[1], 10), suffix = match[2];
      // Reserve the final width (in digit widths, not pixels, so it survives a resize)
      // while the digits grow; released when the count is done.
      el.style.minWidth = (target + suffix).length + "ch";
      el.textContent = "0" + suffix;
      var delay = 350 + i * 120, duration = 1400, begin = null;
      var step = function (now) {
        if (begin === null) begin = now;
        var t = Math.min(1, (now - begin) / duration);
        var eased = 1 - Math.pow(2, -10 * t); // fast start, soft landing
        el.textContent = (t < 1 ? Math.round(target * eased) : target) + suffix;
        if (t < 1) requestAnimationFrame(step);
        else el.style.minWidth = "";
      };
      setTimeout(function () { requestAnimationFrame(step); }, delay);
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
