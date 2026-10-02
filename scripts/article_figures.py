"""Render the article's development data and illustrative finish-reward formula."""

import json
from itertools import pairwise
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

matplotlib.use("Agg")


ASSETS = Path(__file__).resolve().parents[1] / "website" / "assets"
GREEN = "#225541"
RUST = "#ab5136"
MUTED = "#5f6c64"
plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Segoe UI", "DejaVu Sans"],
        "font.size": 12,
        "axes.edgecolor": "#bac9bf",
        "axes.labelcolor": "#202c27",
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "svg.fonttype": "none",
        "mathtext.fontset": "cm",
        "svg.hashsalt": "trackmaniarl-article",
        "axes.spines.top": False,
        "axes.spines.right": False,
    }
)


def save_svg(figure: Figure, name: str) -> None:
    path = ASSETS / name
    figure.savefig(path, format="svg", metadata={"Date": None})
    # Keep generated files clean for Git's whitespace check.
    path.write_text(
        "\n".join(line.rstrip() for line in path.read_text(encoding="utf-8").splitlines()) + "\n",
        encoding="utf-8",
    )
    plt.close(figure)


def evaluation_history() -> None:
    data = json.loads((ASSETS / "evaluation-history.json").read_text(encoding="utf-8"))
    figure, axes = plt.subplots(2, 3, figsize=(12, 6.8), sharex="col")
    figure.subplots_adjust(left=0.07, right=0.98, bottom=0.17, top=0.90, hspace=0.16, wspace=0.29)
    titles = [
        "Initial model\nfrom scratch",
        "Finish-time reward\nwarm start",
        "Recurrent recovery\nexperiment",
    ]
    for column, series in enumerate(data["series"]):
        points = series["points"]
        x = np.array([point["logged_environment_transitions"] / 1000 for point in points])
        means = [point["mean_finished_seconds"] for point in points]
        y = np.array([np.nan if mean is None else mean for mean in means])
        color = RUST if column == 2 else GREEN
        top, bottom = axes[:, column]
        top.plot(x, y, "o-", color=color, markersize=4, linewidth=1.6)
        valid = np.flatnonzero(np.isfinite(y))
        for previous, current in pairwise(valid):
            if current > previous + 1:
                top.plot(
                    x[[previous, current]],
                    y[[previous, current]],
                    color=color,
                    linewidth=1.6,
                    linestyle=(0, (2, 2)),
                )
        top.axhline(37, color="#809b75", linewidth=1, linestyle=(0, (6, 3)))
        top.set_title(titles[column], fontsize=13, loc="left", pad=14)
        top.set_ylim(35, 61)
        top.set_yticks([35, 40, 45, 50, 55, 60])
        if column == 0:
            top.set_ylabel("Mean of finishes (s)")
        trials = points[0]["trials"]
        bottom.plot(
            x,
            [point["finished"] for point in points],
            "o-",
            color=color,
            markersize=4,
            linewidth=1.6,
        )
        bottom.set_ylim(-0.25, trials + 0.5)
        bottom.set_yticks([0, trials])
        bottom.set_ylabel(f"Finished / {trials}")
        bottom.set_xlabel("Logged transitions (thousands)", fontsize=11, labelpad=8)
        span = x[-1] - x[0]
        bottom.set_xlim(max(0, x[0] - span * 0.05), x[-1] + span * 0.05)
        for axis in (top, bottom):
            axis.grid(axis="y", color="#eef1ee", linewidth=0.8)
            axis.set_axisbelow(True)
            axis.tick_params(labelsize=11)
    figure.text(
        0.07,
        0.045,
        "Short dashes: connection across a batch with no finishes. No time value is imputed.",
        fontsize=11,
        color=MUTED,
    )
    figure.text(
        0.07,
        0.013,
        "Long dashes: 37-second reference. Each column has its own transition counter.",
        fontsize=11,
        color=MUTED,
    )
    save_svg(figure, "evaluation-history.svg")


def finish_reward() -> None:
    figure, axis = plt.subplots(figsize=(10, 4.3))
    figure.subplots_adjust(left=0.10, right=0.97, bottom=0.20, top=0.88)
    times = np.linspace(33, 43, 201)
    axis.plot(times, 70 + np.maximum(-70, 2 * (35 - times)), color=GREEN, linewidth=2)
    axis.axvline(35, color=MUTED, linestyle=(0, (3, 3)), linewidth=1)
    axis.axvline(37, color="#809b75", linestyle=(0, (6, 3)), linewidth=1)
    axis.text(35.12, 73.5, "35 s: reward reference", color=MUTED, fontsize=11)
    axis.text(37.12, 71, "37 s: benchmark threshold for the mean", color=MUTED, fontsize=11)
    for time in (37, 39):
        value = 70 + 2 * (35 - time)
        axis.scatter(time, value, color=GREEN, s=35, zorder=3)
        axis.annotate(
            rf"$T={time}\,\mathrm{{s}}$" + "\n" + rf"$r_{{\mathrm{{finish}}}}={value}$",
            (time, value),
            xytext=(12, 10),
            textcoords="offset points",
            color=GREEN,
            fontsize=12,
        )
    axis.set(
        xlim=(33, 43),
        ylim=(53, 76),
        xlabel=r"Finish time $T$ (seconds)",
        ylabel=r"Extra reward at a valid finish, $r_{\mathrm{finish}}$",
    )
    axis.set_title("Finish bonus + signed time correction", loc="left", fontsize=15, pad=12)
    axis.grid(axis="y", color="#eef1ee")
    axis.set_axisbelow(True)
    save_svg(figure, "finish-reward.svg")


if __name__ == "__main__":
    evaluation_history()
    finish_reward()
