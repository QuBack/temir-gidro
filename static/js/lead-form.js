// Progressive enhancement: without JS the form posts normally and redirects to
// the thank-you page; with JS it submits in place and reports a Metrika goal.
(function () {
  "use strict";

  function renderErrors(form, errors) {
    form.querySelectorAll(".errorlist[data-js]").forEach(function (el) { el.remove(); });
    Object.keys(errors).forEach(function (name) {
      var list = document.createElement("ul");
      list.className = "errorlist";
      list.dataset.js = "";
      errors[name].forEach(function (err) {
        var li = document.createElement("li");
        li.textContent = err.message;
        list.appendChild(li);
      });
      var input = form.elements[name];
      var target = name === "__all__" || !input
        ? form.querySelector("[data-lead-form-errors]")
        : input.closest(".field");
      target.appendChild(list);
    });
    var first = form.querySelector(".errorlist[data-js]");
    if (first) first.scrollIntoView({ block: "center" });
  }

  document.querySelectorAll("[data-lead-form]").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var button = form.querySelector("button[type=submit]");
      button.disabled = true;

      fetch(form.action, {
        method: "POST",
        body: new FormData(form),
        headers: { Accept: "application/json" },
        credentials: "same-origin",
      })
        .then(function (response) { return response.json(); })
        .then(function (data) {
          if (data.ok) {
            form.querySelectorAll(".field, button, [data-lead-form-errors]").forEach(function (el) { el.hidden = true; });
            form.querySelector("[data-lead-form-success]").hidden = false;
            if (window.temirGoal) window.temirGoal("lead_sent");
          } else {
            renderErrors(form, data.errors || {});
            button.disabled = false;
          }
        })
        .catch(function () {
          // Network or JSON failure: fall back to a regular submission.
          form.submit();
        });
    });
  });
})();
