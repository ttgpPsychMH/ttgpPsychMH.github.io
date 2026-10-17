(function () {
  "use strict";

  const THEME_KEY = "theme";
  const THEME_MODES = ["system", "light", "dark"];
  const systemTheme = window.matchMedia
    ? window.matchMedia("(prefers-color-scheme: dark)")
    : null;

  function getThemePreference() {
    let saved;
    try { saved = localStorage.getItem(THEME_KEY); } catch (error) { return "system"; }
    return THEME_MODES.includes(saved) ? saved : "system";
  }

  function resolveTheme(preference) {
    if (preference === "light" || preference === "dark") return preference;
    return systemTheme && systemTheme.matches ? "dark" : "light";
  }

  function updateThemeControl(preference) {
    const button = document.getElementById("theme-mode-toggle");
    const icon = document.getElementById("theme-mode-icon");
    const label = document.getElementById("theme-mode-label");
    if (!button || !icon || !label) return;

    const config = {
      system: { symbol: "◐", label: "System" },
      light: { symbol: "☀", label: "Light" },
      dark: { symbol: "☾", label: "Dark" }
    }[preference];

    icon.className = "theme-switch__icon";
    icon.textContent = config.symbol;
    label.textContent = config.label;
    button.setAttribute(
      "aria-label",
      "Theme: " + config.label + ". Click to change theme."
    );
    button.setAttribute(
      "title",
      "Theme: " + config.label + " · click to change"
    );
  }

  function applyTheme(preference, persist) {
    const mode = THEME_MODES.includes(preference) ? preference : "system";
    const resolved = resolveTheme(mode);

    if (persist) {
      try { localStorage.setItem(THEME_KEY, mode); } catch (error) { /* Keep the in-memory theme usable. */ }
    }
    document.documentElement.setAttribute("data-theme-preference", mode);

    if (resolved === "dark") {
      document.documentElement.setAttribute("data-theme", "dark");
    } else {
      document.documentElement.removeAttribute("data-theme");
    }

    updateThemeControl(mode);
  }

  function cycleTheme() {
    const current = document.documentElement.getAttribute("data-theme-preference") || getThemePreference();
    const next = THEME_MODES[(THEME_MODES.indexOf(current) + 1) % THEME_MODES.length];

    applyTheme(next, true);
  }

  function enhanceExternalLinks() {
    document.querySelectorAll('a[href^="http"]').forEach(function (link) {
      link.setAttribute("rel", "noopener noreferrer");
    });
  }

  function closeNavigation() {
    const nav = document.getElementById("site-nav");
    const toggle = document.getElementById("site-nav-toggle");
    if (!nav || !toggle) return;

    nav.classList.remove("is-open");
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-label", "Open navigation menu");
  }

  function toggleNavigation() {
    const nav = document.getElementById("site-nav");
    const toggle = document.getElementById("site-nav-toggle");
    if (!nav || !toggle) return;

    const open = !nav.classList.contains("is-open");
    nav.classList.toggle("is-open", open);
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    toggle.setAttribute(
      "aria-label",
      open ? "Close navigation menu" : "Open navigation menu"
    );
    if (open) {
      const firstLink = nav.querySelector(".site-nav__link");
      if (firstLink) firstLink.focus();
    }
  }

  function initNavigation() {
    const nav = document.getElementById("site-nav");
    const toggle = document.getElementById("site-nav-toggle");
    if (!nav || !toggle) return;

    toggle.addEventListener("click", toggleNavigation);

    nav.querySelectorAll(".site-nav__link, .site-nav__brand").forEach(function (link) {
      link.addEventListener("click", closeNavigation);
    });

    document.addEventListener("click", function (event) {
      if (nav.classList.contains("is-open") && !nav.contains(event.target)) {
        closeNavigation();
      }
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && nav.classList.contains("is-open")) {
        closeNavigation();
        toggle.focus();
      }
    });

    window.addEventListener(
      "resize",
      function () {
        if (window.innerWidth > 900) closeNavigation();
      },
      { passive: true }
    );
  }

  function initProfileMenu() {
    const button = document.querySelector(
      '[aria-controls="author-profile-links"]'
    );
    const wrapper = button ? button.closest(".author__urls-wrapper") : null;
    if (!button || !wrapper) return;

    button.addEventListener("click", function () {
      const open = !wrapper.classList.contains("is-open");
      wrapper.classList.toggle("is-open", open);
      button.setAttribute("aria-expanded", open ? "true" : "false");
    });

    document.addEventListener("click", function (event) {
      if (
        wrapper.classList.contains("is-open") &&
        !wrapper.contains(event.target)
      ) {
        wrapper.classList.remove("is-open");
        button.setAttribute("aria-expanded", "false");
      }
    });

    window.addEventListener(
      "resize",
      function () {
        if (window.innerWidth >= 925) {
          wrapper.classList.remove("is-open");
          button.setAttribute("aria-expanded", "false");
        }
      },
      { passive: true }
    );
  }

  document.addEventListener("DOMContentLoaded", function () {
    applyTheme(getThemePreference(), false);
    enhanceExternalLinks();
    initNavigation();
    initProfileMenu();


    const themeButton = document.getElementById("theme-mode-toggle");
    if (themeButton) themeButton.addEventListener("click", cycleTheme);
  });

  if (systemTheme) {
    const systemChange = function () {
      if (document.documentElement.getAttribute("data-theme-preference") === "system") applyTheme("system", false);
    };

    if (systemTheme.addEventListener) {
      systemTheme.addEventListener("change", systemChange);
    } else if (systemTheme.addListener) {
      systemTheme.addListener(systemChange);
    }
  }
})();