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
    // The first section slides up under the top bar and header by --chrome; CSS has
    // an estimate, here it becomes the exact height, so no strip of page shows above.
    var topbar = document.querySelector(".topbar");
    var syncChrome = function () {
      var height = header.offsetHeight + (topbar ? topbar.offsetHeight : 0);
      document.documentElement.style.setProperty("--chrome", height + "px");
    };
    syncChrome();
    window.addEventListener("resize", syncChrome, { passive: true });

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

  // Counters: numbers in [data-count] run up from zero once scrolled into view. The final
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
      // The final value stays in place until the first frame actually runs: a page
      // rendered without animation frames (a crawler, a hidden tab) never shows zeros.
      var delay = 150 + i * 120, duration = 1400, begin = null;
      var step = function (now) {
        if (begin === null) begin = now;
        var t = Math.min(1, (now - begin) / duration);
        var eased = 1 - Math.pow(2, -10 * t); // fast start, soft landing
        el.textContent = (t < 1 ? Math.round(target * eased) : target) + suffix;
        if (t < 1) requestAnimationFrame(step);
        else el.style.minWidth = "";
      };
      var start = function () { setTimeout(function () { requestAnimationFrame(step); }, delay); };
      if (!("IntersectionObserver" in window)) return start();
      var io = new IntersectionObserver(function (entries) {
        if (entries[0].isIntersecting) { io.disconnect(); start(); }
      }, { threshold: 0.5 });
      io.observe(el);
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

  // Timeline: each step comes up as it scrolls in, the rail fills behind the reader.
  // The steps are hidden only once this runs (html.reveal-on), so without JS, for
  // crawlers and with reduced motion everything is simply shown.
  var timeline = document.querySelector("[data-timeline]");
  if (timeline && "IntersectionObserver" in window &&
      !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    var steps = timeline.querySelectorAll("[data-reveal]");
    var reveal = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          reveal.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -20% 0px", threshold: 0.2 });
    steps.forEach(function (step) { reveal.observe(step); });
    document.documentElement.classList.add("reveal-on");

    // Rail fill: how far a line at 60% of the screen has gone down the timeline;
    // a step's dot turns red when the fill reaches it.
    var dots = timeline.querySelectorAll(".timeline__dot");
    var railTicking = false;
    var syncRail = function () {
      railTicking = false;
      var line = window.innerHeight * 0.6;
      var box = timeline.getBoundingClientRect();
      var reached = (line - box.top) / box.height;
      timeline.style.setProperty("--progress", Math.min(1, Math.max(0, reached)).toFixed(3));
      dots.forEach(function (dot) {
        var d = dot.getBoundingClientRect();
        dot.classList.toggle("is-reached", d.top + d.height / 2 <= line);
      });
    };
    syncRail();
    window.addEventListener("scroll", function () {
      if (!railTicking) { railTicking = true; requestAnimationFrame(syncRail); }
    }, { passive: true });
    window.addEventListener("resize", syncRail, { passive: true });
  }
})();
