// Optional visual QA and PNG export: npm package "playwright" plus local Chrome.
const fs = require('node:fs');
const path = require('node:path');
const { setTimeout: delay } = require('node:timers/promises');
const { chromium } = require('playwright');

function inspectLayout(spec) {
  const errors = [];
  const insideRectangle = (b, n) => (
    b.x >= n.x + 7 && b.x + b.width <= n.x + n.w - 7 &&
    b.y >= n.y + 7 && b.y + b.height <= n.y + n.h - 7
  );
  for (const node of spec.nodes) {
    const labels = document.querySelectorAll(`[data-node="${node.id}"] text`);
    if (!labels.length) errors.push({ node: node.id, problem: 'missing node text' });
    for (const text of labels) {
      const b = text.getBBox();
      const corners = [
        [b.x, b.y], [b.x + b.width, b.y],
        [b.x, b.y + b.height], [b.x + b.width, b.y + b.height],
      ];
      const inside = node.shape === 'diamond'
        ? corners.every(([x, y]) => (
          Math.abs(x - node.x - node.w / 2) / (node.w / 2) +
          Math.abs(y - node.y - node.h / 2) / (node.h / 2) < 0.94
        ))
        : insideRectangle(b, node);
      if (!inside) errors.push({ node: node.id, text: text.textContent });
    }
  }
  for (const label of document.querySelectorAll('[data-edge] text')) {
    const b = label.getBBox();
    for (const node of spec.nodes) {
      if (b.x < node.x + node.w && b.x + b.width > node.x &&
          b.y < node.y + node.h && b.y + b.height > node.y) {
        errors.push({ edge: label.parentElement.dataset.edge, overlap: node.id });
      }
    }
  }
  for (const note of spec.notes || []) {
    const text = document.querySelector(`[data-note="${note.id}"] text`);
    if (!text || !insideRectangle(text.getBBox(), note)) {
      errors.push({ note: note.id, problem: 'text overflow' });
    }
  }
  for (const text of document.querySelectorAll('svg text')) {
    const b = text.getBBox();
    if (b.x < 0 || b.y < 0 || b.x + b.width > spec.width || b.y + b.height > spec.height) {
      errors.push({ text: text.textContent, problem: 'outside canvas' });
    }
  }
  return errors;
}

async function main() {
  const browserChoice = process.env.DIAGRAM_BROWSER_PATH
    ? { executablePath: process.env.DIAGRAM_BROWSER_PATH }
    : { channel: 'chrome' };
  const browser = await chromium.launch({ headless: true, ...browserChoice });
  try {
    const page = await browser.newPage({ deviceScaleFactor: 1 });
    const specs = fs.readdirSync(__dirname).filter(file => file.endsWith('.spec.json')).sort();
    for (const file of specs) {
      const spec = JSON.parse(fs.readFileSync(path.join(__dirname, file), 'utf8'));
      const stem = file.replace('.spec.json', '');
      const svg = fs.readFileSync(path.join(__dirname, `${stem}-preview.svg`), 'utf8');
      await page.setContent('<img id="standalone" src="data:image/svg+xml;base64,' + Buffer.from(svg).toString('base64') + '">');
      await page.waitForFunction(() => document.querySelector('#standalone').complete);
      const imageWidth = await page.locator('#standalone').evaluate(img => img.naturalWidth);
      if (imageWidth !== spec.width) throw new Error(`${stem}: invalid standalone SVG image`);
      await page.setViewportSize({ width: spec.width, height: spec.height });
      await page.setContent('<style>body{margin:0}</style>' + svg);
      await page.evaluate(() => document.fonts.ready);
      const issues = await page.evaluate(inspectLayout, spec);
      if (issues.length) throw new Error(`${stem}: ${JSON.stringify(issues)}`);
      const png = await page.screenshot();
      await savePng(path.join(__dirname, `${stem}-preview.png`), png);
      console.log(`${stem}: layout verified, PNG saved`);
    }
  } finally {
    await browser.close();
  }
}

async function savePng(filename, png) {
  // Desktop image previews can hold a brief Windows file lock during refresh.
  for (let attempt = 0; attempt < 4; attempt++) {
    try {
      await fs.promises.writeFile(filename, png);
      return;
    } catch (error) {
      if (attempt === 3 || !['UNKNOWN', 'EBUSY', 'EPERM'].includes(error.code)) throw error;
      await delay(250);
    }
  }
}

main().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
