// Interactive lift configurator for the home and equipment pages. Content is
// server-rendered; without this file the configurator shows a static render.
(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // ---------- Configurator: sliders redraw a side-view scheme of a scissor lift ----------
  var config = document.querySelector("[data-config]");
  if (config) initConfig(config);

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

    function sync() {
      inputs.forEach(function (input) {
        var min = parseFloat(input.min), max = parseFloat(input.max);
        input.style.setProperty("--fill", ((input.value - min) / (max - min)) * 100 + "%");
      });
      out("L", target.L + " мм");
      out("B", target.B + " мм");
      out("H", target.H + " мм");
      out("Q", tons(target.Q) + " т");
      out("LB", target.L + " × " + target.B);
      out("Hs", String(target.H));
      out("Qs", String(target.Q * 1000)); // kg: in ГОСТ lettering "т" reads like "m"
      out("N", String(pairs(target)));
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
      var line = "Параметры подъёмника: платформа " + target.L + " × " + target.B + " мм, высота подъёма " +
        target.H + " мм, грузоподъёмность " + tons(target.Q) + " т.";
      var rest = field.value.replace(/^Параметры подъёмника:.*\n?/, "");
      field.value = line + (rest ? "\n" + rest : "");
      var name = document.getElementById("lead-name");
      if (name) setTimeout(function () { name.focus({ preventScroll: true }); }, 600);
      if (window.temirGoal) window.temirGoal("config_sent");
    });
  }

  // Longer platform → longer arms → fewer pairs for the same height. Schematic only.
  function pairs(v) {
    return Math.min(4, Math.max(1, Math.ceil(v.H / (0.55 * v.L))));
  }

  var NS = "http://www.w3.org/2000/svg";
  var FLOOR = 540;

  // px per mm: small lifts are drawn large, big ones shrink to fit the sheet.
  function scale(v) {
    return Math.min(0.16, 420 / v.L, 360 / v.H);
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
    var s = scale(v);
    var lw = v.L * s;
    var hp = Math.max(v.H * s, 46);
    var x0 = 30 + (500 - lw) / 2, x1 = x0 + lw, cx = x0 + lw / 2;
    var baseTop = FLOOR - 12, platTop = FLOOR - hp, platBottom = platTop + 14;

    // Floor with hatching.
    line(svg, 0, FLOOR, 640, FLOOR, "s-floor");
    for (var hx = 14; hx < 640; hx += 16) line(svg, hx, FLOOR + 1, hx - 9, FLOOR + 10, "s-hatch");

    // Scissor pairs between the base frame and the platform.
    var n = pairs(v), h = (baseTop - platBottom) / n;
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
    node(svg, "text", { x: cx + 10, y: by - 38 }, "Q = " + Math.round(v.Q * 2) * 500 + " кг");

    // H: platform top to floor, right of the lift.
    var dx = x1 + 40;
    line(svg, x1 + 6, platTop, dx + 8, platTop, "s-dim");
    line(svg, x1 + 6, FLOOR, dx + 8, FLOOR, "s-dim");
    line(svg, dx, platTop + 2, dx, FLOOR - 2, "s-dim");
    arrow(svg, dx, platTop + 1, "up");
    arrow(svg, dx, FLOOR - 1, "down");
    var hy = (platTop + FLOOR) / 2;
    node(svg, "text", { x: dx - 8, y: hy, transform: "rotate(-90 " + (dx - 8) + " " + hy + ")", "text-anchor": "middle" },
      "H = " + Math.round(v.H / 10) * 10);

    // L: under the floor.
    var ly = FLOOR + 38;
    line(svg, x0, FLOOR + 14, x0, ly + 8, "s-dim");
    line(svg, x1, FLOOR + 14, x1, ly + 8, "s-dim");
    line(svg, x0 + 2, ly, x1 - 2, ly, "s-dim");
    arrow(svg, x0 + 1, ly, "left");
    arrow(svg, x1 - 1, ly, "right");
    node(svg, "text", { x: cx, y: ly + 28, "text-anchor": "middle" }, "L = " + Math.round(v.L / 10) * 10);
  }
})();
