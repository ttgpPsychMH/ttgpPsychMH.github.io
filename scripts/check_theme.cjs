/* Theme-policy browser regressions, run by check_ui.cjs. */
const assert = require('node:assert/strict');
const path = require('node:path');

const backgrounds = { light: 'rgb(253, 253, 253)', dark: 'rgb(25, 27, 30)' };

async function expectTheme(page, mode) {
  await page.waitForFunction(({ mode, background }) => document.documentElement && document.body &&
    document.documentElement.dataset.theme === mode && getComputedStyle(document.body).backgroundColor === background,
  { mode, background: backgrounds[mode] });
  assert.equal(await page.locator('body').evaluate(x => getComputedStyle(x).backgroundColor), backgrounds[mode]);
  assert.equal(await page.locator('html').evaluate(x => getComputedStyle(x).colorScheme), mode);
  const action = mode === 'dark' ? 'light' : 'dark';
  const button = page.getByRole('button', { name: `Switch to ${action} theme`, exact: true });
  await button.waitFor({ state: 'visible' });
  assert.ok(await button.isVisible());
  assert.equal(await button.getAttribute('title'), `Switch to ${action} theme`);
  assert.equal(await button.getAttribute('type'), 'button');
  assert.equal(await button.locator('#theme-mode-icon').textContent(), mode === 'dark' ? '☀' : '☾');
  assert.equal(await page.locator('[data-theme-preference]').count(), 0);
}

function luminance(rgb) {
  return rgb.match(/[\d.]+/g).slice(0, 3).map(Number).map(n => {
    const c = n / 255;
    return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
  }).reduce((sum, c, i) => sum + c * [0.2126, 0.7152, 0.0722][i], 0);
}

