// Product page tabs (includes/tabs_bar.html). Without JS the bar is a list of anchors and
// every section is on the page; here only the chosen one is shown. The address keeps the
// tab (#harakteristiki), so a link to it or a reload opens the same tab.
(function () {
  "use strict";

  var root = document.querySelector("[data-tabs]");
  if (!root) return;
  var bar = root.querySelector(".page-nav");
  var list = root.querySelector("[data-tabs-list]");
  var panelsBox = root.querySelector("[data-tabs-panels]");
  var tabs = Array.prototype.slice.call(root.querySelectorAll("[data-tab]"));
  var panels = tabs.map(function (tab) { return document.getElementById(tab.hash.slice(1)); });
  if (!bar || !list || !panelsBox || panels.indexOf(null) !== -1) return;

  list.setAttribute("role", "tablist");
  tabs.forEach(function (tab, i) {
    tab.parentNode.setAttribute("role", "presentation");
    tab.setAttribute("role", "tab");
    tab.id = "tab-" + panels[i].id;
    tab.setAttribute("aria-controls", panels[i].id);
    panels[i].setAttribute("role", "tabpanel");
    panels[i].setAttribute("aria-labelledby", tab.id);
  });

  var current = -1;
  function select(i) {
    if (i === current) return;
    current = i;
    tabs.forEach(function (tab, j) {
      var on = j === i;
      tab.setAttribute("aria-selected", on ? "true" : "false");
      tab.tabIndex = on ? 0 : -1;
      tab.classList.toggle("is-active", on);
      panels[j].hidden = !on;
    });
    // Scroll-revealed blocks of a panel that was hidden would wait for a scroll that already happened.
    panels[i].querySelectorAll(".reveal").forEach(function (el) { el.classList.add("is-visible"); });
  }

  // Which tab holds this element (the panel itself or something inside it)?
  function tabOf(el) {
    for (var i = 0; el && i < panels.length; i++) if (panels[i].contains(el)) return i;
    return -1;
  }

  // Switched while scrolled down into a long tab: bring the start of the new one under the bar.
  function toPanels() {
    if (panelsBox.getBoundingClientRect().top < bar.getBoundingClientRect().bottom - 1) {
      panelsBox.scrollIntoView({ block: "start" });
    }
  }

  function open(i, focus) {
    select(i);
    history.replaceState(null, "", "#" + panels[i].id);
    toPanels();
    if (focus) tabs[i].focus();
  }

  tabs.forEach(function (tab, i) {
    tab.addEventListener("click", function (event) {
      if (event.ctrlKey || event.metaKey || event.shiftKey) return;
      event.preventDefault();
      open(i, false);
    });
    tab.addEventListener("keydown", function (event) {
      var to = { ArrowRight: i + 1, ArrowLeft: i - 1, Home: 0, End: tabs.length - 1 }[event.key];
      if (to === undefined) return;
      event.preventDefault();
      open((to + tabs.length) % tabs.length, true);
    });
  });

  // Any other link to a section inside a closed tab opens that tab first;
  // the browser then scrolls to the target as usual.
  document.addEventListener("click", function (event) {
    var link = event.target.closest && event.target.closest('a[href^="#"]');
    if (!link || link.hasAttribute("data-tab") || link.hash.length < 2) return;
    var i = tabOf(document.getElementById(link.hash.slice(1)));
    if (i !== -1) select(i);
  }, true);

  function fromHash() {
    var target = location.hash.length > 1 ? document.getElementById(location.hash.slice(1)) : null;
    var i = tabOf(target);
    select(i !== -1 ? i : Math.max(current, 0));
    if (i !== -1 && target !== panels[i]) target.scrollIntoView();
  }
  window.addEventListener("hashchange", fromHash);
  fromHash();
})();
