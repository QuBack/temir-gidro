// Shared bits of the mockups: a click on a [data-zoom] link opens the picture full screen.
document.addEventListener("click", (e) => {
  const a = e.target.closest("[data-zoom]");
  if (!a) return;
  e.preventDefault();
  const box = document.createElement("div");
  box.className = "lb";
  const img = document.createElement("img");
  img.src = a.getAttribute("href");
  img.alt = a.querySelector("img")?.alt || "";
  box.append(img);
  if (img.alt) {
    const p = document.createElement("p");
    p.textContent = img.alt;
    box.append(p);
  }
  const close = () => box.remove();
  box.addEventListener("click", close);
  document.addEventListener("keydown", (k) => k.key === "Escape" && close(), { once: true });
  document.body.append(box);
});
