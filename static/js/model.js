// Model page: photo gallery, kit callouts, request sliders. All content is
// server-rendered; this file only adds interaction.
(function () {
  "use strict";

  // ---------- Gallery: thumbnails switch the main picture ----------
  var gallery = document.querySelector("[data-gallery]");
  if (gallery) {
    var slides = gallery.querySelectorAll("[data-slide]");
    var thumbs = gallery.querySelectorAll("[data-thumb]");
    thumbs.forEach(function (thumb) {
      thumb.addEventListener("click", function (event) {
        event.preventDefault();
        var index = parseInt(thumb.dataset.thumb, 10);
        slides.forEach(function (slide, i) { slide.hidden = i !== index; });
        thumbs.forEach(function (t) { t.classList.toggle("is-active", t === thumb); });
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
