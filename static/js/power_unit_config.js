// Power unit page (/gidrostancii/): the purpose chips filter the types, and the calculator
// recalculates the circuit and the title block from apps/core/power_units.py (#pu-config-data).
// Content is server-rendered: without this file every type shows and the circuit keeps its defaults.
(function () {
  "use strict";

  // ---------- Purpose chips: only the types for that purpose stay ----------
  document.querySelectorAll("[data-pu-filter]").forEach(function (section) {
    var chips = section.querySelectorAll("[data-purpose]");
    var types = section.querySelectorAll("[data-purposes]");
    chips.forEach(function (chip) {
      chip.addEventListener("click", function () {
        var key = chip.dataset.purpose;
        chips.forEach(function (c) {
          c.classList.toggle("is-active", c === chip);
          c.setAttribute("aria-pressed", c === chip ? "true" : "false");
        });
        types.forEach(function (t) {
          t.hidden = key !== "" && t.dataset.purposes.split(" ").indexOf(key) < 0;
        });
      });
    });
  });

  // ---------- Calculator ----------
  var root = document.querySelector("[data-pu-config]");
  if (!root) return;
  var data = JSON.parse(document.getElementById("pu-config-data").textContent);
  var ranges = root.querySelectorAll("input[type=range]");
  var warn = root.querySelector("[data-pu-warn]");

  function out(name, text) {
    root.querySelectorAll('[data-out="' + name + '"]').forEach(function (el) { el.textContent = text; });
  }
  function fixed(x, digits) { return x.toFixed(digits).replace(".", ","); }
  function num(x) { return x < 100 ? fixed(x, 1) : String(Math.round(x)); }
  function kw(x) { return String(x).replace(".", ","); }
  // The first value of a series that covers x; the last one if none does.
  function up(series, x) {
    for (var i = 0; i < series.length; i++) if (series[i] >= x) return series[i];
    return series[series.length - 1];
  }

  function read() {
    return {
      voltage: parseInt(root.querySelector('input[name="voltage"]:checked').value, 10),
      load: parseFloat(root.querySelector('input[name="load"]').value),
      bore: parseInt(root.querySelector('input[name="bore"]').value, 10),
      stroke: parseFloat(root.querySelector('input[name="stroke"]').value),
      time: parseFloat(root.querySelector('input[name="time"]').value),
    };
  }

  // Pressure from the load on the piston, flow from the area and the speed, power from both
  // (N = p × Q / η), the tank about three minutes of flow and never less than the stroke's oil.
  function calc(v) {
    var D = data.bores[v.bore];
    var area = Math.PI * D * D / 4; // mm²
    var p = v.load * 9810 / area; // MPa
    var speed = v.stroke / v.time; // mm/s
    var q = area * speed * 60 / 1e6; // l/min
    var oil = area * v.stroke / 1e6; // l
    var need = p * q / 60 / data.efficiency; // kW
    var motor = up(data.motors, need);
    var tank = up(data.tanks, Math.max(3 * q, oil * 1.5));
    var days = data.days[data.days.length - 1][1];
    for (var i = 0; i < data.days.length; i++) if (motor <= data.days[i][0]) { days = data.days[i][1]; break; }
    return {
      D: D, p: p, q: q, speed: speed, oil: oil, motor: motor, tank: tank, days: days,
      over: p > data.pressure_max,
      tooBig: need > data.motors[data.motors.length - 1],
      single: v.voltage === 220 && motor > data.motor_max_220,
      pump: p > data.gear_pump_max ? "поршневой" : "шестерённый",
    };
  }

  function sync() {
    ranges.forEach(function (input) {
      var min = parseFloat(input.min), max = parseFloat(input.max);
      input.style.setProperty("--fill", ((input.value - min) / (max - min)) * 100 + "%");
    });
    var v = read(), c = calc(v);
    out("F", fixed(v.load, v.load % 1 ? 1 : 0) + " т");
    out("Fs", fixed(v.load, v.load % 1 ? 1 : 0));
    out("D", c.D + " мм");
    out("Dd", String(c.D));
    out("S", v.stroke + " мм");
    out("Sd", String(v.stroke));
    out("T", v.time + " с");
    out("P", num(c.p)); out("Ps", num(c.p));
    out("Q", num(c.q)); out("Qs", num(c.q));
    out("N", kw(c.motor)); out("Ns", kw(c.motor));
    out("V", String(c.tank)); out("Vs", String(c.tank));
    out("Speed", String(Math.round(c.speed)));
    out("Oil", c.oil < 1 ? fixed(c.oil, 2) : num(c.oil));
    out("Pump", c.pump);
    out("Days", String(c.days));
    out("M", "ГС-" + v.voltage);
    out("Code", [Math.round(c.p), Math.round(c.q), kw(c.motor), c.tank].join("."));
    // What the series can't do yet: said plainly, the figures stay to show how far off it is.
    var notes = [];
    if (c.over) notes.push("Давление выше " + data.pressure_max + " МПа — возьмите цилиндр большего диаметра.");
    if (c.tooBig) notes.push("Мощность больше " + kw(data.motors[data.motors.length - 1]) + " кВт — увеличьте время подъёма или рассчитаем индивидуально.");
    if (c.single) notes.push("От 220 В — моторы до " + kw(data.motor_max_220) + " кВт; для этой станции нужно 380 В.");
    warn.textContent = notes.join(" ");
    warn.hidden = !notes.length;
    root.classList.toggle("is-over", notes.length > 0);
  }

  root.addEventListener("input", sync);
  root.addEventListener("change", sync);
  sync();

  // Hand the chosen unit to the lead form; the link itself scrolls there.
  root.querySelector("[data-config-send]").addEventListener("click", function () {
    var field = document.getElementById("lead-message");
    if (!field) return;
    var v = read(), c = calc(v);
    var line = "Параметры гидростанции: нагрузка " + fixed(v.load, v.load % 1 ? 1 : 0) + " т, цилиндр Ø" + c.D +
      " мм, ход " + v.stroke + " мм за " + v.time + " с, питание " + v.voltage + " В — давление " + num(c.p) +
      " МПа, подача " + num(c.q) + " л/мин, мотор " + kw(c.motor) + " кВт, бак " + c.tank + " л.";
    var rest = field.value.replace(/^Параметры гидростанции:.*\n?/, "");
    field.value = line + (rest ? "\n" + rest : "");
    var name = document.getElementById("lead-name");
    if (name) setTimeout(function () { name.focus({ preventScroll: true }); }, 600);
    if (window.temirGoal) window.temirGoal("power_unit_config_sent");
  });
})();
