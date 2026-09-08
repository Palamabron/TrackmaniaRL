# Contributing to TrackmaniaRL

TrackmaniaRL is an SDK, not a collection of hard-coded training modes. Read the
[architecture](readme/architecture.md) and
[development guide](readme/development.md) before changing a public contract.

## Local quality gate

Install and run the same commands used by CI:

```bash
uv sync --group dev
uv run poe fmt
uv run poe types
uv run poe test
```

This runs the maintained regression suite, including integration and documentation
contracts. For iteration, select the tests relevant to the changed component;
run the complete suite before preparing a release.

Do not use another package manager or formatter. Keep `uv.lock` synchronized
when dependencies change and describe any optional dependency or platform
impact in the pull request.

## Where changes belong

- stable interfaces, data and runtime mechanics: `trackmaniarl.core`;
- reusable learner/objective implementations: `trackmaniarl.algorithms`;
- frame encoders, temporal cores, heads, value strategies and model composition:
  `trackmaniarl.models`;
- Trackmania/OpenPlanet behavior only: `trackmaniarl.trackmania`;
- actor/learner transport and durability: `trackmaniarl.distributed`;
- logging/artifacts: `trackmaniarl.observability`;
- experiment orchestration: `trackmaniarl.experiments`;
- application-specific behavior: a generated extension project.

Keep the public CLI portable: `trackmaniarl init` and `trackmaniarl validate`
must behave the same on Windows and Linux. Avoid local file access, environment
reads and optional imports during `import trackmaniarl`. Validate configuration
at the boundary; keep Pydantic models out of rollout and sampling hot paths.

Every bundled component needs deterministic contract coverage. A distributed
change also needs fake actor/slow learner coverage; a Trackmania change needs an
offline test and should pass the bounded Windows smoke test before release.

When a public flow or ownership boundary changes, update `README.md`, the
relevant guide under `readme/`, the diagram spec and all `.excalidraw`, SVG, PNG
and HTML derivatives. Diagram validation and visual inspection are part of the
documentation gate.

Security reports follow [SECURITY.md](SECURITY.md), not the public issue tracker.

## Before sharing a change or release

- Inspect staged files and reachable history for secrets, home paths, private
  URLs, account/session identifiers and machine/network details. Report categories
  and relative paths, never copy sensitive values into issues or review output.
- Keep credentials in environment variables; copy `.env-example` locally and
  never commit real values. Keep recordings, checkpoints and datasets outside
  distribution inputs.
- Review screenshots and every selected video segment for visible private data;
  remove nonessential container/EXIF/XMP metadata before publishing media.
- Build the wheel and source distribution and run `scripts/check_distribution.py`
  on that exact pair. Git ignore rules alone do not control setuptools archives.
- Read [the release review](docs/reviews/1.2.0-release-review.md) and resolve its
  publication blockers. Preserve license and upstream attribution.
