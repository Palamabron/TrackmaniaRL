# Article draft

An unpublished, standalone article about TrackmaniaRL, based on remote `origin/main`
at `556adeefdb401dae5d211e836f44ea734a48aa05` (1.2.11). Source is on the local
`codex/library-article` branch. No remote push or deployment is part of this draft.

## Read and edit

Open `index.html` directly, or from the repository root run:

```powershell
python -m http.server 8765 --bind 127.0.0.1 --directory website
```

Then visit <http://127.0.0.1:8765>. All assets, typography and scripts are local;
there is no analytics, CDN, backend, installation or build step. Edit the article
in `index.html`, presentation in `style.css`, and optional interactions in
`article.js`. Core text, source links, chart and trial table work without JavaScript.
The animated recording is opt-in and has a stop control.

## Privacy and future GitHub Pages use

The draft stays private by remaining local. No Pages workflow was added and no
repository settings were changed. `noindex` and `robots.txt` discourage indexing;
they are **not access controls**. Do not push this branch to a public repository
while its contents need to stay private.

The `website/` directory is the complete static publishable artifact. When public
publication is explicitly approved, it can be uploaded as a GitHub Pages artifact.
Relative asset paths work at either a project subpath or an organization root.
At that point, review the author/date, draft label, robots directives, accessibility,
media permissions and scientific claims. An organization-root address such as
`TrackmaniaRL.github.io` requires the corresponding Pages repository/configuration;
this draft does not create it. Do not assume a private repository makes its Pages
site private; confirm available access controls before any private online deployment.

## Editorial and media notes

The author attribution follows the repository NOTICE. The narrative is a synthesis
of implementation and release records, not an invented first-person account.
Links are pinned to the source snapshot. Benchmark values come from the complete
tracked V108 trial artifact. The benchmark and the five-attempt film are explicitly
separate. The film model is not presented as the starter model.

Current assets reuse the repository's real footage. Posters are frames from
`docs/assets/v108-neighbors-best.gif` and `trackmaniarl-neural-flow.gif`; the latter
GIF is copied locally so the site is self-contained. No generated gameplay,
fabricated learning curves or borrowed reference-article graphics are used.

Useful additions for the next editorial pass:

| Capture | What to record | Where it helps |
| --- | --- | --- |
| Clean hero screenshot | 1920×1080 or larger, same benchmark map, third-person view approaching a readable corner; hide ghost and unrelated overlays | Replaces the existing GIF-derived hero frame with a sharper image |
| Paired observation view | The same timestamp as gameplay, showing the actual boundary lookahead or camera input; preserve settings and map identity | Explains exactly what the agent sees |
| Failure and recovery clip | 10–20 seconds from an identified attempt, with visible controls; retain trial/checkpoint IDs and say whether selected | Shows the engineering problem behind recovery |
| Training evidence | Export actual learning/evaluation data with seeds, axes, environment steps and wall time; retain failures | Enables a real learning curve, which is deliberately absent now |

These are optional improvements; the current page has complete figures and no
empty screenshot slots. Avoid exposing account names, chat, tokens or local paths.
Add your own account of why the rewrite began, the first successful finish and the
hardest debugging episode if you want a more personal article; those facts cannot
be inferred reliably from commit history.

The supplied reference articles are credited in the page as inspiration and
companion reading, not as evidence for TrackmaniaRL performance.
