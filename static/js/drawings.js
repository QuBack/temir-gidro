// Interactive lift configurator for the home and equipment pages. Content is
// server-rendered; without this file the configurator shows a static render.
(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // ---------- Configurator: sliders redraw a side-view scheme of a scissor lift ----------

  function initConfig(root) {
    // Scissor lifts by default; data-config="console" draws the console lift 1L instead.
    var kind = root.getAttribute("data-config") === "console" ? CONSOLE : SCISSOR;
    var calc = kind.calc, draw = kind.draw;
    var svg = root.querySelector("[data-config-svg]");
    var inputs = root.querySelectorAll("input[type=range]");
    var target = {};
    inputs.forEach(function (input) { target[input.name] = parseFloat(input.value); });
    var current = Object.assign({}, target);
    // The scheme rises from its lowest position when first scrolled into view.
    if (!reduceMotion) current.H = 500;

    root.querySelector("[data-config-fallback]").hidden = true;
    svg.removeAttribute("hidden"); // SVGElement has no .hidden property

    function out(name, text) {
      root.querySelectorAll('[data-out="' + name + '"]').forEach(function (el) { el.textContent = text; });
    }
    function tons(q) { return String(q).replace(".", ","); }

    // The stroke slider stops at what the largest model reaches on this platform and load:
    // a lift the series can't build is never offered.
    var strokeInput = root.querySelector('input[name="H"]');
    var strokeMax = parseFloat(strokeInput.max);
    function keepStroke() {
      var limit = Math.min(strokeMax, calc(target).limit);
      strokeInput.max = limit;
      if (target.H <= limit) return;
      target.H = limit;
      strokeInput.value = limit;
    }

    function sync() {
      inputs.forEach(function (input) {
        var min = parseFloat(input.min), max = parseFloat(input.max);
        input.style.setProperty("--fill", ((input.value - min) / (max - min)) * 100 + "%");
      });
      var c = calc(target);
      out("L", target.L + " мм");
      out("B", target.B + " мм");
      out("H", target.H + " мм");
      out("Q", tons(target.Q) + " т");
      out("LB", target.L + " × " + target.B);
      out("Ls", String(target.L));
      out("Bs", String(target.B));
      out("Hs", String(target.H));
      out("Qs", String(Math.round(target.Q * 1000))); // kg: in ГОСТ lettering "т" reads like "m"
      out("N", String(c.n));
      out("M", kind.model(c)); // a scissor model by its pairs (2 pairs → 2X); the console lift is 1L
      out("Code", [target.L, target.B, Math.round(target.Q * 1000), target.H].join("."));
      out("Hmin", String(c.hmin));
      out("Hmax", String(c.hmin + target.H));
      out("T", String(c.time));
      out("D", String(c.days));
    }

    var frame = 0;
    function animate() {
      var done = true;
      Object.keys(target).forEach(function (key) {
        var diff = target[key] - current[key];
        if (Math.abs(diff) > (key === "Q" ? 0.01 : 1)) {
          current[key] += diff * 0.18;
          done = false;
        } else {
          current[key] = target[key];
        }
      });
      draw(svg, current);
      frame = done ? 0 : requestAnimationFrame(animate);
    }
    function kick() {
      if (reduceMotion) {
        current = Object.assign({}, target);
        draw(svg, current);
      } else if (!frame) {
        frame = requestAnimationFrame(animate);
      }
    }

    // The width never exceeds the length: a narrower length pulls the width down with it,
    // and the width slider stops at the length.
    var widthInput = root.querySelector('input[name="B"]');
    function keepWidth() {
      if (kind !== SCISSOR || target.B <= target.L) return;
      target.B = target.L;
      widthInput.value = target.L;
    }

    inputs.forEach(function (input) {
      input.addEventListener("input", function () {
        target[input.name] = parseFloat(input.value);
        keepWidth();
        keepStroke();
        sync();
        kick();
      });
    });

    keepStroke();
    sync();
    draw(svg, current);
    if (!reduceMotion && "IntersectionObserver" in window) {
      var io = new IntersectionObserver(function (entries) {
        if (entries[0].isIntersecting) { io.disconnect(); kick(); }
      }, { threshold: 0.35 });
      io.observe(svg);
    } else {
      kick();
    }

    // Hand the chosen parameters to the lead form; the link itself scrolls there.
    var send = root.querySelector("[data-config-send]");
    send.addEventListener("click", function () {
      var field = document.getElementById("lead-message"); // the home, line or model form
      if (!field) return;
      var c = calc(target);
      var code = [target.L, target.B, Math.round(target.Q * 1000), target.H].join(".");
      var line = "Параметры подъёмника: платформа " + target.L + " × " + target.B + " мм, ход " +
        target.H + " мм, грузоподъёмность " + tons(target.Q) + " т, модель ТЕМИР ГИДРО " + kind.model(c) + " " +
        code + (kind === SCISSOR ? " (пар ножниц: " + c.n + ")." : ", в сложенном виде " + c.hmin + " мм.");
      var rest = field.value.replace(/^Параметры подъёмника:.*\n?/, "");
      field.value = line + (rest ? "\n" + rest : "");
      var name = document.getElementById("lead-name");
      if (name) setTimeout(function () { name.focus({ preventScroll: true }); }, 600);
      if (window.temirGoal) window.temirGoal("config_sent");
    });
  }

  // ---------- The client's sizing rules (table «Минимальная высота столов», 2026) ----------
  // Load classes, kg (upper bounds); a gap between table ranges goes to the heavier class.
  var LOADS = [500, 1100, 2200, 3300, 4400, 5500];
  // Platform length classes, mm (upper bounds), per load class: up to 500 kg the table
  // has short platforms only, longer ones are taken from the next class.
  var LENGTHS_LIGHT = [1500, 2000, 3000];
  var LENGTHS = [2200, 4400, 5500];
  // Height folded, mm: [load class][length class][pairs − 1]. The table stops at 5X for
  // 4,4–5,5 t: the client has no 6X in that class.
  var HMIN = [
    [[250, 300, 350, 410, 600, 700], [300, 350, 400, 450, 600, 700], [350, 400, 450, 550, 600, 700]],
    [[300, 400, 450, 550, 750, 900], [450, 500, 650, 750, 750, 900], [500, 600, 750, 850, 750, 900]],
    [[450, 500, 650, 750, 850, 1000], [500, 550, 700, 850, 950, 1100], [600, 700, 900, 1050, 1150, 1300]],
    [[500, 550, 700, 850, 950, 1100], [550, 650, 800, 950, 1050, 1200], [600, 750, 900, 1100, 1200, 1350]],
    [[550, 650, 1000, 1300, 1400, 1550], [600, 700, 1100, 1400, 1500, 1650], [650, 800, 1200, 1550, 1650, 1800]],
    [[600, 700, 1050, 1400, 1500], [650, 800, 1150, 1550, 1650], [750, 900, 1350, 1800, 1900]],
  ];
  // Lead time, working days: [load class][length class][1 pair, 2 pairs, 3+ pairs].
  var DAYS = [
    [[30, 35, 40], [30, 35, 40], [30, 35, 40]],
    [[30, 35, 40], [30, 35, 40], [30, 35, 40]],
    [[30, 35, 40], [30, 35, 40], [35, 40, 45]],
    [[35, 40, 45], [35, 40, 45], [35, 40, 45]],
    [[35, 40, 45], [35, 40, 45], [40, 45, 50]],
    [[35, 40, 45], [35, 40, 45], [45, 50, 55]],
  ];

  function classOf(bounds, value) {
    for (var i = 0; i < bounds.length; i++) if (value <= bounds[i]) return i;
    return bounds.length - 1;
  }

  // Pairs of scissors, folded height, stroke limit, lift time and lead time for L, H (stroke), Q.
  // Each pair rises (L − 150) × 0,866 (arms at 60°), so a model rises that times its pairs
  // (client's rule, 2026-10): 3X is × 3. The stroke is that minus the folded height. The largest
  // model in the table (6X, or 5X for the heaviest class) sets the limit of the stroke slider.
  function calc(v) {
    var kg = v.Q * 1000;
    var q = classOf(LOADS, kg);
    var l;
    if (q === 0 && v.L > LENGTHS_LIGHT[2]) { q = 1; }
    l = q === 0 ? classOf(LENGTHS_LIGHT, v.L) : classOf(LENGTHS, v.L);
    var perPair = (v.L - 150) * 0.866;
    var top = function (n) { return perPair * n; };
    var row = HMIN[q][l], n = 1;
    // A model fits only when its stroke strictly exceeds H: an exact match leaves no margin.
    while (n < row.length && top(n) - row[n - 1] <= v.H) n++;
    var hmin = row[n - 1];
    // The longest stroke on offer, in the slider's 100 mm steps, strictly below the largest model's.
    var last = row.length;
    var limit = Math.ceil((top(last) - row[last - 1]) / 100) * 100 - 100;
    var speed = kg <= 1000 ? 70 : kg <= 2000 ? 60 : kg <= 4000 ? 50 : 40; // mm/s
    return {
      n: n, hmin: hmin, limit: limit,
      time: Math.round(v.H / speed), days: DAYS[q][l][Math.min(n, 3) - 1],
    };
  }

  var NS = "http://www.w3.org/2000/svg";
  var FLOOR = 540;

  // px per mm: small lifts are drawn large, big ones shrink to fit the sheet.
  function scale(v, hmax) {
    return Math.min(0.16, 420 / v.L, 360 / hmax);
  }

  function node(svg, tag, attrs, text) {
    var el = document.createElementNS(NS, tag);
    Object.keys(attrs).forEach(function (key) { el.setAttribute(key, attrs[key]); });
    if (text) el.textContent = text;
    svg.appendChild(el);
    return el;
  }
  function line(svg, x1, y1, x2, y2, cls) {
    return node(svg, "line", { x1: x1, y1: y1, x2: x2, y2: y2, "class": cls });
  }
  function arrow(svg, x, y, dir) { // tip at (x, y), pointing up / down / left / right
    var p = {
      up: [x, y, x - 4, y + 11, x + 4, y + 11],
      down: [x, y, x - 4, y - 11, x + 4, y - 11],
      left: [x, y, x + 11, y - 4, x + 11, y + 4],
      right: [x, y, x - 11, y - 4, x - 11, y + 4],
    }[dir];
    node(svg, "polygon", { points: p.join(" "), "class": "s-arrow" });
  }

  function draw(svg, v) {
    svg.textContent = "";
    var c = calc(v);
    var s = scale(v, c.hmin + v.H);
    var lw = v.L * s;
    var hp = Math.max((c.hmin + v.H) * s, 46);
    var hFolded = Math.max(c.hmin * s, 26);
    var x0 = 30 + (500 - lw) / 2, x1 = x0 + lw, cx = x0 + lw / 2;
    var baseTop = FLOOR - 12, platTop = FLOOR - hp, platBottom = platTop + 14;

    // Floor with hatching.
    line(svg, 0, FLOOR, 640, FLOOR, "s-floor");
    for (var hx = 14; hx < 640; hx += 16) line(svg, hx, FLOOR + 1, hx - 9, FLOOR + 10, "s-hatch");

    // Scissor pairs between the base frame and the platform.
    var n = c.n, h = (baseTop - platBottom) / n;
    var xa = x0 + lw * 0.08, xb = x1 - lw * 0.08, pins = [];
    for (var k = 0; k < n; k++) {
      var y1 = platBottom + k * h, y2 = y1 + h;
      line(svg, xa, y1, xb, y2, "s-arm");
      line(svg, xb, y1, xa, y2, "s-arm");
      pins.push([xa, y1], [xb, y1], [(xa + xb) / 2, y1 + h / 2]);
    }
    pins.push([xa, baseTop], [xb, baseTop]);

    // Hydraulic cylinders sit between the arms, as on the 1X–3X renders: the barrel's
    // pivot low on a "\" or "/" arm, the rod's pivot higher up. A 4X is two 2X stacked,
    // so it gets two cylinders; a 5X and a 6X get two long ones that share the third pair from
    // the top, on a 6X the upper one reaching the platform corner (client's sketch).
    // A point is [pair from the top, arm, share of the pair height].
    function onArm(p) {
      var t = p[2], y = platBottom + (p[0] + t) * h;
      return [p[1] === "\\" ? xa + t * (xb - xa) : xb - t * (xb - xa), y];
    }
    var CYLINDERS = {
      1: [[[0, "\\", 0.88], [0, "/", 0.35]]],
      2: [[[1, "\\", 0.74], [0, "/", 0.72]]],
      3: [[[2, "/", 0.14], [0, "/", 0.81]]],
      4: [[[3, "\\", 0.74], [2, "/", 0.72]], [[1, "\\", 0.74], [0, "/", 0.72]]],
      5: [[[4, "/", 0.3], [2, "/", 0.75]], [[2, "/", 0.25], [0, "/", 0.7]]],
      6: [[[5, "/", 0.14], [2, "/", 0.81]], [[2, "/", 0.14], [0, "\\", 0.19]]],
    }[n];
    CYLINDERS.forEach(function (cyl) {
      var a = onArm(cyl[0]), b = onArm(cyl[1]);
      var mx = a[0] + (b[0] - a[0]) * 0.55, my = a[1] + (b[1] - a[1]) * 0.55;
      line(svg, mx, my, b[0], b[1], "s-rod");
      line(svg, a[0], a[1], mx, my, "s-cyl");
      pins.push(a, b);
    });

    node(svg, "rect", { x: x0, y: baseTop, width: lw, height: 12, "class": "s-frame" });
    node(svg, "rect", { x: x0, y: platTop, width: lw, height: 14, "class": "s-frame" });
    pins.forEach(function (p) { node(svg, "circle", { cx: p[0], cy: p[1], r: 4, "class": "s-pin" }); });

    // Load on the platform and the Q arrow.
    var bw = Math.min(lw * 0.6, 36 + v.Q * 12), bh = 16 + v.Q * 5, by = platTop - bh;
    node(svg, "rect", { x: cx - bw / 2, y: by, width: bw, height: bh, "class": "s-load" });
    line(svg, cx, by - 58, cx, by - 4, "s-dim");
    arrow(svg, cx, by - 3, "down");
    node(svg, "text", { x: cx + 10, y: by - 38 }, "Q = " + Math.round(v.Q * 10) * 100 + " кг");

    // Folded platform: a dashed outline at the folded height.
    var foldTop = FLOOR - hFolded;
    node(svg, "rect", { x: x0, y: foldTop, width: lw, height: 10, "class": "s-ghost" });

    // H (stroke) from the folded platform up, Hmin from the floor: as on the client's sketch.
    var dx = x1 + 40;
    line(svg, x1 + 6, platTop, dx + 8, platTop, "s-dim");
    line(svg, x1 + 6, foldTop, dx + 8, foldTop, "s-dim");
    line(svg, x1 + 6, FLOOR, dx + 8, FLOOR, "s-dim");
    line(svg, dx, platTop + 2, dx, foldTop - 2, "s-dim");
    arrow(svg, dx, platTop + 1, "up");
    arrow(svg, dx, foldTop - 1, "down");
    var hy = (platTop + foldTop) / 2;
    node(svg, "text", { x: dx - 8, y: hy, transform: "rotate(-90 " + (dx - 8) + " " + hy + ")", "text-anchor": "middle" },
      "H = " + Math.round(v.H / 10) * 10);
    // Hmin: floor to the folded platform, always labelled. With room, along the line like H; a low
    // folded lift leaves too short a span, so then the label runs up from the floor on the line's
    // other side, clear of the H label.
    line(svg, dx, foldTop + 2, dx, FLOOR - 2, "s-dim");
    arrow(svg, dx, foldTop + 1, "up");
    arrow(svg, dx, FLOOR - 1, "down");
    var hminText = "Hmin = " + c.hmin;
    if (hFolded >= 150) {
      var my2 = (foldTop + FLOOR) / 2;
      node(svg, "text", { x: dx - 8, y: my2, transform: "rotate(-90 " + (dx - 8) + " " + my2 + ")", "text-anchor": "middle" },
        hminText);
    } else {
      var hx = dx + 28, hy2 = FLOOR - 4;
      node(svg, "text", { x: hx, y: hy2, transform: "rotate(-90 " + hx + " " + hy2 + ")", "text-anchor": "start" }, hminText);
    }

    // L: under the floor.
    var ly = FLOOR + 38;
    line(svg, x0, FLOOR + 14, x0, ly + 8, "s-dim");
    line(svg, x1, FLOOR + 14, x1, ly + 8, "s-dim");
    line(svg, x0 + 2, ly, x1 - 2, ly, "s-dim");
    arrow(svg, x0 + 1, ly, "left");
    arrow(svg, x1 - 1, ly, "right");
    node(svg, "text", { x: cx, y: ly + 28, "text-anchor": "middle" }, "L = " + Math.round(v.L / 10) * 10);
  }

  // ---------- Console lift 1L (client's ranges, 2026-10) ----------
  // L 800–2800, B 800–2000, stroke to 12 m, up to 2 t. Folded 200 mm; 150 mm when the load is up
  // to 600 kg, the platform up to 2200 mm long and up to 1300 mm wide.
  function calcConsole(v) {
    var low = v.Q * 1000 <= 600 && v.L <= 2200 && v.B <= 1300;
    return { n: 1, hmin: low ? 150 : 200, limit: 12000 };
  }

  // Side view: the mast on the left, the platform on its carriage sticking out to the right. Seen
  // from the side, the platform's run from the mast is its width B (the length L goes into the sheet).
  function drawConsole(svg, v) {
    svg.textContent = "";
    var c = calcConsole(v);
    var CARRIAGE = 900, MAST = 260; // mm: carriage height above the deck, mast depth
    var s = Math.min(0.16, 400 / (v.B + MAST), 430 / (c.hmin + v.H + CARRIAGE + 300));
    var lw = v.B * s, mw = Math.max(MAST * s, 16);
    var x0 = 30 + (470 - mw - lw) / 2, mx1 = x0 + mw, x1 = mx1 + lw, cx = mx1 + lw / 2;
    var hp = Math.max((c.hmin + v.H) * s, 10);
    var platTop = FLOOR - hp - 10, platBottom = FLOOR - hp;
    var carTop = platTop - Math.max(CARRIAGE * s, 34);
    var mastTop = Math.min(carTop - Math.max(300 * s, 14), FLOOR - (c.hmin + v.H + CARRIAGE + 300) * s);

    line(svg, 0, FLOOR, 640, FLOOR, "s-floor");
    for (var hx = 14; hx < 640; hx += 16) line(svg, hx, FLOOR + 1, hx - 9, FLOOR + 10, "s-hatch");

    // Mast: two columns from the floor up, the cylinder between them.
    // The mast's two columns in the lifts' red, the cylinder between them dark.
    node(svg, "rect", { x: x0, y: mastTop, width: mw * 0.3, height: FLOOR - mastTop, "class": "s-mast" });
    node(svg, "rect", { x: x0 + mw * 0.7, y: mastTop, width: mw * 0.3, height: FLOOR - mastTop, "class": "s-mast" });
    var mc = x0 + mw / 2, rodTop = carTop + (platBottom - carTop) * 0.3;
    var barrelTop = FLOOR - Math.max((FLOOR - rodTop) * 0.52, 20);
    line(svg, mc, barrelTop, mc, FLOOR - 6, "s-cyl");
    line(svg, mc, rodTop, mc, barrelTop, "s-rod");

    // Carriage on the mast, the platform and its brace.
    node(svg, "rect", { x: mx1, y: carTop, width: 8, height: platBottom - carTop, "class": "s-frame" });
    node(svg, "rect", { x: mx1, y: platTop, width: lw, height: platBottom - platTop, "class": "s-frame" });
    [[mx1 + 4, carTop + 6], [mx1 + 4, platBottom - 6], [mc, rodTop]].forEach(function (p) {
      node(svg, "circle", { cx: p[0], cy: p[1], r: 4, "class": "s-pin" });
    });

    // Load on the platform and the Q arrow.
    var bw = Math.min(lw * 0.55, 30 + v.Q * 20), bh = 14 + v.Q * 8, by = platTop - bh, lx = mx1 + lw * 0.58;
    node(svg, "rect", { x: lx - bw / 2, y: by, width: bw, height: bh, "class": "s-load" });
    line(svg, lx, by - 58, lx, by - 4, "s-dim");
    arrow(svg, lx, by - 3, "down");
    node(svg, "text", { x: lx + 10, y: by - 38 }, "Q = " + Math.round(v.Q * 10) * 100 + " кг");

    // Folded platform: a dashed outline at the folded height.
    var hFolded = Math.max(c.hmin * s, 8), foldTop = FLOOR - hFolded;
    node(svg, "rect", { x: mx1, y: foldTop - 8, width: lw, height: 8, "class": "s-ghost" });

    // H from the folded deck up, Hmin from the floor, as on the scissor scheme.
    var dx = x1 + 40, deck = platTop, fold = foldTop - 8;
    line(svg, x1 + 6, deck, dx + 8, deck, "s-dim");
    line(svg, x1 + 6, fold, dx + 8, fold, "s-dim");
    line(svg, x1 + 6, FLOOR, dx + 8, FLOOR, "s-dim");
    line(svg, dx, deck + 2, dx, fold - 2, "s-dim");
    arrow(svg, dx, deck + 1, "up");
    arrow(svg, dx, fold - 1, "down");
    var hy = (deck + fold) / 2;
    node(svg, "text", { x: dx - 8, y: hy, transform: "rotate(-90 " + (dx - 8) + " " + hy + ")", "text-anchor": "middle" },
      "H = " + Math.round(v.H / 10) * 10);
    line(svg, dx, fold + 2, dx, FLOOR - 2, "s-dim");
    var hxm = dx + 28, hym = FLOOR - 4;
    node(svg, "text", { x: hxm, y: hym, transform: "rotate(-90 " + hxm + " " + hym + ")", "text-anchor": "start" }, "Hmin = " + c.hmin);

    // B: under the floor, along the platform.
    var ly = FLOOR + 38;
    line(svg, mx1, FLOOR + 14, mx1, ly + 8, "s-dim");
    line(svg, x1, FLOOR + 14, x1, ly + 8, "s-dim");
    line(svg, mx1 + 2, ly, x1 - 2, ly, "s-dim");
    arrow(svg, mx1 + 1, ly, "left");
    arrow(svg, x1 - 1, ly, "right");
    node(svg, "text", { x: cx, y: ly + 28, "text-anchor": "middle" }, "B = " + Math.round(v.B / 10) * 10);
  }

  var SCISSOR = { calc: calc, draw: draw, model: function (c) { return c.n + "X"; } };
  var CONSOLE = { calc: calcConsole, draw: drawConsole, model: function () { return "1L"; } };

  // Started last: the tables and constants above must be set first.
  var config = document.querySelector("[data-config]");
  if (config) initConfig(config);
})();
