// Cylinder configurator on /gidrocilindry/: the mounting, bore, rod, stroke and pressure redraw a
// dimensioned side view from the catalog tables (apps/core/cylinders.py → #cyl-config-data).
// Content is server-rendered; without this file the section shows a static scheme.
(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var NS = "http://www.w3.org/2000/svg";
  var SHEET_H = 290; // the sheet's height in the viewBox

  function initConfig(root, data) {
    var svg = root.querySelector("[data-config-svg]");
    var boreInput = root.querySelector('input[name="bore"]');
    var rodBox = root.querySelector("[data-cyl-rods]");
    var ranges = root.querySelectorAll("input[type=range]");
    var target = {
      mount: root.querySelector('input[name="mount"]:checked').value,
      bore: parseInt(boreInput.value, 10),
      rod: 0, // index among the bore's rods: 0 is the thinner one
      stroke: parseFloat(root.querySelector('input[name="stroke"]').value),
      pressure: parseFloat(root.querySelector('input[name="pressure"]').value),
    };
    var shape = geometry(data, target);
    // The rod comes out of the cylinder when the sheet is first scrolled into view.
    var current = Object.assign({}, shape, { ext: reduceMotion ? 1 : 0 });
    shape.ext = 1;

    root.querySelector("[data-config-fallback]").hidden = true;
    svg.removeAttribute("hidden"); // SVGElement has no .hidden property

    function out(name, text) {
      root.querySelectorAll('[data-out="' + name + '"]').forEach(function (el) { el.textContent = text; });
    }

    // A mounting without the largest bore (MF3 stops at 200) pulls the bore slider back.
    function keepBore() {
      var a = data.mounts[target.mount].A, last = a.length - 1;
      while (a[last] === null) last--;
      boreInput.max = last;
      if (target.bore > last) { target.bore = last; boreInput.value = last; }
    }

    // The rod choice follows the bore: one or two rods from the table, the same side kept.
    function rodsFor() {
      var m = data.mounts[target.mount];
      return target.bore === data.bores.length - 1 && m.rods250 ? m.rods250 : data.rods[target.bore];
    }
    function renderRods() {
      var rods = rodsFor();
      if (target.rod >= rods.length) target.rod = rods.length - 1;
      rodBox.textContent = "";
      rods.forEach(function (d, i) {
        var label = document.createElement("label");
        label.className = "choice__option";
        var input = document.createElement("input");
        input.type = "radio"; input.name = "rod"; input.value = i; input.checked = i === target.rod;
        var span = document.createElement("span");
        span.textContent = d + " мм";
        label.appendChild(input); label.appendChild(span);
        rodBox.appendChild(label);
      });
    }

    function sync() {
      ranges.forEach(function (input) {
        var min = parseFloat(input.min), max = parseFloat(input.max);
        input.style.setProperty("--fill", ((input.value - min) / (max - min)) * 100 + "%");
      });
      var c = calc(data, target);
      out("mountName", data.mounts[target.mount].name);
      out("D", c.D + " мм");
      out("S", target.stroke + " мм");
      out("P", target.pressure + " МПа");
      out("M", target.mount);
      out("Code", c.code);
      out("Fpush", num(c.push));
      out("Fpull", num(c.pull));
      out("Lmin", String(c.lmin));
      out("Lmax", String(c.lmin + target.stroke));
      out("Area", fixed(c.area, 1));
      out("Oil", c.oil < 1 ? fixed(c.oil, 2) : c.oil < 10 ? fixed(c.oil, 1) : String(Math.round(c.oil)));
      out("X", data.X[target.bore]);
      out("Y", data.Y[target.bore]);
    }

    var frame = 0;
    function animate() {
      var done = true;
      Object.keys(shape).forEach(function (key) {
        if (typeof shape[key] !== "number") { current[key] = shape[key]; return; }
        if (typeof current[key] !== "number") current[key] = shape[key];
        var diff = shape[key] - current[key];
        if (Math.abs(diff) > (key === "ext" ? 0.002 : 0.5)) {
          current[key] += diff * (key === "ext" ? 0.06 : 0.18);
          done = false;
        } else {
          current[key] = shape[key];
        }
      });
      draw(svg, current, calc(data, target));
      frame = done ? 0 : requestAnimationFrame(animate);
    }
    function kick() {
      shape = Object.assign(geometry(data, target), { ext: shape.ext });
      if (reduceMotion) {
        current = Object.assign({}, shape);
        draw(svg, current, calc(data, target));
      } else if (!frame) {
        frame = requestAnimationFrame(animate);
      }
    }
    function update() { sync(); kick(); }

    root.addEventListener("input", function (e) {
      var input = e.target;
      if (input.name === "mount") { target.mount = input.value; keepBore(); renderRods(); }
      else if (input.name === "bore") { target.bore = parseInt(input.value, 10); renderRods(); }
      else if (input.name === "rod") { target.rod = parseInt(input.value, 10); }
      else if (input.name === "stroke" || input.name === "pressure") { target[input.name] = parseFloat(input.value); }
      else return;
      update();
    });

    keepBore();
    renderRods();
    sync();
    draw(svg, current, calc(data, target));
    if (!reduceMotion && "IntersectionObserver" in window) {
      var io = new IntersectionObserver(function (entries) {
        if (entries[0].isIntersecting) { io.disconnect(); kick(); }
      }, { threshold: 0.35 });
      io.observe(svg);
    } else {
      kick();
    }

    // Hand the chosen cylinder to the lead form; the link itself scrolls there.
    root.querySelector("[data-config-send]").addEventListener("click", function () {
      var field = document.getElementById("lead-message");
      if (!field) return;
      var c = calc(data, target);
      var line = "Параметры гидроцилиндра: крепление " + target.mount + " (" + data.mounts[target.mount].name.toLowerCase() +
        "), поршень " + c.D + " мм, шток " + c.d + " мм, ход " + target.stroke + " мм, давление " + target.pressure +
        " МПа — ТЕМИР ГИДРО " + target.mount + " " + c.code + ".";
      var rest = field.value.replace(/^Параметры гидроцилиндра:.*\n?/, "");
      field.value = line + (rest ? "\n" + rest : "");
      var name = document.getElementById("lead-name");
      if (name) setTimeout(function () { name.focus({ preventScroll: true }); }, 600);
      if (window.temirGoal) window.temirGoal("cylinder_config_sent");
    });
  }

  function fixed(x, digits) { return x.toFixed(digits).replace(".", ","); }
  function num(kn) { return kn < 100 ? fixed(kn, 1) : String(Math.round(kn)); }

  // ---------- The numbers: catalog sizes, areas and forces ----------

  // Forces from the areas: F = p × A, MPa × mm² = N. Oil per stroke: the piston side, litres.
  function calc(data, v) {
    var D = data.bores[v.bore];
    var rods = v.bore === data.bores.length - 1 && data.mounts[v.mount].rods250 ? data.mounts[v.mount].rods250 : data.rods[v.bore];
    var d = rods[Math.min(v.rod, rods.length - 1)];
    var a1 = Math.PI * D * D / 4, a3 = a1 - Math.PI * d * d / 4; // mm²
    return {
      D: D, d: d, p: v.pressure,
      area: a1 / 100,
      push: v.pressure * a1 / 1000,
      pull: v.pressure * a3 / 1000,
      oil: a1 * v.stroke / 1e6,
      lmin: data.mounts[v.mount].A[v.bore] + v.stroke,
      code: [D, d, v.stroke, v.pressure].join("."),
    };
  }

  // Everything the drawing needs, in mm: animated between two states key by key.
  function geometry(data, v) {
    var m = data.mounts[v.mount], i = v.bore, c = calc(data, v);
    var W = data.W[i];
    return {
      mount: v.mount, D: c.D, d: c.d, W: W, A: m.A[i], B: data.B[i], S: v.stroke,
      O: m.O ? m.O[i] : 0, C: m.C ? m.C[i] : 0, R: m.R ? m.R[i] : 0,
    };
  }

  // ---------- The drawing ----------

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
  function rect(svg, x, y, w, h, cls) {
    return node(svg, "rect", { x: x, y: y, width: Math.max(w, 0), height: Math.max(h, 0), "class": cls });
  }
  function circle(svg, cx, cy, r, cls) {
    return node(svg, "circle", { cx: cx, cy: cy, r: r, "class": cls });
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
  // A horizontal dimension between x1 and x2 on the line y, extension lines up to y0.
  function hdim(svg, x1, x2, y, y0, label) {
    line(svg, x1, y0, x1, y + 8, "s-dim");
    line(svg, x2, y0, x2, y + 8, "s-dim");
    if (x2 - x1 > 26) {
      line(svg, x1 + 2, y, x2 - 2, y, "s-dim");
      arrow(svg, x1, y, "left"); arrow(svg, x2, y, "right");
    } else { // too short for the arrows inside: they point in from outside
      line(svg, x1 - 18, y, x2 + 18, y, "s-dim");
      arrow(svg, x1, y, "right"); arrow(svg, x2, y, "left");
    }
    node(svg, "text", { x: (x1 + x2) / 2, y: y - 8, "text-anchor": "middle" }, label);
  }

  function draw(svg, g, c) {
    svg.textContent = "";
    var eye = g.mount === "MP3" || g.mount === "MP5";
    var re = eye ? Math.max(g.C * 0.95, g.W * 0.3) : 0; // eye outer radius
    var L = g.A + g.S; // retracted: the reference point to the rod end
    var stroke = g.S * g.ext;
    var rear = eye ? re : 0, half = Math.max(g.W, g.O) / 2;
    var below = g.mount === "MS2" ? Math.max(g.R + g.C * 0.35, half) : half;
    // px per mm: the whole extended cylinder fits across, the flange or the feet fit in height.
    var s = Math.min(2.5, 540 / (rear + L + g.S), 92 / half, 110 / below);
    var x0 = 48 + rear * s + (540 - (rear + L + g.S) * s) / 2;
    // The axis sits so that the cylinder with its labels above and dimensions below is centred.
    var above = Math.max(g.W * 0.54, g.O / 2) * s + Math.max(g.W * 0.12 * s, 4) + 46, under = below * s + 56;
    var AXIS = above + (SHEET_H - above - under) / 2;
    function X(mm) { return x0 + mm * s; }
    var w2 = g.W * s / 2, d2 = Math.max(g.d * s / 2, 2), D2 = g.D * s / 2;

    var capLen = g.W * 0.35, headLen = g.W * 0.45;
    var capStart = eye ? re * 0.55 : (g.mount === "MF4" ? g.C : 0);
    var headEnd = L - g.B, headStart = headEnd - headLen, barrelStart = capStart + capLen;
    var rodEnd = L + stroke;
    var top = AXIS - w2;

    line(svg, X(-rear) - 16, AXIS, X(L + g.S) + 16, AXIS, "c-axis");

    // Feet (MS2) under the cap and the head; the floor they stand on.
    if (g.mount === "MS2") {
      var floor = AXIS + g.R * s, fw = g.C * 1.6;
      line(svg, X(-rear) - 16, floor, X(headEnd) + 30, floor, "s-floor");
      [capStart + capLen / 2, headStart + headLen / 2].forEach(function (mid) {
        rect(svg, X(mid - fw / 2), AXIS, fw * s, floor - AXIS, "c-cap");
      });
    }

    // Ports at both ends of the barrel; the oil goes in at P.
    var portW = Math.max(g.W * 0.2 * s, 6), portH = Math.max(g.W * 0.12 * s, 4);
    var portRear = X(barrelStart) + portW * 0.8, portFront = X(headStart) - portW * 1.8;
    rect(svg, portRear, top - portH, portW, portH, "c-port");
    rect(svg, portFront, top - portH, portW, portH, "c-port");

    // Rod: from the piston out of the head; the thread on its end.
    // The piston travels with the rod: at the cap when retracted, a stroke further when out.
    var piston = Math.min(barrelStart + g.W * 0.1 + stroke, headStart - g.W * 0.25);
    rect(svg, X(headEnd), AXIS - d2, X(rodEnd) - X(headEnd), d2 * 2, "c-rod");
    var thread = Math.min(g.B * 0.55, 60) * s;
    for (var tx = X(rodEnd) - thread; tx < X(rodEnd) - 2; tx += 4) line(svg, tx, AXIS - d2, tx + 2, AXIS + d2, "s-hatch");

    // Barrel, cap and head.
    rect(svg, X(barrelStart), top, X(headStart) - X(barrelStart), w2 * 2, "c-body");
    rect(svg, X(capStart), AXIS - w2 * 1.08, capLen * s, w2 * 2.16, "c-cap");
    rect(svg, X(headStart), AXIS - w2 * 1.08, headLen * s, w2 * 2.16, "c-cap");
    // Piston and the rod inside, as hidden lines.
    rect(svg, X(piston), AXIS - D2, Math.max(g.W * 0.25 * s, 4), D2 * 2, "s-ghost");
    line(svg, X(piston) + Math.max(g.W * 0.25 * s, 4), AXIS - d2, X(headStart), AXIS - d2, "s-ghost");
    line(svg, X(piston) + Math.max(g.W * 0.25 * s, 4), AXIS + d2, X(headStart), AXIS + d2, "s-ghost");

    // The mounting.
    if (g.mount === "MF3") rect(svg, X(headEnd - g.C), AXIS - g.O * s / 2, g.C * s, g.O * s, "c-cap");
    if (g.mount === "MF4") rect(svg, X(0), AXIS - g.O * s / 2, g.C * s, g.O * s, "c-cap");
    if (eye) {
      circle(svg, X(0), AXIS, re * s, "c-eye");
      circle(svg, X(0), AXIS, Math.max(g.C * s / 2, 2), g.mount === "MP5" ? "c-cap" : "c-hole");
      if (g.mount === "MP5") circle(svg, X(0), AXIS, Math.max(g.C * s / 3, 1.5), "c-hole");
    }
    if (g.mount === "MT4") { // the trunnions seen end-on, across the middle of the barrel
      var mid = (barrelStart + headStart) / 2;
      rect(svg, X(mid) - g.C * 0.8 * s, AXIS - w2 * 1.12, g.C * 1.6 * s, w2 * 2.24, "c-cap");
      circle(svg, X(mid), AXIS, Math.max(g.C * s / 2, 3), "c-hole");
    }

    // Dimensions: ØD at the piston, Ød at the rod, the retracted length and the stroke below.
    var px = X(piston) + Math.max(g.W * 0.25 * s, 4) / 2;
    if (D2 > 14) {
      line(svg, px, AXIS - D2 + 12, px, AXIS + D2 - 12, "s-dim");
      arrow(svg, px, AXIS - D2, "up"); arrow(svg, px, AXIS + D2, "down");
    }
    node(svg, "text", { x: px + 10, y: top - portH - 12, "text-anchor": "start" }, "ØD " + c.D);
    var rx = (X(headEnd) + X(rodEnd) - thread) / 2;
    line(svg, rx, AXIS - d2 - 28, rx, AXIS - d2 - 11, "s-dim");
    arrow(svg, rx, AXIS - d2, "down");
    node(svg, "text", { x: rx + 8, y: AXIS - d2 - 22 }, "Ød " + c.d);

    // One chain under the cylinder: the retracted length, then the stroke.
    var dimY = AXIS + below * s + 46;
    hdim(svg, X(0), X(L), dimY, AXIS + 6, "A + S = " + c.lmin);
    if (g.S * g.ext * s > 1) hdim(svg, X(L), X(rodEnd), dimY, AXIS + d2 + 4, "S " + Math.round(g.S));

    // Pressure in at the rear port, the push out of the rod end.
    var pX = portRear + portW / 2;
    line(svg, pX, top - portH - 40, pX, top - portH - 12, "s-dim");
    arrow(svg, pX, top - portH - 1, "down");
    node(svg, "text", { x: pX - 10, y: top - portH - 20, "text-anchor": "end" }, "P " + c.p);
    line(svg, X(rodEnd) + 6, AXIS, X(rodEnd) + 36, AXIS, "s-dim");
    arrow(svg, X(rodEnd) + 46, AXIS, "right");
    node(svg, "text", { x: X(rodEnd) + 26, y: AXIS - 14, "text-anchor": "middle" }, "F");
  }

  document.querySelectorAll("[data-cyl-config]").forEach(function (root) {
    var data = JSON.parse(document.getElementById("cyl-config-data").textContent);
    initConfig(root, data);
  });
})();
