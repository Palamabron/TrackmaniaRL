// Render the article's LaTeX at build time. No math JavaScript is shipped to readers.
// Usage: node scripts/render_article_math.cjs [path/to/katex/dist/katex.js]
const fs = require('node:fs');
const path = require('node:path');
const katex = require(process.argv[2] || 'katex');
const root = path.resolve(__dirname, '..');
const formulas = JSON.parse(fs.readFileSync(path.join(__dirname, 'article-math.json'), 'utf8'));
const file = path.join(root, 'website', 'index.html');
const source = fs.readFileSync(file, 'utf8');
const used = new Set();
const rendered = source.replace(/<!-- math:([a-z-]+) -->[\s\S]*?<!-- \/math:\1 -->/g, (_, key) => {
  const formula = formulas[key];
  if (!formula) throw new Error(`Unknown formula: ${key}`);
  used.add(key);
  const html = katex.renderToString(formula.tex, {
    displayMode: Boolean(formula.display),
    throwOnError: true,
    strict: 'error',
    trust: false,
    output: 'htmlAndMathml',
  });
  return `<!-- math:${key} -->${html}<!-- /math:${key} -->`;
});
for (const key of Object.keys(formulas)) {
  if (!used.has(key)) throw new Error(`Unused formula: ${key}`);
}
fs.writeFileSync(file, rendered);
console.log(`Rendered ${used.size} LaTeX expressions with KaTeX ${katex.version}.`);
