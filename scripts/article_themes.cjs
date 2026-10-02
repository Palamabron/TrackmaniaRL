// Recolor only original article vectors. Paper figures and game media are untouched.
// Run after regenerating the light SVGs: node scripts/article_themes.cjs
const fs = require('node:fs');
const path = require('node:path');
const assets = path.resolve(__dirname, '../website/assets');

const palette = {
  '#ffffff': '#18221e',
  '#202c27': '#e7eee9',
  '#225541': '#9ed5b9',
  '#5f6c64': '#adbbb2',
  '#809b75': '#a1c78f',
  '#ab5136': '#ee9a7b',
  '#bac9bf': '#52655b',
  '#eef1ee': '#2d3c34',
  '#124c3e': '#9ed5b9',
  '#50645e': '#adbbb2',
  '#57784b': '#a1c78f',
  '#89401f': '#ee9a7b',
  '#a64a25': '#ee9a7b',
  '#b0b0b0': '#52655b',
  '#c5d6c8': '#2d3c34',
  '#ced8d0': '#52655b',
  '#52655a': '#adbbb2',
  '#557264': '#9eb8a9',
  '#759c90': '#89b7a5',
  '#80788e': '#c3afd9',
  '#899c90': '#adbbb2',
  '#8b958e': '#a4b4a9',
  '#d7e1d8': '#52655b',
  '#e0eadf': '#253b2e',
  '#eef3ed': '#18221e',
  '#b9cbbd': '#52655b',
  '#fbfcfa': '#202d26',
  '#172c28': '#e7eee9',
  '#63746f': '#adbbb2',
  '#70877c': '#9eb8a9',
  '#376d92': '#99c8ed',
  '#946a25': '#e6c17c',
  '#786098': '#c3afd9',
  '#d7e3dd': '#43574b',
  '#edf1ee': '#2d3c34',
  '#f0f7f3': '#20372c',
  '#f2f6fa': '#202f3a',
  '#f6f9f7': '#202d26',
  '#f7f4fa': '#30283c',
  '#fbf8f1': '#373122',
};

for (const name of ['benchmark', 'decision-values', 'evaluation-history',
  'finish-reward', 'model-architecture', 'rl-loop']) {
  let svg = fs.readFileSync(path.join(assets, `${name}.svg`), 'utf8');
  // The two diagrams use dark green blocks with white lettering in both themes.
  const colors = { ...palette };
  if (name === 'rl-loop') delete colors['#225541'];
  svg = svg.replace(/#[\da-f]{6}\b/gi, color => colors[color.toLowerCase()] || color);
  // Matplotlib omits fill on some labels, which would otherwise default to black.
  svg = svg.replace('<svg ', '<svg fill="#e7eee9" ');
  if (name === 'model-architecture') {
    svg = svg.replace(/<[^>]+>/g, tag => {
      if (tag.startsWith('<rect') || tag.startsWith('<circle')) {
        tag = tag.replace('fill="white"', 'fill="#18221e"');
      }
      if (tag.startsWith('<rect')) return tag;
      return tag.replaceAll('#1c6552', '#9ed5b9');
    });
  }
  fs.writeFileSync(path.join(assets, `${name}-dark.svg`), svg);
}
