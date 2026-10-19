(function () {
  "use strict";

  var key = "theme-session";
  var media = window.matchMedia ? window.matchMedia("(prefers-color-scheme: dark)") : null;
  var system = systemTheme();
  var manual = readOverride();
  var button;

  function systemTheme() {
    return media && media.matches ? "dark" : "light";
  }

  function readOverride() {
    try {
      var saved = JSON.parse(sessionStorage.getItem(key));
      if (saved && saved.system === system && (saved.theme === "light" || saved.theme === "dark")) {
        return saved.theme;
      }
    } catch (error) { /* Use the system preference if storage is blocked or invalid. */ }
    return null;
  }

  function render() {
    var theme = manual || system;
    var action = theme === "dark" ? "Light" : "Dark";
    document.documentElement.setAttribute("data-theme", theme);
    if (!button) return;
    document.getElementById("theme-mode-icon").textContent = theme === "dark" ? "☀" : "☾";
    document.getElementById("theme-mode-label").textContent = action;
    button.setAttribute("aria-label", "Switch to " + action.toLowerCase() + " theme");
    button.setAttribute("title", "Switch to " + action.toLowerCase() + " theme");
  }

  function save() {
    try {
      if (manual) sessionStorage.setItem(key, JSON.stringify({ theme: manual, system: system }));
      else sessionStorage.removeItem(key);
    } catch (error) { /* The toggle and live system sync remain usable in memory. */ }
  }

  function synchronize() {
    var current = systemTheme();
    if (current !== system) {
      system = current;
      manual = null;
      save();
    }
    render();
  }

  // Ignore all permanent values from the previous three-mode implementation.
  try { localStorage.removeItem("theme"); } catch (error) { /* Storage is optional. */ }
  save();
  render(); // Executed inline in <head>, before the stylesheet.

  if (media) {
    if (media.addEventListener) media.addEventListener("change", synchronize);
    else if (media.addListener) media.addListener(synchronize);
  }
  window.addEventListener("pageshow", function (event) {
    if (event.persisted) {
      system = systemTheme();
      manual = readOverride();
    }
    synchronize();
  });
  document.addEventListener("visibilitychange", synchronize);
  document.addEventListener("DOMContentLoaded", function () {
    button = document.getElementById("theme-mode-toggle");
    if (!button) return;
    synchronize();
    button.addEventListener("click", function () {
      synchronize();
      manual = (manual || system) === "dark" ? "light" : "dark";
      save();
      render();
    });
    button.hidden = false;
  });
})();
