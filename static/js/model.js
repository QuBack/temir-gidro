// Model page: kit callouts, request sliders. All content is
// server-rendered; this file only adds interaction.
(function () {
  "use strict";

  // ---------- Console chains (kit tab): the photo opens once it comes into view, then drifts with the scroll ----------
  var chains = document.querySelector("[data-chains]");
  if (chains && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    if ("IntersectionObserver" in window) {
      // It sits in the kit tab, hidden at first: a hidden block never intersects, so it opens
      // when that tab is shown (or, on a page opened at the tab, once its top is on screen).
      chains.classList.add("is-pending");
      new IntersectionObserver(function (entries, io) {
        if (!entries[0].isIntersecting) return;
        chains.classList.remove("is-pending");
        io.disconnect();
      }, { rootMargin: "0px 0px -10% 0px" }).observe(chains);
    }
    var img = chains.querySelector(".chains__photo img");
    var drift = function () {
      var r = chains.getBoundingClientRect();
      var t = Math.max(-1, Math.min(1, (r.top + r.height / 2 - window.innerHeight / 2) / window.innerHeight));
      img.style.setProperty("--drift", (t * 6).toFixed(2) + "%");
    };
    window.addEventListener("scroll", drift, { passive: true });
    drift();
  }

  // ---------- Under the chains photo: the headline rising word by word, and the drive on a drawing sheet ----------
  var still = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var canWatch = "IntersectionObserver" in window && !still;
  // Runs fn once the element is on screen; the kit tab is hidden at first, and hidden never intersects.
  var whenSeen = function (el, fn) {
    new IntersectionObserver(function (entries, io) {
      if (!entries[0].isIntersecting) return;
      io.disconnect();
      fn();
    }, { rootMargin: "0px 0px -15% 0px" }).observe(el);
  };

  var strike = document.querySelector("[data-chains-strike]");
  if (strike && canWatch) {
    // Words rise one after another, so each gets its own clipping box.
    var words = strike.querySelector(".chains-strike__new");
    var text = words.textContent.trim().split(/\s+/);
    words.textContent = "";
    text.forEach(function (w, i) {
      var box = document.createElement("span"), word = document.createElement("i");
      box.className = "chains-strike__w";
      word.textContent = w;
      word.style.transitionDelay = (0.15 + i * 0.12) + "s";
      box.appendChild(word);
      words.appendChild(box);
      words.appendChild(document.createTextNode(" "));
    });
    strike.classList.add("is-pending");
    whenSeen(strike, function () { strike.classList.remove("is-pending"); });
  }

  var sheet = document.querySelector("[data-chains-sheet]");
  if (sheet) drawDrive(sheet);

  // The drive as on the lift: two double sprockets on a head that the cylinder rod pushes up; over
  // each runs a double-row chain, its inner end pinned to a beam by the cylinder, the outer one holding
  // the carriage. The rod moves h, the carriage 2h; the chain runs over the teeth as the head rises.
  function drawDrive(sheet) {
    var svg = sheet.querySelector("svg");
    var NS = "http://www.w3.org/2000/svg";
    var el = function (name, attrs, parent) {
      var n = document.createElementNS(NS, name);
      for (var k in attrs) n.setAttribute(k, attrs[k]);
      (parent || svg).appendChild(n);
      return n;
    };
    var INK = "#22282b", RED = "#c4161c", PAPER = "#f7f8f7", STEEL = "#8d979b";

    // Geometry (svg units). The head sits at HEAD0 with the rod in; H is the full stroke, read as 1 m.
    var CX = 240, GAP = 110, R = 38, N = 14, STEP = 2 * Math.PI / N, P = R * STEP;
    var BASE = 405, ANCHOR = 300, HEAD0 = 118, CAR0 = 326, CAR_H = 68, H = 60;
    var DX = 11, DY = -8;  // the second row of the chain and the second ring of the sprocket, set back

    // Paper: guide rails of the mast, the base with hatching, the centre line.
    var frame = el("g", { stroke: INK, fill: "none" });
    [34, 446].forEach(function (x) {
      el("line", { x1: x, y1: -30, x2: x, y2: BASE, "stroke-width": 1.4 }, frame);
      el("line", { x1: x + (x < CX ? 8 : -8), y1: -30, x2: x + (x < CX ? 8 : -8), y2: BASE, "stroke-width": .8 }, frame);
    });
    el("line", { x1: 20, y1: BASE, x2: 460, y2: BASE, "stroke-width": 1.6 }, frame);
    for (var hx = 24; hx < 460; hx += 12) el("line", { x1: hx, y1: BASE + 1, x2: hx - 9, y2: BASE + 10, "stroke-width": .7 }, frame);
    el("line", { x1: CX, y1: -36, x2: CX, y2: BASE + 18, stroke: INK, "stroke-width": .7, "stroke-dasharray": "14 3 2 3" });

    // The carriage, behind everything: it rides on the rails, the outer chain ends hold it.
    var car = el("g");
    el("rect", { x: 52, width: 376, height: CAR_H, fill: "#e9ecea", stroke: INK, "stroke-width": 1.6 }, car);
    var carHatch = el("g", { stroke: INK, "stroke-width": .5, opacity: .35, "clip-path": "url(#chains-car-clip)" }, car);
    for (var c = 0; c < 40; c++) el("line", { x1: 52 + c * 12, y1: 0, x2: 52 + c * 12 - CAR_H, y2: CAR_H }, carHatch);
    el("rect", { x: 52, width: 376, height: CAR_H }, el("clipPath", { id: "chains-car-clip" }, el("defs")));
    var carEars = [-1, 1].map(function (sign) {
      return el("rect", { x: CX + sign * (GAP + R) - 9, width: 18, fill: STEEL, stroke: INK, "stroke-width": 1.2 }, car);
    });

    // Cylinder: the body stands on the base, the rod pushes the head.
    var rod = el("rect", { x: CX - 7, width: 14, fill: "#e6eaec", stroke: INK, "stroke-width": 1.3 });
    var rodShine = el("line", { x1: CX - 2, x2: CX - 2, y2: 262, stroke: "#fff", "stroke-width": 2 });
    el("rect", { x: CX - 17, y: 268, width: 34, height: BASE - 268, fill: "#5b6468", stroke: INK, "stroke-width": 1.6 });
    el("rect", { x: CX - 21, y: 264, width: 42, height: 12, fill: "#5b6468", stroke: INK, "stroke-width": 1.4 });
    el("rect", { x: CX - 21, y: BASE - 12, width: 42, height: 12, fill: "#5b6468", stroke: INK, "stroke-width": 1.4 });

    // The head (traverse) on the rod.
    var head = el("g");
    el("rect", { x: CX - GAP - R - 14, y: -9, width: 2 * (GAP + R + 14), height: 18, fill: STEEL, stroke: INK, "stroke-width": 1.6 }, head);

    // The inner chain ends: pinned in lugs on a beam of the mast that the cylinder is clamped to.
    el("rect", { x: CX - GAP + R - 16, y: ANCHOR + 6, width: 2 * (GAP - R + 16), height: 12, fill: STEEL, stroke: INK, "stroke-width": 1.4 });
    el("rect", { x: CX - 21, y: ANCHOR + 2, width: 42, height: 20, rx: 6, fill: "none", stroke: INK, "stroke-width": 2.4 });
    [-1, 1].forEach(function (sign) {
      var x = CX + sign * (GAP - R);
      el("path", { d: "M" + (x - 9) + " " + (ANCHOR + 7) + " V" + (ANCHOR - 4) + " A9 9 0 0 1 " + (x + 9) + " " + (ANCHOR - 4) +
        " V" + (ANCHOR + 7) + " Z", fill: STEEL, stroke: INK, "stroke-width": 1.3 });
    });

    var gearPath = (function () {
      var d = "", pt = function (a, r) { return [r * Math.cos(a), -r * Math.sin(a)]; };
      for (var j = 0; j < N; j++) {
        var a = j * STEP;
        [[a - .2 * STEP, R - 3], [a, R - 6], [a + .2 * STEP, R - 3], [a + .38 * STEP, R + 10], [a + .62 * STEP, R + 10]]
          .forEach(function (q, k) { var xy = pt(q[0], q[1]); d += (j || k ? "L" : "M") + xy[0].toFixed(2) + " " + xy[1].toFixed(2); });
      }
      return d + "Z";
    })();
    // A link plate one pitch long along x: round ends around the pins, a waist between them.
    var linkPath = function (r) {
      var w = .24 * r;
      return "M0 " + (-r) + "A" + r + " " + r + " 0 0 0 0 " + r + "Q" + P / 2 + " " + w + " " + P + " " + r +
        "A" + r + " " + r + " 0 0 0 " + P + " " + (-r) + "Q" + P / 2 + " " + (-w) + " 0 " + (-r) + "Z";
    };
    var LINK_OUT = linkPath(.44 * P), LINK_IN = linkPath(.37 * P);
    var hexPath = function (r) {
      var d = "";
      for (var k = 0; k < 6; k++) d += (k ? "L" : "M") + (r * Math.cos(k * Math.PI / 3)).toFixed(2) + " " + (r * Math.sin(k * Math.PI / 3)).toFixed(2);
      return d + "Z";
    };
    // The chain is laid by length from its pinned end, so as the head rises it runs over the sprocket by itself.
    var S00 = ANCHOR - HEAD0, LENGTH = S00 + Math.PI * R + (CAR0 - HEAD0);
    var COUNT = Math.floor(LENGTH / P);
    // It ends on a whole link, a little above the carriage: the ears reach up to the last pin.
    var short = LENGTH - COUNT * P;
    carEars.forEach(function (ear) { ear.setAttribute("y", -short - 6); ear.setAttribute("height", short + 20); });

    // One side: a double sprocket and a double-row chain over it; sign -1 is the left one.
    var sides = [-1, 1].map(function (sign) {
      var gx = CX + sign * GAP, xi = gx - sign * R, xo = gx + sign * R;
      var back = el("g", { "class": "chains-sheet__back" });
      var pins = el("g");
      var row = el("g", { id: "chains-row" + sign });
      // The chain lies over the sprocket, the teeth between its rollers.
      var gear = el("g", {}, row), inner = el("g", {}, row), outer = el("g", {}, row), heads = el("g", {}, row);
      el("path", { d: gearPath, fill: RED, stroke: INK, "stroke-width": 1.6, "stroke-linejoin": "round" }, gear);
      el("circle", { r: R - 22, fill: "none", stroke: INK, "stroke-width": 1.1 }, gear);
      el("path", { d: hexPath(10), fill: "#cfd5d7", stroke: INK, "stroke-width": 1.4, "stroke-linejoin": "round" }, gear);
      el("circle", { r: 4, fill: "#9aa3a6", stroke: INK, "stroke-width": 1 }, gear);
      for (var b = 0; b < 5; b++) {
        var a = b * 2 * Math.PI / 5;
        el("circle", { cx: 21 * Math.cos(a), cy: 21 * Math.sin(a), r: 3.6, fill: PAPER, stroke: INK, "stroke-width": 1.1 }, gear);
      }
      // The second row: the same sprocket and chain once more, set back and darker.
      el("use", { href: "#chains-row" + sign, transform: "translate(" + DX + " " + DY + ")" }, back);
      var axle = el("line", { stroke: INK, "stroke-width": 16, "stroke-linecap": "round" });
      svg.insertBefore(axle, pins);
      // Links: figure-eight plates from pin to pin, inner and outer ones in turn (outer on top),
      // a pin head at every joint and a pin across to the second row.
      var joints = [];
      for (var i = 0; i <= COUNT; i++) {
        var j = {};
        if (i) j.link = el("path", i % 2 ? { d: LINK_IN, fill: "#9aa3a6", stroke: INK, "stroke-width": 1.2 }
                                        : { d: LINK_OUT, fill: "#6b7478", stroke: INK, "stroke-width": 1.3 }, i % 2 ? inner : outer);
        j.pin = el("line", { stroke: INK, "stroke-width": 5, "stroke-linecap": "round" }, pins);
        j.head = el("circle", { r: 2.6, fill: "#d9dedf", stroke: INK, "stroke-width": 1 }, heads);
        joints.push(j);
      }
      // Where the chain is, s units from its pinned end, with the head at ty.
      var at = function (s, ty) {
        var s0 = ANCHOR - ty;
        if (s <= s0) return [xi, ANCHOR - s];
        var t = (s - s0) / R;
        if (t <= Math.PI) return [gx - sign * R * Math.cos(t), ty - R * Math.sin(t)];
        return [xo, ty + (s - s0 - Math.PI * R)];
      };
      // Teeth phase: the gaps fall where the rollers sit.
      var phase = (sign < 0 ? -S00 / R : Math.PI + S00 / R) * 180 / Math.PI;
      var update = function (h) {
        var ty = HEAD0 - h;
        // Rolling: the inner side stays put, so the sprocket turns by h / R (the left one clockwise).
        var turn = -sign * (h / R) * 180 / Math.PI;
        gear.setAttribute("transform", "translate(" + gx + " " + ty + ") rotate(" + (turn - phase) + ")");
        axle.setAttribute("x1", gx); axle.setAttribute("y1", ty); axle.setAttribute("x2", gx + DX); axle.setAttribute("y2", ty + DY);
        var prev = null;
        joints.forEach(function (j, i) {
          var xy = at(i * P, ty);
          j.head.setAttribute("cx", xy[0]); j.head.setAttribute("cy", xy[1]);
          j.pin.setAttribute("x1", xy[0]); j.pin.setAttribute("y1", xy[1]);
          j.pin.setAttribute("x2", xy[0] + DX); j.pin.setAttribute("y2", xy[1] + DY);
          if (prev) {
            var dx = xy[0] - prev[0], dy = xy[1] - prev[1];
            j.link.setAttribute("transform", "translate(" + prev[0] + " " + prev[1] + ") rotate(" + Math.atan2(dy, dx) * 180 / Math.PI +
              ") scale(" + Math.hypot(dx, dy) / P + " 1)");
          }
          prev = xy;
        });
      };
      return { update: update, gx: gx, xo: xo };
    });

    // Dimensions on the right: the rod's h and the carriage's 2h, from where they start.
    var dims = el("g", { stroke: INK, "stroke-width": .9, fill: "none" });
    el("line", { x1: CX + GAP + R + 14, y1: HEAD0, x2: 488, y2: HEAD0, "stroke-dasharray": "4 3" }, dims);
    el("line", { x1: 428, y1: CAR0, x2: 512, y2: CAR0, "stroke-dasharray": "4 3" }, dims);
    var dimRod = el("line", { x1: 480, x2: 480, y1: HEAD0 }, dims);
    var dimCar = el("line", { x1: 504, x2: 504, y1: CAR0 }, dims);
    var extHead = el("line", { x1: CX + GAP + R + 14, x2: 488 }, dims);
    var extCar = el("line", { x1: 428, x2: 512 }, dims);
    var tRod = el("text", { "class": "draw", x: 466, "text-anchor": "end" });
    tRod.textContent = "h";
    var tCar = el("text", { "class": "draw draw--red", x: 498, "text-anchor": "end" });
    tCar.textContent = "2h";

    // Position numbers; the names are in the stamp, small text in the drawing is unreadable on a phone.
    var bubble = function (n) {
      var g = el("g", { "class": "chains-sheet__bubble" });
      var line = el("line", {}, g), dot = el("circle", { r: 2.4, "class": "chains-sheet__dot" }, g), ring = el("circle", { r: 11 }, g);
      var num = el("text", {}, g);
      num.textContent = n;
      return function (bx, by, tx, ty) {
        line.setAttribute("x1", bx); line.setAttribute("y1", by); line.setAttribute("x2", tx); line.setAttribute("y2", ty);
        dot.setAttribute("cx", tx); dot.setAttribute("cy", ty);
        ring.setAttribute("cx", bx); ring.setAttribute("cy", by);
        num.setAttribute("x", bx); num.setAttribute("y", by);
      };
    };
    var b1 = bubble(1), b2 = bubble(2), b3 = bubble(3), b4 = bubble(4);

    // The stamp's readings: the stroke and the lift, in metres.
    var rodOut = sheet.querySelector("[data-run-rod]"), carOut = sheet.querySelector("[data-run-car]");
    var metres = function (out, v) { out.firstChild.nodeValue = (v / H).toFixed(2).replace(".", ","); };

    var draw = function (h) {
      var ty = HEAD0 - h, yc = CAR0 - 2 * h;
      head.setAttribute("transform", "translate(0 " + ty + ")");
      rod.setAttribute("y", ty); rod.setAttribute("height", 268 - ty);
      rodShine.setAttribute("y1", ty + 12);
      car.setAttribute("transform", "translate(0 " + yc + ")");
      sides.forEach(function (s) { s.update(h); });
      dimRod.setAttribute("y2", ty); extHead.setAttribute("y1", ty); extHead.setAttribute("y2", ty);
      dimCar.setAttribute("y2", yc); extCar.setAttribute("y1", yc); extCar.setAttribute("y2", yc);
      tRod.setAttribute("y", (HEAD0 + ty) / 2 + 5); tRod.setAttribute("opacity", h > 8 ? 1 : 0);
      tCar.setAttribute("y", (CAR0 + yc) / 2 + 5); tCar.setAttribute("opacity", h > 8 ? 1 : 0);
      var right = sides[1];
      b1(right.gx + 30, ty - 66, right.gx + 14, ty - 22);
      b2(right.xo + 32, (ty + yc) / 2 + 10, right.xo, (ty + yc) / 2 + 10);
      b3(CX, 335, CX, 335);
      b4(18, yc + CAR_H / 2, 52, yc + CAR_H / 2);
      if (rodOut) metres(rodOut, h);
      if (carOut) metres(carOut, 2 * h);
    };

    // Without motion: still, at two-thirds of the stroke. Otherwise the rod goes out and back
    // while the sheet is on screen.
    if (!canWatch) { draw(H * .66); return; }
    draw(0);
    var ease = function (t) { return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
    var CYCLE = 7000, visible = false, start = null, raf = null;
    var loop = function (now) {
      if (!visible) { raf = null; return; }
      if (start === null) start = now;
      var t = ((now - start) % CYCLE) / CYCLE, k;
      if (t < .4) k = ease(t / .4); else if (t < .5) k = 1; else if (t < .9) k = 1 - ease((t - .5) / .4); else k = 0;
      draw(H * k);
      raf = requestAnimationFrame(loop);
    };
    new IntersectionObserver(function (entries) {
      visible = entries[0].isIntersecting;
      if (visible && !raf) { start = null; raf = requestAnimationFrame(loop); }
    }).observe(sheet);
  }

  // ---------- Kit: a list item and its marker on the picture light up together ----------
  var kit = document.querySelector(".kit");
  if (kit) {
    var light = function (n, on) {
      kit.querySelectorAll('[data-kit-marker="' + n + '"], [data-kit-item="' + n + '"]').forEach(function (el) {
        el.classList.toggle("is-lit", on);
      });
    };
    kit.querySelectorAll("[data-kit-item], [data-kit-marker]").forEach(function (el) {
      var n = el.dataset.kitItem || el.dataset.kitMarker;
      el.addEventListener("mouseenter", function () { light(n, true); });
      el.addEventListener("mouseleave", function () { light(n, false); });
    });
  }

  // ---------- Request sliders: values go into the form's comment ----------
  var params = document.querySelector("[data-model-params]");
  var message = document.getElementById("lead-message");
  if (params && message) {
    var inputs = params.querySelectorAll("[data-param]");
    var prefix = "Модель: " + params.dataset.modelName + ".";
    var touched = false;

    var fill = function (input) {
      var pct = (input.value - input.min) / (input.max - input.min) * 100;
      input.style.setProperty("--fill", pct + "%");
    };
    var format = function (value) { return Number(value).toLocaleString("ru-RU"); };

    // The model always goes in; the parameters only once the visitor has moved a slider.
    var write = function () {
      var line = prefix;
      if (touched) {
        var parts = [];
        inputs.forEach(function (input) {
          parts.push(input.dataset.label.toLowerCase() + " " + format(input.value) + " " + input.dataset.unit);
        });
        line += " Параметры: " + parts.join(", ") + ".";
      }
      // Replace our own line, keep whatever the visitor typed below it.
      var rest = message.value.replace(/^Модель:.*\n?/, "");
      message.value = line + (rest ? "\n" + rest : "");
    };

    var show = function (input) {
      params.querySelector('[data-param-out="' + input.dataset.param + '"]').textContent =
        format(input.value) + " " + input.dataset.unit;
      fill(input);
    };

    inputs.forEach(function (input) {
      show(input);
      input.addEventListener("input", function () {
        show(input);
        touched = true;
        write();
      });
    });
    message.form.addEventListener("submit", write, true);
  }
})();
