// 3D model of a lift (model page): the render in the «3D-модель» block switches to
// <model-viewer> on request. Nothing heavy loads with the page: the viewer
// (~1 MB, static/vendor/model-viewer) and the model (~3 MB, Draco-compressed GLB)
// are fetched on the first click. The Draco decoder is served from our static
// (static/vendor/draco) — CSP allows no third-party scripts.
(function () {
  "use strict";

  var script = document.currentScript;
  var hosts = document.querySelectorAll("[data-model3d]");
  if (!script || !hosts.length || !("customElements" in window)) return;

  var motion = !window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var viewerReady = null;

  function loadViewer() {
    if (!viewerReady) {
      // The viewer reads its settings from this global when its module runs.
      window.ModelViewerElement = window.ModelViewerElement || {};
      window.ModelViewerElement.dracoDecoderLocation = script.dataset.draco;
      viewerReady = new Promise(function (resolve, reject) {
        var tag = document.createElement("script");
        tag.type = "module";
        tag.src = script.dataset.viewer;
        tag.onerror = reject;
        document.head.appendChild(tag);
        customElements.whenDefined("model-viewer").then(resolve);
      });
    }
    return viewerReady;
  }

  function createViewer(host) {
    var mv = document.createElement("model-viewer");
    mv.className = "model3d-viewer";
    mv.setAttribute("src", host.dataset.model3d);
    mv.setAttribute("alt", host.dataset.model3dAlt || "");
    mv.setAttribute("camera-controls", "");
    mv.setAttribute("touch-action", "pan-y");           // vertical swipes still scroll the page
    mv.setAttribute("interaction-prompt", "none");
    mv.setAttribute("environment-image", "neutral");
    mv.setAttribute("shadow-intensity", "1");
    mv.setAttribute("shadow-softness", "0.8");
    mv.setAttribute("camera-orbit", "60deg 78deg auto");   // three-quarter view, as on the renders
    mv.setAttribute("max-camera-orbit", "auto 95deg auto");  // not under the floor
    if (motion) {
      mv.setAttribute("auto-rotate", "");
      mv.setAttribute("auto-rotate-delay", "3000");
      mv.setAttribute("rotation-per-second", "12deg");
    }
    host.appendChild(mv);
    return mv;
  }

  hosts.forEach(function (host) {
    var toggle = host.querySelector("[data-model3d-toggle]");
    if (!toggle) return;
    var label = toggle.querySelector("[data-model3d-label]");
    var label3d = label.textContent;
    var viewer = null;

    var block = host.closest(".model-3d");
    if (block) block.hidden = false;
    toggle.hidden = false;

    function show3d(on) {
      host.classList.toggle("is-3d", on);
      label.textContent = on ? toggle.dataset.labelPhoto : label3d;
    }

    function busy(on) {
      toggle.disabled = on;
      toggle.setAttribute("aria-busy", on ? "true" : "false");
    }

    toggle.addEventListener("click", function () {
      if (host.classList.contains("is-3d")) { show3d(false); return; }
      if (viewer) { show3d(true); return; }
      busy(true);
      loadViewer().then(function () {
        viewer = createViewer(host);
        viewer.addEventListener("load", function () { busy(false); show3d(true); }, { once: true });
        viewer.addEventListener("error", function () {
          busy(false);
          viewer.remove();
          viewer = null;
        }, { once: true });
      }, function () { busy(false); });
    });
  });
})();
