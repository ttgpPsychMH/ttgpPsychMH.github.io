(function () {
  "use strict";

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
    enhanceExternalLinks();
    initNavigation();
    initProfileMenu();

  });
})();