module.exports = async function checkThemes(browser, base, output) {
  const checks = [];

  // Hold the deferred UI script so DOMContentLoaded cannot repair a late theme.
  // Record every styled animation frame, including frames before that event.
  for (const initial of [
    { system: 'light', mode: 'light' }, { system: 'dark', mode: 'dark' },
    { system: 'light', mode: 'dark', manual: true }, { system: 'dark', mode: 'light', manual: true }
  ]) {
    const { mode } = initial;
    const context = await browser.newContext({ colorScheme: initial.system });
    if (initial.manual) {
      await context.addInitScript(value => sessionStorage.setItem('theme-session',
        JSON.stringify({ system: value.system, theme: value.mode })), initial);
    }
    await context.addInitScript(() => {
      window.themeFrames = [];
      window.themeDOMReady = false;
      document.addEventListener('DOMContentLoaded', () => { window.themeDOMReady = true; });
      function sample() {
        if (document.body && getComputedStyle(document.body).fontSize === '17.6px') {
          window.themeFrames.push({ theme: document.documentElement.dataset.theme,
            background: getComputedStyle(document.body).backgroundColor });
        }
        if (!window.stopThemeFrames) requestAnimationFrame(sample);
      }
      requestAnimationFrame(sample);
    });
    const page = await context.newPage();
    let release;
    const gate = new Promise(resolve => { release = resolve; });
    await page.route('**/assets/js/custom-ui.js', async route => { await gate; await route.continue(); });
    try {
      await page.goto(base, { waitUntil: 'commit' });
      await page.waitForFunction(() => window.themeFrames.length > 1);
      assert.equal(await page.evaluate(() => window.themeDOMReady), false);
      assert.equal(await page.locator('#theme-mode-toggle').isVisible(), false);
      release();
      await page.waitForLoadState('networkidle');
      await expectTheme(page, mode);
      const frames = await page.evaluate(() => { window.stopThemeFrames = true; return window.themeFrames; });
      assert.ok(frames.length > 1);
      for (const frame of frames) assert.deepEqual(frame, { theme: mode, background: backgrounds[mode] });
      const early = await page.evaluate(() => {
        const init = [...document.head.querySelectorAll('script')].find(x => x.textContent.includes('theme-session'));
        return !!(init.compareDocumentPosition(document.querySelector('link[rel="stylesheet"]')) & Node.DOCUMENT_POSITION_FOLLOWING);
      });
      assert.ok(early, 'initializer precedes CSS');
      if (!initial.manual) {
        for (const width of [1440, 390]) {
          await page.setViewportSize({ width, height: width === 1440 ? 1000 : 844 });
          await page.screenshot({ path: path.join(output, `theme-${mode}-${width}.png`) });
        }
      }
      checks.push(`initial ${mode} (${initial.manual ? 'manual session' : 'system'}), before CSS/DOMContentLoaded, no wrong styled frames`);
    } finally {
      release();
      await context.close();
    }
  }

  const context = await browser.newContext({ colorScheme: 'light', viewport: { width: 390, height: 844 } });
  const page = await context.newPage();
  await page.goto(base, { waitUntil: 'networkidle' });
  await expectTheme(page, 'light');
  const button = page.locator('#theme-mode-toggle');
  await button.focus();
  await page.keyboard.press('Space');
  await expectTheme(page, 'dark');
  assert.ok(await button.evaluate(x => document.activeElement === x && getComputedStyle(x).outlineStyle !== 'none'));
  await page.reload({ waitUntil: 'networkidle' });
  await expectTheme(page, 'dark');
  await page.locator('#site-nav-toggle').click();
  await page.locator('.site-nav__link[href$="/research/"]').click();
  await expectTheme(page, 'dark');
  await page.locator('.site-nav__brand').click();
  await expectTheme(page, 'dark');
  await button.focus();
  await page.keyboard.press('Enter');
  await expectTheme(page, 'light');
  await button.click();
  await expectTheme(page, 'dark');
  checks.push('two-state toggle, Space/Enter, focus, same-session reload and internal navigation');

  await page.emulateMedia({ colorScheme: 'dark' });
  await expectTheme(page, 'dark');
  assert.equal(await page.evaluate(() => sessionStorage.getItem('theme-session')), null);
  await button.click();
  await expectTheme(page, 'light');
  await page.emulateMedia({ colorScheme: 'light' });
  await expectTheme(page, 'light');
  assert.equal(await page.evaluate(() => sessionStorage.getItem('theme-session')), null);
  await page.emulateMedia({ colorScheme: 'dark' });
  await expectTheme(page, 'dark');
  await page.emulateMedia({ colorScheme: 'light' });
  await expectTheme(page, 'light');
  // Visit another page with a manual choice, clear it there, then navigate back.
  await button.click();
  await page.locator('#site-nav-toggle').click();
  await page.locator('.site-nav__link[href$="/research/"]').click();
  await page.emulateMedia({ colorScheme: 'dark' });
  await expectTheme(page, 'dark');
  await page.emulateMedia({ colorScheme: 'light' });
  await expectTheme(page, 'light');
  await page.goBack({ waitUntil: 'networkidle' });
  await expectTheme(page, 'light');
  checks.push('live Light → Dark → Light clears manual choices in both directions; history navigation stays synchronized');

  await button.click();
  await page.goto('about:blank'); // No website listener exists during the OS change.
  await page.emulateMedia({ colorScheme: 'dark' });
  await page.goto(base, { waitUntil: 'networkidle' });
  await expectTheme(page, 'dark');
  assert.equal(await page.evaluate(() => sessionStorage.getItem('theme-session')), null);
  await page.emulateMedia({ colorScheme: 'light' });
  await expectTheme(page, 'light');
  await button.click();
  await expectTheme(page, 'dark');
  await context.close();
  const fresh = await browser.newContext({ colorScheme: 'light' });
  const freshPage = await fresh.newPage();
  await freshPage.goto(base, { waitUntil: 'networkidle' });
  await expectTheme(freshPage, 'light');
  assert.equal(await freshPage.evaluate(() => sessionStorage.getItem('theme-session')), null);
  await fresh.close();
  checks.push('system change while away; fresh session ignores prior manual choice');

  for (const mode of ['light', 'dark']) {
    for (const legacy of ['system', 'light', 'dark', 'invalid']) {
      const legacyContext = await browser.newContext({ colorScheme: mode });
      await legacyContext.addInitScript(value => localStorage.setItem('theme', value), legacy);
      const legacyPage = await legacyContext.newPage();
      await legacyPage.goto(base, { waitUntil: 'networkidle' });
      await expectTheme(legacyPage, mode);
      assert.equal(await legacyPage.evaluate(() => localStorage.getItem('theme')), null);
      await legacyContext.close();
    }
  }
  for (const invalid of ['broken JSON', '{"theme":"system","system":"light"}', '{"theme":"dark","system":"dark"}']) {
    const invalidContext = await browser.newContext({ colorScheme: 'light' });
    await invalidContext.addInitScript(value => sessionStorage.setItem('theme-session', value), invalid);
    const invalidPage = await invalidContext.newPage();
    await invalidPage.goto(base, { waitUntil: 'networkidle' });
    await expectTheme(invalidPage, 'light');
    assert.equal(await invalidPage.evaluate(() => sessionStorage.getItem('theme-session')), null);
    await invalidContext.close();
  }
  checks.push('legacy localStorage values ignored/removed; malformed, invalid and stale session data rejected');

  for (const failure of ['getter', 'write']) {
    const blocked = await browser.newContext({ colorScheme: 'light', viewport: { width: 390, height: 844 } });
    await blocked.addInitScript(kind => {
      if (kind === 'getter') {
        for (const key of ['localStorage', 'sessionStorage']) {
          Object.defineProperty(window, key, { get() { throw new Error('Storage disabled'); } });
        }
      } else {
        Storage.prototype.setItem = Storage.prototype.removeItem = () => { throw new Error('Storage read-only'); };
      }
    }, failure);
    const blockedPage = await blocked.newPage();
    const errors = [];
    blockedPage.on('pageerror', e => errors.push(e.message));
    await blockedPage.goto(base, { waitUntil: 'networkidle' });
    await expectTheme(blockedPage, 'light');
    await blockedPage.locator('#theme-mode-toggle').click();
    await expectTheme(blockedPage, 'dark');
    await blockedPage.emulateMedia({ colorScheme: 'dark' });
    await expectTheme(blockedPage, 'dark');
    await blockedPage.emulateMedia({ colorScheme: 'light' });
    await expectTheme(blockedPage, 'light');
    await blockedPage.locator('#site-nav-toggle').click();
    assert.equal(await blockedPage.locator('#site-nav-toggle').getAttribute('aria-expanded'), 'true');
    await blockedPage.locator('.site-nav__link[href$="/research/"]').click();
    await expectTheme(blockedPage, 'light');
    assert.deepEqual(errors, []);
    await blocked.close();
  }
  checks.push('blocked storage getters and failing writes: toggle, live sync and menu remain usable');

  for (const mode of ['light', 'dark']) {
    const noJS = await browser.newContext({ javaScriptEnabled: false, colorScheme: mode, viewport: { width: 320, height: 900 } });
    const noJSPage = await noJS.newPage();
    await noJSPage.goto(base, { waitUntil: 'networkidle' });
    assert.equal(await noJSPage.locator('body').evaluate(x => getComputedStyle(x).backgroundColor), backgrounds[mode]);
    assert.equal(await noJSPage.locator('#theme-mode-toggle').isVisible(), false);
    for (const link of await noJSPage.locator('.site-nav__link').all()) assert.ok(await link.isVisible());
    const next = mode === 'light' ? 'dark' : 'light';
    await noJSPage.emulateMedia({ colorScheme: next });
    await noJSPage.waitForFunction(color => getComputedStyle(document.body).backgroundColor === color, backgrounds[next]);
    await noJS.close();
  }
  checks.push('no-JavaScript Light/Dark initial and live CSS fallback, usable navigation, hidden inert control');

  const legacyMedia = await browser.newContext({ colorScheme: 'light' });
  await legacyMedia.addInitScript(() => {
    const native = window.matchMedia.bind(window);
    window.matchMedia = query => {
      const media = native(query);
      return { get matches() { return media.matches; }, addListener: fn => media.addEventListener('change', fn) };
    };
  });
  const legacyPage = await legacyMedia.newPage();
  await legacyPage.goto(base, { waitUntil: 'networkidle' });
  await legacyPage.emulateMedia({ colorScheme: 'dark' });
  await expectTheme(legacyPage, 'dark');
  await legacyMedia.close();
  const noMedia = await browser.newContext();
  await noMedia.addInitScript(() => { window.matchMedia = undefined; });
  const noMediaPage = await noMedia.newPage();
  await noMediaPage.goto(base, { waitUntil: 'networkidle' });
  await expectTheme(noMediaPage, 'light');
  await noMediaPage.locator('#theme-mode-toggle').click();
  await expectTheme(noMediaPage, 'dark');
  await noMedia.close();
  checks.push('legacy addListener and missing matchMedia graceful fallback');

  // Contrast of body, normal links, navigation, toggle and footer in both themes.
  for (const mode of ['light', 'dark']) {
    const contrastContext = await browser.newContext({ colorScheme: mode });
    const contrastPage = await contrastContext.newPage();
    await contrastPage.goto(base, { waitUntil: 'networkidle' });
    const colors = await contrastPage.evaluate(() => ({
      background: getComputedStyle(document.body).backgroundColor,
      foregrounds: ['body', '.page__content a', '.site-nav__link', '#theme-mode-toggle', '.profile-links a']
        .map(selector => getComputedStyle(document.querySelector(selector)).color)
    }));
    for (const foreground of colors.foregrounds) {
      const values = [luminance(foreground), luminance(colors.background)].sort((a, b) => a - b);
      assert.ok((values[1] + 0.05) / (values[0] + 0.05) >= 4.5, `${mode}: contrast ${foreground}`);
    }
    await contrastContext.close();
  }
  checks.push('Light/Dark body/link/navigation/toggle/footer contrast ≥ 4.5:1');
  return checks;
};
