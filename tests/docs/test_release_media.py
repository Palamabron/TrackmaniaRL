from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]


def test_neural_gif_is_bounded_looping_and_has_no_private_metadata() -> None:
    path = ROOT / "docs/assets/trackmaniarl-neural-flow.gif"
    assert path.stat().st_size < 16 * 1024**2
    with Image.open(path) as image:
        assert image.size == (480, 270)
        assert image.n_frames == 1263
        assert image.info["loop"] == 0
        duration = 0
        for index in range(image.n_frames):
            image.seek(index)
            assert not {"comment", "exif", "xmp", "icc_profile"} & image.info.keys()
            assert not image.getexif()
            assert image.info["duration"] in {30, 40}
            duration += image.info["duration"]
        assert duration == 42100


def test_neural_media_documentation_keeps_provenance_and_links() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    guide = (ROOT / "docs/neural-flow-media.md").read_text(encoding="utf-8")
    assert (
        "https://github.com/Palamabron/TrackmaniaRL/releases/download/"
        "v1.2.5/trackmaniarl-neural-flow.gif"
    ) in readme
    assert (
        "https://raw.githubusercontent.com/Palamabron/TrackmaniaRL/"
        "v1.2.5/docs/assets/trackmaniarl-logo.png"
    ) in readme
    assert "best-performing model supplied for this release" in readme
    assert "map-specific" in readme
    assert "-map_metadata -1" in guide
    assert "No seek, trim or speed changes" in guide
    assert "fps=30,scale=480" in guide
    assert (ROOT / "docs/activation-film.md").is_file()
