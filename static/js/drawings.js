// Interactive lift configurator for the home and equipment pages. Content is
// server-rendered; without this file the configurator shows a static render.
(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // ---------- Configurator: sliders redraw a side-view scheme of a scissor lift ----------

  function initConfig(root) {
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

    var note = root.querySelector("[data-config-note]");

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
      out("Hs", String(target.H));
      out("Qs", String(Math.round(target.Q * 1000))); // kg: in ГОСТ lettering "т" reads like "m"
      out("N", String(c.n));
      out("Hmin", String(c.hmin));
      out("Hmax", String(c.hmin + target.H));
      out("T", String(c.time));
      out("D", String(c.days));
      out("Hreach", String(c.reach));
      note.hidden = c.ok;
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

    inputs.forEach(function (input) {
      input.addEventListener("input", function () {
        target[input.name] = parseFloat(input.value);
        sync();
        kick();
      });
    });

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
      var field = document.getElementById("lead-message");
      if (!field) return;
      var c = calc(target);
      var line = "Параметры подъёмника: платформа " + target.L + " × " + target.B + " мм, ход " +
        target.H + " мм, грузоподъёмность " + tons(target.Q) + " т, пар ножниц: " + c.n + ".";
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
  // Height folded, mm: [load class][length class][pairs − 1].
  var HMIN = [
    [[250, 300, 350, 410], [300, 350, 400, 450], [350, 400, 450, 550]],
    [[300, 400, 450, 550], [450, 500, 650, 750], [500, 600, 750, 850]],
    [[450, 500, 650, 750], [500, 550, 700, 850], [600, 700, 900, 1050]],
    [[500, 550, 700, 850], [550, 650, 800, 950], [600, 750, 900, 1100]],
    [[550, 650, 1000, 1300], [600, 700, 1100, 1400], [650, 800, 1200, 1550]],
    [[600, 700, 1050, 1400], [650, 800, 1150, 1550], [750, 900, 1350, 1800]],
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

  // Pairs of scissors, folded height, reach, lift time and lead time for L, H (stroke), Q.
  // One pair rises to (L − 150) × 0,866 (arms at 60°); the stroke is that minus the folded height.
  function calc(v) {
    var kg = v.Q * 1000;
    var q = classOf(LOADS, kg);
    var l;
    if (q === 0 && v.L > LENGTHS_LIGHT[2]) { q = 1; }
    l = q === 0 ? classOf(LENGTHS_LIGHT, v.L) : classOf(LENGTHS, v.L);
    var perPair = (v.L - 150) * 0.866;
    var n = 1;
    while (n < 4 && n * perPair - HMIN[q][l][n - 1] < v.H) n++;
    var hmin = HMIN[q][l][n - 1];
    var reach = Math.floor((n * perPair - hmin) / 10) * 10;
    var speed = kg <= 1000 ? 70 : kg <= 2000 ? 60 : kg <= 4000 ? 50 : 40; // mm/s
    return {
      n: n, hmin: hmin, reach: reach, ok: reach >= v.H,
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

    // Hydraulic cylinder: from the base to the centre pin of the lowest pair.
    var sx = xa + (xb - xa) * 0.1, sy = baseTop - 3;
    var ex = (xa + xb) / 2, ey = baseTop - h / 2;
    var mx = sx + (ex - sx) * 0.55, my = sy + (ey - sy) * 0.55;
    line(svg, mx, my, ex, ey, "s-rod");
    line(svg, sx, sy, mx, my, "s-cyl");

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
    // Hmin: floor to the folded platform. Labelled only when there is room; the stamp always shows it.
    line(svg, dx, foldTop + 2, dx, FLOOR - 2, "s-dim");
    arrow(svg, dx, foldTop + 1, "up");
    arrow(svg, dx, FLOOR - 1, "down");
    if (hFolded >= 120) {
      var my2 = (foldTop + FLOOR) / 2;
      node(svg, "text", { x: dx - 8, y: my2, transform: "rotate(-90 " + (dx - 8) + " " + my2 + ")", "text-anchor": "middle" },
        "Hmin = " + c.hmin);
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

  // Started last: the tables and constants above must be set first.
  var config = document.querySelector("[data-config]");
  if (config) initConfig(config);
})();
