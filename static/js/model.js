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

  // ---------- Under the chains photo: the struck-out headline and the chain on a drawing sheet ----------
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
      word.style.transitionDelay = (1.3 + i * 0.12) + "s";
      box.appendChild(word);
      words.appendChild(box);
      words.appendChild(document.createTextNode(" "));
    });
    strike.classList.add("is-pending");
    whenSeen(strike, function () { strike.classList.remove("is-pending"); });
  }

  var sheet = document.querySelector("[data-chains-sheet]");
  if (sheet) drawChain(sheet);

  function drawChain(sheet) {
    var svg = sheet.querySelector("svg");
    var NS = "http://www.w3.org/2000/svg";
    var el = function (name, attrs, parent) {
      var n = document.createElementNS(NS, name);
      for (var k in attrs) n.setAttribute(k, attrs[k]);
      (parent || svg).appendChild(n);
      return n;
    };
    var INK = "#22282b", RED = "#c4161c", PAPER = "#f7f8f7";
    var cx = 140, cy = 112, R = 70, N = 16, stepA = (2 * Math.PI) / N, p = 2 * R * Math.sin(Math.PI / N);
    var pt = function (a, r) { return [cx + r * Math.cos(a), cy - r * Math.sin(a)]; };
    // Centre lines, dash-dot as on a drawing.
    var axes = el("g", { stroke: INK, "stroke-width": 0.8, "stroke-dasharray": "14 3 2 3" });
    el("line", { x1: cx - R - 28, y1: cy, x2: cx + R + 28, y2: cy }, axes);
    el("line", { x1: cx, y1: cy - R - 28, x2: cx, y2: cy + R + 28 }, axes);
    // The sprocket: teeth, hub, bolt holes.
    var gear = el("g");
    var d = "";
    for (var j = 0; j < N; j++) {
      var a = j * stepA;
      [[a - 0.2 * stepA, R - 3], [a, R - 6], [a + 0.2 * stepA, R - 3], [a + 0.38 * stepA, R + 11], [a + 0.62 * stepA, R + 11]]
        .forEach(function (q, k) { var xy = pt(q[0], q[1]); d += (j || k ? "L" : "M") + xy[0].toFixed(1) + " " + xy[1].toFixed(1); });
    }
    el("path", { d: d + "Z", fill: RED, stroke: INK, "stroke-width": 1.6, "stroke-linejoin": "round" }, gear);
    el("circle", { cx: cx, cy: cy, r: R - 26, fill: "none", stroke: INK, "stroke-width": 1.2 }, gear);
    el("circle", { cx: cx, cy: cy, r: 16, fill: PAPER, stroke: INK, "stroke-width": 1.6 }, gear);
    for (var b = 0; b < 6; b++) {
      var h = pt((b * Math.PI) / 3, 30);
      el("circle", { cx: h[0], cy: h[1], r: 5, fill: PAPER, stroke: INK, "stroke-width": 1.2 }, gear);
    }

    // Roller seats along the chain: up the left side, over the top, down the right; arc seats keep their angle.
    var BOTTOM = 300, seats = [], y;
    for (y = BOTTOM + 4 * p; y > cy + 0.1; y -= p) seats.push({ x: cx - R, y: y });
    for (j = 0; j <= N / 2; j++) {
      var aa = Math.PI - j * stepA, s0 = pt(aa, R);
      seats.push({ x: s0[0], y: s0[1], a: aa });
    }
    for (y = cy + p; y <= BOTTOM + 4 * p; y += p) seats.push({ x: cx + R, y: y });
    var at = function (f) {
      var i = Math.floor(f), t = f - i, s1 = seats[i], s2 = seats[i + 1];
      if (s1.a !== undefined && s2.a !== undefined) return pt(s1.a + (s2.a - s1.a) * t, R);
      return [s1.x + (s2.x - s1.x) * t, s1.y + (s2.y - s1.y) * t];
    };
    var COUNT = seats.length - 4;
    var clip = el("clipPath", { id: "chains-sheet-clip" }, el("defs"));
    el("rect", { x: -20, y: -60, width: 440, height: 420 }, clip);  // the svg box itself trims the bottom
    var chain = el("g", { "clip-path": "url(#chains-sheet-clip)" });
    var plates = el("g", {}, chain), rolls = el("g", {}, chain);
    // The second row: the same sprocket and chain once more, set back and darker — the drawing reads
    // as a double sprocket with a double-row chain. <use> copies follow the front row as it moves.
    gear.id = "chains-sheet-gear";
    chain.id = "chains-sheet-chain";
    var DX = 30, DY = -22;
    var back = document.createElementNS(NS, "g");
    back.setAttribute("class", "chains-sheet__back");
    svg.insertBefore(back, gear);
    // The axle through both sprockets, and a pin through each pair of rollers.
    var axle = document.createElementNS(NS, "line");
    [["x1", cx], ["y1", cy], ["x2", cx + DX], ["y2", cy + DY], ["stroke", INK], ["stroke-width", 22], ["stroke-linecap", "round"]]
      .forEach(function (kv) { axle.setAttribute(kv[0], kv[1]); });
    var pins = document.createElementNS(NS, "g");
    pins.setAttribute("clip-path", "url(#chains-sheet-clip)");
    svg.insertBefore(pins, gear);
    svg.insertBefore(axle, pins);
    ["#chains-sheet-gear", "#chains-sheet-chain"].forEach(function (ref) {
      el("use", { href: ref, transform: "translate(" + DX + " " + DY + ")" }, back);
    });
    var addLink = function (from, to) {
      el("line", { x1: from[0], y1: from[1], x2: to[0], y2: to[1], stroke: INK, "stroke-width": 17, "stroke-linecap": "round" }, plates);
      el("line", { x1: from[0], y1: from[1], x2: to[0], y2: to[1], stroke: "#dfe3e1", "stroke-width": 13, "stroke-linecap": "round" }, plates);
    };
    var addRoller = function (xy) {
      el("line", { x1: xy[0], y1: xy[1], x2: xy[0] + DX, y2: xy[1] + DY, stroke: INK, "stroke-width": 7, "stroke-linecap": "round" }, pins);
      return el("circle", { cx: xy[0], cy: xy[1], r: 5.5, fill: "#fff", stroke: INK, "stroke-width": 1.4 }, rolls);
    };
    // Leaders with position numbers.
    var leaders = el("g");
    var leader = function (x1, y1, x2, y2, num, label) {
      el("line", { x1: x1, y1: y1, x2: x2, y2: y2, stroke: INK, "stroke-width": 1 }, leaders);
      el("circle", { cx: x1, cy: y1, r: 2.5, fill: INK }, leaders);
      el("line", { x1: x2, y1: y2, x2: x2 + 116, y2: y2, stroke: INK, "stroke-width": 1 }, leaders);
      el("text", { x: x2 + 4, y: y2 - 5, "class": "draw" }, leaders).textContent = num;
      el("text", { x: x2 + 18, y: y2 - 5, "class": "draw draw--muted" }, leaders).textContent = label;
    };
    leader(cx + 38, cy + 34, 262, 196, "1", svg.getAttribute("data-label-1"));
    leader(cx + R + 7, 238, 262, 256, "2", svg.getAttribute("data-label-2"));

    var place = function (shift) {
      var pos = [];
      for (var i = 0; i < COUNT; i++) pos.push(at(i + 2 + shift));
      Array.prototype.forEach.call(rolls.childNodes, function (c, i) { c.setAttribute("cx", pos[i][0]); c.setAttribute("cy", pos[i][1]); });
      Array.prototype.forEach.call(pins.childNodes, function (l, i) {
        l.setAttribute("x1", pos[i][0]); l.setAttribute("y1", pos[i][1]);
        l.setAttribute("x2", pos[i][0] + DX); l.setAttribute("y2", pos[i][1] + DY);
      });
      Array.prototype.forEach.call(plates.childNodes, function (l, k) {
        var i = (k >> 1) + 1;
        l.setAttribute("x1", pos[i - 1][0]); l.setAttribute("y1", pos[i - 1][1]);
        l.setAttribute("x2", pos[i][0]); l.setAttribute("y2", pos[i][1]);
      });
    };
    var all = [];
    for (var i = 0; i < COUNT; i++) all.push(at(i + 2));

    // Without motion: the finished drawing, standing still.
    if (!canWatch) {
      all.forEach(function (xy, n) { if (n) addLink(all[n - 1], xy); addRoller(xy); });
      return;
    }
    [axes, gear, back, axle, leaders].forEach(function (g) { g.style.opacity = 0; });
    var fade = function (g, ms) { return g.animate([{ opacity: 0 }, { opacity: 1 }], { duration: ms, fill: "forwards" }).finished; };

    // Once laid, the chain keeps running over the sprocket while the sheet is on screen:
    // one pitch every 0.9 s, the sprocket one tooth per pitch, so the rollers stay in the teeth.
    var visible = false, spin = null, last = 0, turned = 0, laid = false;
    var loop = function (now) {
      if (!visible) { spin = null; return; }
      turned += last ? Math.min(0.1, (now - last) / 1000) / 0.9 : 0;
      last = now;
      gear.setAttribute("transform", "rotate(" + turned * stepA * (180 / Math.PI) + " " + cx + " " + cy + ")");
      place(turned % 1);
      spin = requestAnimationFrame(loop);
    };
    var startSpin = function () { if (!spin && visible) { last = 0; spin = requestAnimationFrame(loop); } };
    new IntersectionObserver(function (entries) {
      visible = entries[0].isIntersecting;
      if (visible && laid) startSpin();
    }).observe(sheet);

    whenSeen(sheet, function () {
      fade(axes, 500).then(function () { fade(back, 600); fade(axle, 600); return fade(gear, 600); }).then(function () {
        var n = 0;
        var next = function () {
          if (n === COUNT) {
            fade(leaders, 400);
            laid = true;
            startSpin();
            return;
          }
          if (n) addLink(all[n - 1], all[n]);
          var c = addRoller(all[n]);
          var onSheet = all[n][1] < 285;
          if (onSheet) c.animate([{ r: 0 }, { r: 8 }, { r: 5.5 }], { duration: 260 });
          n++;
          if (onSheet) setTimeout(next, 45); else next();
        };
        next();
      });
    });
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
