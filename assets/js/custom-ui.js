(function () {
  "use strict";

  const THEME_KEY = "theme";
  const MODES = ["system", "light", "dark"];
  const media = window.matchMedia ? window.matchMedia("(prefers-color-scheme: dark)") : null;

  function getPreference() {
    const saved = localStorage.getItem(THEME_KEY);
    return MODES.includes(saved) ? saved : "system";
  }

  function resolvedTheme(preference) {
    if (preference === "dark" || preference === "light") return preference;
    return media && media.matches ? "dark" : "light";
  }

  function updateThemeControl(preference) {
    const button = document.getElementById("theme-mode-toggle");
    const icon = document.getElementById("theme-mode-icon");
    const label = document.getElementById("theme-mode-label");
    if (!button || !icon || !label) return;

    const config = {
      system: { icon: "fa-desktop", label: "System" },
      light:  { icon: "fa-sun", label: "Light" },
      dark:   { icon: "fa-moon", label: "Dark" }
    }[preference];

    icon.className = "fa-solid " + config.icon;
    label.textContent = config.label;
    button.setAttribute("aria-label", "Theme: " + config.label + ". Click to change theme.");
    button.setAttribute("title", "Theme: " + config.label + " · click to change");
  }

  function applyTheme(preference, persist) {
    const mode = MODES.includes(preference) ? preference : "system";
    const resolved = resolvedTheme(mode);

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
    const current = getPreference();
    const next = MODES[(MODES.indexOf(current) + 1) % MODES.length];
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
    const headings = document.querySelectorAll(".page__title, .page__content h2, .archive h2");
    headings.forEach(function (heading) {
      if (heading.querySelector(".heading-icon")) return;
      const text = heading.textContent.trim();
      if (!text) return;

      const span = document.createElement("span");
      span.className = "heading-icon";
      span.setAttribute("aria-hidden", "true");

      const icon = document.createElement("i");
      icon.className = "fa-solid " + iconForHeading(text);
      span.appendChild(icon);
      heading.prepend(span);
    });
  }

  function routeClass() {
    let path = window.location.pathname.replace(/^\/+|\/+$/g, "");
    if (!path) path = "home";
    document.body.classList.add("route-" + path.replace(/[^a-zA-Z0-9]+/g, "-").toLowerCase());
  }

  function wrapHomepageSections() {
    if (window.location.pathname !== "/" && window.location.pathname !== "/index.html") return;
    const content = document.querySelector(".page__content");
    if (!content) return;

    const children = Array.from(content.children);
    let section = null;
    let index = 0;

    children.forEach(function (node) {
      if (node.tagName === "H2") {
        index += 1;
        section = document.createElement("section");
        section.className = "home-section home-section--" + (((index - 1) % 5) + 1);
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
        card.className = "project-card project-card--" + (((index - 1) % 5) + 1);
        content.insertBefore(card, node);
        card.appendChild(node);
      } else if (card) {
        card.appendChild(node);
      }
    });
  }

  function wrapPublicationEntries() {
    if (!window.location.pathname.startsWith("/publications")) return;
    const content = document.querySelector(".page__content");
    if (!content) return;

    const children = Array.from(content.children);
    let inSection = false;
    let card = null;

    children.forEach(function (node) {
      if (node.tagName === "H2") {
        inSection = true;
        card = null;
        return;
      }
      if (!inSection || node.tagName !== "P") return;

      const text = node.textContent.trim();
      const indexing = /^(Indexed in|Journal indexed in)/i.test(text);

      if (indexing && card) {
        node.classList.add("publication-indexing");
        card.appendChild(node);
        return;
      }

      card = document.createElement("article");
      card.className = "publication-card";
      content.insertBefore(card, node);
      node.classList.add("publication-citation");
      card.appendChild(node);
    });
  }

  function enhanceExternalLinks() {
    document.querySelectorAll('.page__content a[href^="http"]').forEach(function (link) {
      link.setAttribute("rel", "noopener noreferrer");
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    applyTheme(getPreference(), false);
    routeClass();
    wrapHomepageSections();
    wrapProjectSections();
    wrapPublicationEntries();
    addHeadingIcons();
    enhanceExternalLinks();

    const button = document.getElementById("theme-mode-toggle");
    if (button) button.addEventListener("click", cycleTheme);
  });

  if (media) {
    const systemChange = function () {
      if (getPreference() === "system") applyTheme("system", false);
    };
    if (media.addEventListener) media.addEventListener("change", systemChange);
    else if (media.addListener) media.addListener(systemChange);
  }
})();