# Neural-flow release media

![Neural model stage summaries and steering, throttle and brake controls beside the recorded drive](assets/trackmaniarl-neural-flow.gif)

This visualizes a selected evaluation lap from the contributor's strongest
checkpoint for this map. The contributor reports approximately 12 wall-clock hours
of training before capture; no training or fine-tuning occurred during capture,
tensor verification or rendering. This does not establish a new ranking of models.
The supplied film uses a map-specific action filter. Its five-attempt collection
and tensor verification are described in
[Neural network in action](activation-film.md). The historical 30-attempt
benchmark is a separate experiment.

The visible branches summarize road geometry, car features and context, followed
by residual blocks, an IQN action-value head and chosen steering/pedals. Colours
and links summarize recorded activations. The visualization is an architecture
showcase, not a neuron-level explanation or feature-attribution tool. Links are not
individual synapses or proof of causality. Geometry is supplied for the map, not
inferred from the gameplay pixels. The [static model diagram](../readme/architecture.md#composed-value-model)
explains the supported compositional API. The film depicts an opt-in graph model,
not the default starter architecture.

## Reproduce the GIF

Source supplied locally: `%USERPROFILE%/Downloads/trackmaniarl-neural-flow-polished-compressed.mp4`.
Use the account-relative form to avoid publishing the contributor's local account
path. Do not add the MP4 or its local sidecars to the source archive.

The source is 1920 × 1080, H.264, 30 fps, 42.10 seconds, with no audio stream.
Source SHA-256:
`aea2e9f65458a48a6aea126971e09f5f983b1fa00c63e1a128475dd1fb98b03c`.
The published GIF shows the **entire supplied film**, from the start through the finish
and the result card, replacing the short excerpt. No seek, trim or speed changes
are applied. GIF frame durations alternate between 30 and 40 ms because GIF
timing has 10 ms resolution. The export has 1,263 frames, lasts 42.10 seconds
and plays at 30 FPS.
Output: **400 × 225, 9,032,652 bytes**, infinite loop.
The 16-colour palette and reduced spatial resolution keep the complete
recording below both the distribution's 16 MiB per-file limit and GitHub's
inline-image threshold. Playback runs at its original pace, not fast-forward.
The MP4 is unchanged.

Exact conversion command (PowerShell. FFmpeg 7.1 from imageio-ffmpeg 0.6.0 on
the review host):

```powershell
$Source = Join-Path $env:USERPROFILE 'Downloads/trackmaniarl-neural-flow-polished-compressed.mp4'
$Palette = Join-Path $env:TEMP 'trackmaniarl-neural-flow-palette.png'
ffmpeg -v error -y -i "$Source" -vf "fps=30,scale=400:-1:flags=lanczos,palettegen=stats_mode=diff:max_colors=16" -frames:v 1 -update 1 "$Palette"
ffmpeg -v error -n -i "$Source" -i "$Palette" -an -map_metadata -1 -lavfi "fps=30,scale=400:-1:flags=lanczos,paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle" -loop 0 docs/assets/trackmaniarl-neural-flow.gif
Remove-Item -LiteralPath "$Palette"
```

Use the path to an installed FFmpeg executable in place of `ffmpeg` if needed.
`-n` refuses to overwrite an existing export. The source is never changed.
Palette generation and application use the same source film. Bayer
dithering and rectangle differencing limit animation noise and file size.

## Privacy and accessibility

Metadata inspection found codec/container identifiers, with no location,
account, comment or title metadata. Sampled source frames across the film and
the full-length export showed gameplay, clocks and model/control displays. No
private messages, credentials or account names were observed. This is a visual
review, not a guarantee against every possible identifier in every pixel.
The published GIF has no comment or EXIF/XMP metadata. Only playback metadata
and the looping extension remain. Text alternatives and the static diagram
provide the explanation without requiring the animation to be played.

The existing `rollout-v107c-clean.gif` was also recompressed in full from
29,340,096 to 8,376,597 bytes, keeping its 320 × 176 dimensions and approximately
37.36-second playback. The original remains in the ignored local review evidence
directory. That conversion used its recorded palette and dither settings, `fps=8`, no
scaling, no seek/trim and `-map_metadata -1`. This is illustrative gameplay,
not the neural-flow source or a new benchmark.
