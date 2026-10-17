/* Run against an already-built local site; see docs/redesign/verification.md. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');

const base = process.env.SITE_TEST_URL || 'http://127.0.0.1:4010';
const output = path.resolve(__dirname, '../docs/redesign/previews');
const widths = [1440, 1024, 768, 390, 320];
const routes = ['/', '/research/', '/publications/', '/projects/', '/cv/', '/contact/'];

function luminance(rgb) {
  const channels = rgb.match(/[\d.]+/g).slice(0, 3).map(Number).map(n => {
    const c = n / 255;
    return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
  });
  return channels[0] * 0.2126 + channels[1] * 0.7152 + channels[2] * 0.0722;
}

(async () => {
  fs.mkdirSync(output, { recursive: true });
  const browser = await chromium.launch({
    executablePath: process.env.CHROMIUM_PATH || undefined,
    headless: true,
    args: ['--no-sandbox']
  });
  const report = { routes: 0, widths, themes: [], interactions: [] };
  try {
    for (const width of widths) {
      const context = await browser.newContext({ viewport: { width, height: 1000 }, colorScheme: 'light' });
      const page = await context.newPage();
      const errors = [];
      page.on('pageerror', e => errors.push(e.message));
      page.on('response', response => {
        if (response.url().startsWith(base) && response.status() >= 400) errors.push(`${response.status()} ${response.url()}`);
      });
      for (const route of routes) {
        const response = await page.goto(base + route, { waitUntil: 'networkidle' });
        assert.equal(response.status(), 200, route);
        assert.equal(await page.locator('h1').count(), 1, `${route}: H1`);
        assert.equal(await page.locator('nav[aria-label="Primary navigation"] [aria-current="page"]').count(), 1);
        const layout = await page.evaluate(() => ({
          viewport: window.innerWidth,
          width: document.documentElement.scrollWidth,
          font: parseFloat(getComputedStyle(document.body).fontSize),
          fontFamily: getComputedStyle(document.body).fontFamily,
          images: [...document.querySelectorAll('#main img')].every(image => image.complete && image.naturalWidth > 0)
        }));
        assert.ok(layout.width <= layout.viewport + 1, `${route} overflows at ${width}: ${layout.width}`);
        assert.ok(!layout.fontFamily.includes("Times New Roman"), `${route}: stylesheet did not apply`);
        assert.ok(layout.font >= 16, `${route}: body text is too small`);
        assert.ok(layout.images, `${route}: profile image failed to load`);
        if (route === '/cv/') {
          for (const button of await page.locator('.cv-actions .btn').all()) {
            const colors = await button.evaluate(x => ({
              foreground: getComputedStyle(x).color,
              background: getComputedStyle(document.body).backgroundColor
            }));
            const values = [luminance(colors.foreground), luminance(colors.background)].sort((a, b) => a - b);
            assert.ok((values[1] + 0.05) / (values[0] + 0.05) >= 4.5, 'CV download/open link contrast');
          }
        }
        if (route === '/') {
          assert.equal(await page.locator('.home-portrait img').count(), 1);
          assert.equal(await page.locator('.heading-icon, .home-section').count(), 0);
          await page.screenshot({ path: path.join(output, `homepage-${width}.png`), fullPage: true });
          if ([1440, 390].includes(width)) await page.screenshot({ path: path.join(output, `homepage-${width}-viewport.png`) });
        }
        report.routes++;
      }
      assert.deepEqual(errors, [], `Browser errors at ${width}`);
      await context.close();
    }

    const context = await browser.newContext({ viewport: { width: 390, height: 844 }, colorScheme: 'light' });
    const page = await context.newPage();
    await page.goto(base, { waitUntil: 'networkidle' });
    await page.keyboard.press('Tab');
    assert.equal(await page.locator('.skip-link').evaluate(x => document.activeElement === x), true);
    await page.keyboard.press('Enter');
    assert.equal(await page.locator('#main').evaluate(x => x.contains(document.activeElement) || document.activeElement === x), true);
    const toggle = page.locator('#site-nav-toggle');
    await toggle.focus();
    await page.keyboard.press('Enter');
    assert.equal(await toggle.getAttribute('aria-expanded'), 'true');
    assert.ok(await page.locator('.site-nav__link').first().isVisible());
    assert.ok(await page.locator('.site-nav__link').first().evaluate(x => x === document.activeElement));
    await page.screenshot({ path: path.join(output, 'mobile-menu.png') });
    await page.keyboard.press('Tab');
    await page.keyboard.press('Escape');
    assert.equal(await toggle.getAttribute('aria-expanded'), 'false');
    assert.ok(await toggle.evaluate(x => document.activeElement === x));
    await toggle.click();
    await page.locator('.home-intro').click();
    assert.equal(await toggle.getAttribute('aria-expanded'), 'false');
    await toggle.click();
    await page.locator('.site-nav__link[href$="/research/"]').click();
    assert.ok(page.url().endsWith('/research/'));
    assert.equal(await toggle.getAttribute('aria-expanded'), 'false');
    report.interactions.push('skip link', 'keyboard menu', 'Escape returns focus', 'outside click', 'menu link');

    await page.goto(base, { waitUntil: 'networkidle' });
    const theme = page.locator('#theme-mode-toggle');
    for (const mode of ['light', 'dark', 'system']) {
      await theme.click();
      assert.equal(await page.locator('html').getAttribute('data-theme-preference'), mode);
      const contrast = await page.evaluate(() => {
        const text = getComputedStyle(document.body);
        const link = getComputedStyle(document.querySelector('.home-profile-links a'));
        return { text: text.color, background: text.backgroundColor, link: link.color };
      });
      for (const foreground of [contrast.text, contrast.link]) {
        const values = [luminance(foreground), luminance(contrast.background)].sort((a, b) => a - b);
        assert.ok((values[1] + 0.05) / (values[0] + 0.05) >= 4.5, `${mode}: contrast`);
      }
      if (mode === 'dark') await page.screenshot({ path: path.join(output, 'homepage-dark-390.png') });
      await page.reload({ waitUntil: 'networkidle' });
      assert.equal(await page.locator('html').getAttribute('data-theme-preference'), mode);
      report.themes.push(mode);
    }
    await page.emulateMedia({ colorScheme: 'dark' });
    await page.waitForFunction(() => document.documentElement.getAttribute('data-theme') === 'dark');
    await page.emulateMedia({ colorScheme: 'light' });
    await page.waitForFunction(() => document.documentElement.getAttribute('data-theme') === null);
    await context.close();

    const noJS = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 320, height: 900 } });
    const noJSPage = await noJS.newPage();
    await noJSPage.goto(base);
    for (const link of await noJSPage.locator('.site-nav__link').all()) assert.ok(await link.isVisible());
    await noJS.close();
    report.interactions.push('navigation without JavaScript', 'system theme changes', 'theme persistence');

    const noStorage = await browser.newContext({ viewport: { width: 390, height: 844 } });
    await noStorage.addInitScript(() => Object.defineProperty(window, 'localStorage', { get() { throw new Error('Storage disabled'); } }));
    const noStoragePage = await noStorage.newPage();
    const storageErrors = [];
    noStoragePage.on('pageerror', e => storageErrors.push(e.message));
    await noStoragePage.goto(base, { waitUntil: 'networkidle' });
    await noStoragePage.locator('#theme-mode-toggle').click();
    await noStoragePage.locator('#theme-mode-toggle').click();
    assert.equal(await noStoragePage.locator('html').getAttribute('data-theme'), 'dark');
    await noStoragePage.locator('#site-nav-toggle').click();
    assert.equal(await noStoragePage.locator('#site-nav-toggle').getAttribute('aria-expanded'), 'true');
    assert.deepEqual(storageErrors, []);
    await noStorage.close();
    report.interactions.push('navigation and theme with blocked storage');
    fs.writeFileSync(path.resolve(output, '../browser-results.json'), JSON.stringify(report, null, 2) + '\n');
    console.log(`BROWSER QA PASSED: ${report.routes} page/viewport checks, three themes, keyboard/menu/storage checks.`);
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
