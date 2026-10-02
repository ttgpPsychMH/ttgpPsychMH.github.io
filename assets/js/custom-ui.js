(function () {
  "use strict";

  const THEME_KEY = "theme";
  const THEME_MODES = ["system", "light", "dark"];
  const systemTheme = window.matchMedia
    ? window.matchMedia("(prefers-color-scheme: dark)")
    : null;

  function getThemePreference() {
    const saved = localStorage.getItem(THEME_KEY);
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
      system: { icon: "fa-desktop", label: "System" },
      light: { icon: "fa-sun", label: "Light" },
      dark: { icon: "fa-moon", label: "Dark" }
    }[preference];

    icon.className = "fa-solid " + config.icon;
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

    if (persist) localStorage.setItem(THEME_KEY, mode);
    document.documentElement.setAttribute("data-theme-preference", mode);

    if (resolved === "dark") {
      document.documentElement.setAttribute("data-theme", "dark");
    } else {
      document.documentElement.removeAttribute("data-theme");
    }

    updateThemeControl(mode);
  }

  function cycleTheme() {
    const current = getThemePreference();
    const next = THEME_MODES[(THEME_MODES.indexOf(current) + 1) % THEME_MODES.length];

    document.documentElement.classList.add("theme-changing");
    applyTheme(next, true);
    window.setTimeout(function () {
      document.documentElement.classList.remove("theme-changing");
    }, 260);
  }

  function iconForHeading(text) {
    const value = text.trim();

    if (/^20\d{2}$/.test(value)) return "fa-calendar-days";
    if (/education|qualification/i.test(value)) return "fa-graduation-cap";
    if (/personal information/i.test(value)) return "fa-id-card";
    if (/research interest|research area|research overview/i.test(value)) return "fa-flask-vial";
    if (/method|expertise/i.test(value)) return "fa-chart-line";
    if (/research laboratory|research lab/i.test(value)) return "fa-microscope";
    if (/research experience/i.test(value)) return "fa-magnifying-glass-chart";
    if (/publication|ongoing work/i.test(value)) return "fa-book-open";
    if (/conference paper|conference service/i.test(value)) return "fa-people-group";
    if (/project/i.test(value)) return "fa-diagram-project";
    if (/work experience|appointment/i.test(value)) return "fa-briefcase";
    if (/honor|award/i.test(value)) return "fa-trophy";
    if (/membership/i.test(value)) return "fa-user-group";
    if (/certification|training/i.test(value)) return "fa-certificate";
    if (/language/i.test(value)) return "fa-language";
    if (/academic service|reviewer/i.test(value)) return "fa-pen-to-square";
    if (/contact|email/i.test(value)) return "fa-envelope";
    if (/academic profile/i.test(value)) return "fa-address-card";
    if (/current direction/i.test(value)) return "fa-compass";
    return "fa-leaf";
  }

  function addHeadingIcons() {
    const headings = document.querySelectorAll(
      ".page__title, .page__content h2, .archive h2"
    );

    headings.forEach(function (heading) {
      if (heading.querySelector(".heading-icon")) return;
      const text = heading.textContent.trim();
      if (!text) return;

      const badge = document.createElement("span");
      badge.className = "heading-icon";
      badge.setAttribute("aria-hidden", "true");

      const icon = document.createElement("i");
      icon.className = "fa-solid " + iconForHeading(text);
      badge.appendChild(icon);
      heading.prepend(badge);
    });
  }

  function wrapHomepageSections() {
    if (window.location.pathname !== "/" && window.location.pathname !== "/index.html") {
      return;
    }

    const content = document.querySelector(".page__content");
    if (!content) return;

    const children = Array.from(content.children);
    let section = null;
    let index = 0;

    children.forEach(function (node) {
      if (node.tagName === "H2") {
        index += 1;
        section = document.createElement("section");
        section.className =
          "home-section home-section--" + (((index - 1) % 5) + 1);
        content.insertBefore(section, node);
        section.appendChild(node);
      } else if (section) {
        section.appendChild(node);
      }
    });
  }

  function wrapProjectSections() {
    if (!window.location.pathname.startsWith("/projects")) return;

    const content = document.querySelector(".page__content");
    if (!content) return;

    const children = Array.from(content.children);
    let card = null;
    let index = 0;

    children.forEach(function (node) {
      if (node.tagName === "H2") {
        index += 1;
        card = document.createElement("section");
        card.className =
          "project-card project-card--" + (((index - 1) % 5) + 1);
        content.insertBefore(card, node);
        card.appendChild(node);
      } else if (card) {
        card.appendChild(node);
      }
    });
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
      if (event.key === "Escape") closeNavigation();
    });

    window.addEventListener(
      "resize",
      function () {
        if (window.innerWidth >= 1024) closeNavigation();
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

  function syncStickyLayout() {
    const masthead = document.querySelector(".masthead");
    if (!masthead) return;

    const mastheadHeight = Math.ceil(masthead.getBoundingClientRect().height);
    document.documentElement.style.setProperty(
      "--sticky-sidebar-top",
      mastheadHeight + 14 + "px"
    );

    masthead.classList.toggle("is-stuck", window.scrollY > 8);
  }

  document.addEventListener("DOMContentLoaded", function () {
    applyTheme(getThemePreference(), false);
    wrapHomepageSections();
    wrapProjectSections();
    addHeadingIcons();
    enhanceExternalLinks();
    initNavigation();
    initProfileMenu();
    syncStickyLayout();

    window.addEventListener("resize", syncStickyLayout, { passive: true });
    window.addEventListener("scroll", syncStickyLayout, { passive: true });

    const themeButton = document.getElementById("theme-mode-toggle");
    if (themeButton) themeButton.addEventListener("click", cycleTheme);
  });

  if (systemTheme) {
    const systemChange = function () {
      if (getThemePreference() === "system") applyTheme("system", false);
    };

    if (systemTheme.addEventListener) {
      systemTheme.addEventListener("change", systemChange);
    } else if (systemTheme.addListener) {
      systemTheme.addListener(systemChange);
    }
  }
})();