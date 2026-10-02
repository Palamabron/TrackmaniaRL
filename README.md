# TrackmaniaRL article — private draft

The article lives on `codex/library-article`, created from `origin/main` at
`556adeefdb401dae5d211e836f44ea734a48aa05`. Work is isolated in this worktree.
No push, Pages deployment or repository-visibility change has been made.

## Preview

From this worktree:

```powershell
python -m http.server 8765 --bind 127.0.0.1 --directory website
```

Open <http://127.0.0.1:8765/>. `index.html` also works directly from disk.
The page is static, with local assets and no analytics, remote fonts or backend.
Native MP4 controls work without JavaScript. Charts have downloadable numeric
sources and the evidence page includes complete development-evaluation tables.

## This revision

The English article now follows the author's experiments from July 2023 through
September 2026, with a gap in the surviving history after January 2024. It joins
Git evidence to three W&B project inventories (681 logging records, not independent
experiments) and full histories for V105A, V105B and V107H. Only selected metadata
and numeric chart points are in the site. Raw exports and credentials are not.

The best-confirmed geometry-based controller is V107I plus the V108 neighbors
filter. Vision is motivated by limited map coverage: as the author clarified,
only a minority of maps have complete track boundaries recordable through driving.
Camera pilots do not yet establish superior driving performance.

Read `evidence.html` for exact source distinctions, recorded-versus-current Git
hashes, benchmark selection, raw-history extraction and media provenance.
The first-person text is a draft assembled from the author's records; personal
motives or memories beyond those records can be added in editorial review.

## Explanations and figures

The article explains the RL loop, the practical choice of IQN, and the differences
from DQN, SAC, TQC and PPO. It does not claim a controlled ranking of these methods.
Visible experiment names are descriptive; source URLs retain their real targets.
The narrative credits the original TMRL authors and the author's subsequent work.

Original figures from the IQN (Figure 1), TQC (Figure 2) and SimbaV2 (Figure 3)
papers were rendered from the published PDFs at 360 dpi and cropped to the figures.
Their captions cite the authors, PMLR papers and CC BY 4.0 license; full credits and
crop dimensions are in `evidence.html#paper-figures`. The paper architecture is
explicitly distinguished from the adapted backbone in the racing model.

The RL loop and return-distribution illustration are local SVGs. The latter uses
invented values, not measured results. The architecture now uses explicit addition
and concatenation nodes with arrows ending at node boundaries. The header logo and
favicon use unchanged repository branding assets.

## Original-resolution media

- `assets/neural-flow.mp4`: complete original 1080p, 30fps, 42.1-second film,
  H.264/yuv420p, approximately 31.2 MB.
- `assets/benchmark-best.mp4`: complete original release excerpt of confirmation
  attempt 29, native 720p/20fps, 38.7 seconds, approximately 23.3 MB.
- Posters were extracted from the original videos; the cover is a native
  1916×1054 frame at 05:00 in the Desktop recording.
- MP4s use faststart and were stream-copied without video re-encoding. Originals
  are untouched. The previous GIF was removed.
- The architecture and both charts are SVG and remain sharp at any zoom level.

For another visual pass, the most useful new capture would be a pair showing
one map with complete recordable boundaries and one without them. It would
illustrate why the vision branch is needed. No new screenshot is required to
read the current complete draft.

## Future GitHub Pages publication

`website/` is a complete static artifact with relative paths and `.nojekyll`.
The nested `.gitignore` permits only the two intended MP4 files under the parent
repository's broad video ignore rule. No deployment workflow is enabled.

Keep this branch local while the article must remain private. `noindex` and
`robots.txt` are indexing hints, not access controls; pushing to a public repo
would expose the source even without Pages. A private repo does not by itself
prove a Pages site will be access-restricted. Before any publication, review the
text, W&B metadata, media rights, author/date and draft/robots markers, then choose
a hosting configuration with the intended access explicitly verified.
