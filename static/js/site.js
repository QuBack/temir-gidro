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

  // Hero intro (CSS) runs on every visit: a page restored by the Back button comes from the
  // back/forward cache with its animations finished, so they are played again.
  var hero = document.querySelector(".hero");
  if (hero && hero.getAnimations) {
    window.addEventListener("pageshow", function (event) {
      if (!event.persisted) return;
      hero.getAnimations({ subtree: true }).forEach(function (a) { a.cancel(); a.play(); });
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

  // Home catalog: a series card (a link to its section without JS) opens its models
  // in a panel under the card's row, one panel at a time.
  var eqGrid = document.querySelector("[data-eq-grid]");
  if (eqGrid) {
    var eqItems = eqGrid.querySelectorAll(".eq-item");
    var eqOpen = null;
    var eqReduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var eqPanels = eqGrid.querySelectorAll(".eq-panel");
    var placePanel = function (card, panel) {
      // After the last card of the row; the notch points at the card. A shown panel takes
      // a whole row and would push cards down, so the rows are read with every panel out.
      eqPanels.forEach(function (p) { p.hidden = true; });
      var top = card.parentNode.offsetTop, last = card.parentNode;
      eqItems.forEach(function (item) { if (Math.abs(item.offsetTop - top) < 4) last = item; });
      if (last.nextElementSibling !== panel) last.after(panel);
      panel.hidden = false;
      var box = card.getBoundingClientRect(), grid = eqGrid.getBoundingClientRect();
      panel.style.setProperty("--notch", (box.left - grid.left + box.width / 2) + "px");
    };
    var closePanel = function (instant) {
      if (!eqOpen) return;
      var was = eqOpen;
      eqOpen = null;
      was.card.setAttribute("aria-expanded", "false");
      was.panel.classList.remove("is-open");
      if (instant || eqReduce) was.panel.hidden = true;
      else setTimeout(function () { if (!was.panel.classList.contains("is-open")) was.panel.hidden = true; }, 400);
    };
    var openPanel = function (card) {
      var panel = document.getElementById(card.getAttribute("aria-controls"));
      // Switching groups swaps the panels at once, without a collapse in between.
      var switching = !!eqOpen;
      closePanel(true);
      panel.classList.toggle("is-instant", switching);
      placePanel(card, panel);
      void panel.offsetHeight; // commit the collapsed state, then animate open
      panel.classList.add("is-open");
      card.setAttribute("aria-expanded", "true");
      eqOpen = { card: card, panel: panel };
      requestAnimationFrame(function () { panel.classList.remove("is-instant"); });
      setTimeout(function () {
        if (eqOpen && eqOpen.panel === panel) panel.scrollIntoView({ block: "nearest", behavior: eqReduce ? "auto" : "smooth" });
      }, switching || eqReduce ? 0 : 420);
    };
    eqGrid.querySelectorAll("[data-eq-toggle]").forEach(function (card) {
      card.setAttribute("role", "button");
      card.setAttribute("aria-expanded", "false");
      card.addEventListener("click", function (event) {
        event.preventDefault();
        if (eqOpen && eqOpen.card === card) closePanel();
        else openPanel(card);
      });
      card.addEventListener("keydown", function (event) {
        if (event.key === " ") { event.preventDefault(); card.click(); }
      });
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && eqOpen) { var card = eqOpen.card; closePanel(); card.focus(); }
    });
    window.addEventListener("resize", function () { if (eqOpen) placePanel(eqOpen.card, eqOpen.panel); }, { passive: true });
  }

  // Reveal on scroll, on every page: section heads, texts, cards and list items rise
  // and fade in, photos also open from the bottom. Items that arrive together come
  // one after another. Whatever is on screen at load is left alone, so the first
  // screen never blinks; without JS, for crawlers and with reduced motion nothing
  // is hidden. Once shown, the helper classes go, so the blocks' own hover effects work.
  var REVEAL_BLOCKS = [
    "main .section-head", "main .prose", "main .split__text", "main .scene__text", "main .config__head",
    "main .config__form", "main .lead__text", "main .lead__form", "main .route", "main .waybill",
    "main .spec-table", "main .kit__options", "main .map-block__info", "main .article-cta", "main .article-related",
    "main .lift-tile", "main .eq-item", "main .cat-card", "main .feature", "main .faq__item", "main .article", "main .series__item",
    "main .reasons__list > li", "main .industries__list > li", "main .project", "main .kit__item",
    "main .stats > div", "main .steps__item", "main .contacts__list > div",
  ].join(", ");
  var REVEAL_PHOTOS = "main .scene__photo, main .eq-about__photo, main .split__main, main .kit__figure, main .sheet";
  var timeline = document.querySelector("[data-timeline]");
  if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    // Checked on scroll, not with IntersectionObserver: a fast scroll or a jump to an
    // anchor can carry a block past the screen between two frames, and it would stay
    // hidden. Here anything above the line is shown, whether on screen or passed.
    var pending = [];
    var fold = window.innerHeight;
    var mark = function (el, photo) {
      if (el.closest("[data-timeline]") || el.closest(".reveal") || el.getBoundingClientRect().top < fold) return;
      el.classList.add("reveal");
      if (photo) el.classList.add("reveal--photo");
      pending.push({ el: el, cleanup: true });
    };
    document.querySelectorAll(REVEAL_PHOTOS).forEach(function (el) { mark(el, true); });
    document.querySelectorAll(REVEAL_BLOCKS).forEach(function (el) { mark(el, false); });
    // Timeline steps keep their own styles (html.reveal-on) and only get is-visible.
    if (timeline) {
      timeline.querySelectorAll("[data-reveal]").forEach(function (el) { pending.push({ el: el, cleanup: false }); });
      document.documentElement.classList.add("reveal-on");
    }

    var revealTicking = false;
    var revealDue = function () {
      revealTicking = false;
      var line = window.innerHeight * 0.88;
      var due = pending.filter(function (p) { return p.el.getBoundingClientRect().top < line; });
      if (!due.length) return;
      pending = pending.filter(function (p) { return due.indexOf(p) < 0; });
      due.sort(function (a, b) {
        var ra = a.el.getBoundingClientRect(), rb = b.el.getBoundingClientRect();
        return ra.top - rb.top || ra.left - rb.left;
      });
      // Blocks that arrive together come one after another.
      due.forEach(function (p, i) {
        var delay = Math.min(i, 5) * 90;
        p.el.style.setProperty("--reveal-delay", delay + "ms");
        p.el.classList.add("is-visible");
        if (p.cleanup) {
          setTimeout(function () {
            p.el.classList.remove("reveal", "reveal--photo", "is-visible");
            p.el.style.removeProperty("--reveal-delay");
          }, delay + 1000);
        }
      });
    };
    revealDue();
    window.addEventListener("scroll", function () {
      if (!revealTicking) { revealTicking = true; requestAnimationFrame(revealDue); }
    }, { passive: true });
    window.addEventListener("resize", revealDue, { passive: true });
  }

  // Timeline rail: fills behind the reader.
  if (timeline && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
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

  // Timeline step with several photos: a thumbnail puts its photo into the frame. Closed, the
  // viewer focuses the photo it showed last, and the frame follows what was browsed there.
  document.querySelectorAll("[data-step-gallery]").forEach(function (gallery) {
    var shots = gallery.querySelectorAll(".timeline__shot");
    var thumbs = gallery.querySelectorAll(".timeline__thumb");
    var pick = function (i) {
      shots.forEach(function (shot, j) {
        shot.classList.toggle("is-active", j === i);
        shot.tabIndex = j === i ? 0 : -1;
      });
      thumbs.forEach(function (thumb, j) {
        if (j === i) thumb.setAttribute("aria-current", "true"); else thumb.removeAttribute("aria-current");
      });
    };
    thumbs.forEach(function (thumb, i) {
      thumb.addEventListener("click", function (event) {
        if (event.ctrlKey || event.metaKey || event.shiftKey || event.button) return; // new tab as usual
        event.preventDefault();
        pick(i);
      });
    });
    var viewer = document.querySelector("[data-lightbox]");
    if (viewer) {
      viewer.addEventListener("close", function () {
        // After lightbox.js has moved the focus back to the page.
        setTimeout(function () {
          var i = Array.prototype.indexOf.call(shots, document.activeElement);
          if (i >= 0) pick(i);
        });
      });
    }
  });

  // Photo strips: the arrows move one screenful of the strip; at either end the arrow hides.
  // Without JS the strip still scrolls sideways by swipe or trackpad.
  document.querySelectorAll("[data-carousel]").forEach(function (carousel) {
    var track = carousel.querySelector("[data-carousel-track]");
    var prev = carousel.querySelector("[data-carousel-prev]");
    var next = carousel.querySelector("[data-carousel-next]");
    var sync = function () {
      var end = track.scrollWidth - track.clientWidth;
      prev.disabled = track.scrollLeft <= 1;
      next.disabled = track.scrollLeft >= end - 1;
    };
    var step = function (dir) {
      var item = track.firstElementChild;
      var gap = parseFloat(getComputedStyle(track).columnGap) || 0;
      var size = item ? item.getBoundingClientRect().width + gap : track.clientWidth;
      var perView = Math.max(1, Math.floor((track.clientWidth + gap) / size));
      track.scrollBy({ left: dir * perView * size });
    };
    prev.hidden = next.hidden = false;
    prev.addEventListener("click", function () { step(-1); });
    next.addEventListener("click", function () { step(1); });
    track.addEventListener("scroll", sync, { passive: true });
    window.addEventListener("resize", sync, { passive: true });
    sync();
  });

  // Other views on a product's first screen: a small picture puts its view on the stage in place
  // of the render. Nothing opens full size there.
  document.querySelectorAll("[data-hero-views]").forEach(function (list) {
    var slides = list.parentElement.querySelectorAll("[data-hero-slide]");
    var items = list.querySelectorAll(".hero-views__item");
    items.forEach(function (item, i) {
      item.addEventListener("click", function () {
        slides.forEach(function (slide, j) { slide.hidden = j !== i; });
        items.forEach(function (other, j) {
          other.classList.toggle("is-active", j === i);
          other.setAttribute("aria-pressed", j === i ? "true" : "false");
        });
      });
    });
  });
})();
