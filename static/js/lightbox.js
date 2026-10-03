// Full-screen photo viewer. A photo opts in by being wrapped in
// <a href="<largest image>" data-zoom="<group>">: without JS the link just opens
// the picture. Photos of one group (a gallery, a page's scenes) are browsed
// with the arrows. The dialog markup is server-rendered (includes/lightbox.html).
(function () {
  "use strict";

  var dialog = document.querySelector("[data-lightbox]");
  var links = document.querySelectorAll("a[data-zoom]");
  if (!dialog || !links.length || typeof dialog.showModal !== "function") return;

  var image = dialog.querySelector("[data-lightbox-img]");
  var caption = dialog.querySelector("[data-lightbox-caption]");
  var prev = dialog.querySelector("[data-lightbox-prev]");
  var next = dialog.querySelector("[data-lightbox-next]");
  var group = [];
  var index = 0;

  function show(i) {
    index = (i + group.length) % group.length;
    var link = group[index];
    var thumb = link.querySelector("img");
    image.src = link.href;
    image.alt = thumb ? thumb.alt : "";
    caption.textContent = image.alt;
    prev.hidden = next.hidden = group.length < 2;
  }

  links.forEach(function (link) {
    link.addEventListener("click", function (event) {
      if (event.ctrlKey || event.metaKey || event.shiftKey) return; // new tab as usual
      event.preventDefault();
      group = Array.prototype.filter.call(links, function (l) { return l.dataset.zoom === link.dataset.zoom; });
      show(group.indexOf(link));
      dialog.showModal();
    });
  });

  prev.addEventListener("click", function () { show(index - 1); });
  next.addEventListener("click", function () { show(index + 1); });
  dialog.addEventListener("keydown", function (event) {
    if (group.length < 2) return;
    if (event.key === "ArrowLeft") show(index - 1);
    if (event.key === "ArrowRight") show(index + 1);
  });
  // A click on the dark area around the photo closes the viewer.
  dialog.addEventListener("click", function (event) {
    if (event.target === dialog || event.target.hasAttribute("data-lightbox-stage")) dialog.close();
  });
  dialog.addEventListener("close", function () { image.removeAttribute("src"); });
})();
