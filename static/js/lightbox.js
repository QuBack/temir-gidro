// Full-screen photo viewer. A photo opts in by being wrapped in
// <a href="<largest image>" data-zoom="<group>">: without JS the link just opens
// the picture. Photos of one group (a page's scenes, a model's views) are browsed
// with the arrows, the thumbnails, the keyboard or a swipe; a swipe down closes.
// The dialog markup is server-rendered (includes/lightbox.html).
(function () {
  "use strict";

  var dialog = document.querySelector("[data-lightbox]");
  var links = document.querySelectorAll("a[data-zoom]");
  if (!dialog || !links.length || typeof dialog.showModal !== "function") return;

  var stage = dialog.querySelector("[data-lightbox-stage]");
  var image = dialog.querySelector("[data-lightbox-img]");
  var spinner = dialog.querySelector("[data-lightbox-spinner]");
  var caption = dialog.querySelector("[data-lightbox-caption]");
  var count = dialog.querySelector("[data-lightbox-count]");
  var strip = dialog.querySelector("[data-lightbox-thumbs]");
  var prev = dialog.querySelector("[data-lightbox-prev]");
  var next = dialog.querySelector("[data-lightbox-next]");
  var motion = !window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var group = [];
  var index = 0;
  var closing = false;

  function thumbOf(link) { return link.querySelector("img"); }

  // Fly between the thumbnail on the page and the picture in the viewer (FLIP).
  function flight(from, reverse) {
    if (!motion || !from || !image.animate) return null;
    var a = from.getBoundingClientRect();
    var b = image.getBoundingClientRect();
    if (!a.width || !b.width || a.bottom < 0 || a.top > innerHeight) return null;
    var dx = a.left + a.width / 2 - (b.left + b.width / 2);
    var dy = a.top + a.height / 2 - (b.top + b.height / 2);
    var s = Math.max(a.width / b.width, a.height / b.height);
    var frames = [{ transform: "translate(" + dx + "px," + dy + "px) scale(" + s + ")", opacity: .6 }, { transform: "none", opacity: 1 }];
    return image.animate(reverse ? frames.reverse() : frames, { duration: 320, easing: "cubic-bezier(.2,.7,.2,1)", fill: "both" });
  }

  function load(link, direction) {
    var thumb = thumbOf(link);
    var full = link.href;
    // The thumbnail is already in the browser: show it at once, swap in the large file when it arrives.
    image.src = thumb && thumb.currentSrc ? thumb.currentSrc : full;
    image.alt = thumb ? thumb.alt : "";
    if (image.src !== full) {
      spinner.hidden = false;
      var big = new Image();
      big.onload = big.onerror = function () {
        if (group[index] !== link) return;
        spinner.hidden = true;
        if (big.naturalWidth) image.src = full;
      };
      big.src = full;
    }
    if (direction && motion && image.animate) {
      image.animate([{ transform: "translateX(" + direction * 3 + "rem)", opacity: 0 }, { transform: "none", opacity: 1 }],
        { duration: 260, easing: "cubic-bezier(.2,.7,.2,1)" });
    }
  }

  function show(i, direction) {
    index = (i + group.length) % group.length;
    var link = group[index];
    load(link, direction);
    caption.textContent = image.alt;
    var many = group.length > 1;
    prev.hidden = next.hidden = count.hidden = strip.hidden = !many;
    count.textContent = (index + 1) + " / " + group.length;
    Array.prototype.forEach.call(strip.children, function (b, j) {
      b.classList.toggle("is-active", j === index);
      if (j === index) b.setAttribute("aria-current", "true"); else b.removeAttribute("aria-current");
    });
    var active = strip.children[index];
    if (active && many) active.scrollIntoView({ block: "nearest", inline: "center" });
    // Neighbours load in the background, so the arrows feel instant.
    if (many) [index + 1, index - 1].forEach(function (j) { new Image().src = group[(j + group.length) % group.length].href; });
  }

  function buildStrip() {
    strip.textContent = "";
    if (group.length < 2) return;
    group.forEach(function (link, j) {
      var thumb = thumbOf(link);
      var b = document.createElement("button");
      b.type = "button";
      b.className = "lightbox__thumb";
      b.setAttribute("aria-label", (j + 1) + ": " + (thumb ? thumb.alt : ""));
      var img = document.createElement("img");
      img.src = thumb && thumb.currentSrc ? thumb.currentSrc : link.href;
      img.alt = "";
      b.appendChild(img);
      b.addEventListener("click", function () { if (j !== index) show(j, j > index ? 1 : -1); });
      strip.appendChild(b);
    });
  }

  // Lock the page under the viewer without making it jump sideways when its scrollbar goes.
  function lock(on) {
    var root = document.documentElement;
    if (on) {
      root.style.setProperty("--scrollbar", (innerWidth - root.clientWidth) + "px");
      root.classList.add("lightbox-open");
    } else {
      root.classList.remove("lightbox-open");
      root.style.removeProperty("--scrollbar");
    }
  }

  function open(link) {
    group = Array.prototype.filter.call(links, function (l) { return l.dataset.zoom === link.dataset.zoom; });
    buildStrip();
    lock(true);
    dialog.showModal();
    dialog.classList.add("is-open");
    show(group.indexOf(link));
    flight(thumbOf(link), false);
  }

  function close() {
    if (closing || !dialog.open) return;
    closing = true;
    dialog.classList.remove("is-open");
    var anim = flight(thumbOf(group[index]), true);
    var done = function () { closing = false; dialog.close(); };
    if (anim) anim.onfinish = done; else setTimeout(done, motion ? 200 : 0);
  }

  links.forEach(function (link) {
    link.addEventListener("click", function (event) {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.button) return; // new tab as usual
      event.preventDefault();
      open(link);
    });
  });

  prev.addEventListener("click", function () { show(index - 1, -1); });
  next.addEventListener("click", function () { show(index + 1, 1); });
  dialog.querySelector("[data-lightbox-close]").addEventListener("click", close);
  dialog.addEventListener("cancel", function (event) { event.preventDefault(); close(); }); // Esc
  dialog.addEventListener("keydown", function (event) {
    if (group.length < 2) return;
    if (event.key === "ArrowLeft") show(index - 1, -1);
    else if (event.key === "ArrowRight") show(index + 1, 1);
    else if (event.key === "Home") show(0, -1);
    else if (event.key === "End") show(group.length - 1, 1);
  });
  dialog.addEventListener("close", function () {
    lock(false);
    image.getAnimations && image.getAnimations().forEach(function (a) { a.cancel(); });
    image.removeAttribute("src");
    var link = group[index];
    if (link) link.focus({ preventScroll: true });
  });

  // Drag: sideways browses, down closes; a tap on the dark area around the photo closes too.
  var drag = null;
  stage.addEventListener("pointerdown", function (event) {
    if (event.button) return;
    drag = { x: event.clientX, y: event.clientY, dx: 0, dy: 0, id: event.pointerId };
  });
  stage.addEventListener("pointermove", function (event) {
    if (!drag || event.pointerId !== drag.id) return;
    drag.dx = event.clientX - drag.x;
    drag.dy = event.clientY - drag.y;
    if (Math.abs(drag.dx) > 6 || Math.abs(drag.dy) > 6) {
      if (!drag.moved) { drag.moved = true; stage.setPointerCapture(drag.id); }
      var down = Math.max(drag.dy, 0);
      var sideways = Math.abs(drag.dx) > down;
      image.style.transition = "none";
      image.style.transform = sideways && group.length > 1 ? "translateX(" + drag.dx + "px)" : "translateY(" + down + "px)";
      dialog.style.setProperty("--fade", sideways ? 1 : Math.max(.35, 1 - down / 400));
    }
  });
  function release(event) {
    if (!drag || event.pointerId !== drag.id) return;
    var d = drag;
    drag = null;
    image.style.transition = "";
    image.style.transform = "";
    dialog.style.removeProperty("--fade");
    if (!d.moved) {
      if (event.type === "pointerup" && event.target !== image) close();
      return;
    }
    if (Math.abs(d.dx) > Math.max(d.dy, 0)) {
      if (group.length > 1 && Math.abs(d.dx) > 60) show(index + (d.dx < 0 ? 1 : -1), d.dx < 0 ? 1 : -1);
    } else if (d.dy > 90) {
      close();
    }
  }
  stage.addEventListener("pointerup", release);
  stage.addEventListener("pointercancel", release);
})();
