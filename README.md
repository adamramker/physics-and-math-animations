# Physics and math animations

Animations using [3Blue1Brown's ManimGL](https://github.com/3b1b/manim).

## Michelson interferometer

`michelson.py` contains the `MichelsonInterferometer` scene. A 632.8 nm
monochromatic beam enters an ideal 50:50 beam splitter, travels along two
perpendicular arms, reflects from the mirrors, and recombines. The upper mirror
moves from 0 to 1.5 wavelengths and back. The opening holds at quarter- and
half-wavelength mirror displacement show how the two output ports exchange light.

The animation displays mirror displacement, round-trip optical path difference,
detector intensity, and returning intensity toward the source. Traveling field
traces, output brightness, and markers on both intensity curves update together.
The diagram magnifies mirror motion and slows optical oscillations; these are
schematic traces rather than geometrically scaled optical wavelengths.

### Run

Install Python 3.11, FFmpeg, and a working OpenGL 3.3 graphics runtime.
Then, from the repository root:

```powershell
python -m pip install -r requirements.txt
python -m unittest -v test_michelson_physics
manimgl michelson.py MichelsonInterferometer -w -m --fps 24 --video_dir outputs
```

For an interactive preview, omit `-w`. For a 1080p movie, replace `-m`
with `--hd`. The scene uses ordinary text and does not require a LaTeX installation.

The video is written under `outputs/` as `MichelsonInterferometer.mp4`
(the exact subdirectory follows your ManimGL directory configuration).
The scene also writes `outputs/michelson_readouts.csv` and prints readouts
every half second of animation time, plus exact mirror-motion checkpoints.
Rendering again replaces the same movie and CSV. Set `MICHELSON_OUTPUT_DIR`
to change the CSV destination, and `--video_dir` to change the movie destination.

### Physics

Assume coherent, equally polarized, spatially overlapping beams, lossless
mirrors, a 50:50 splitter, air/vacuum arms, and quasi-static mirror motion.
With equal beam areas, the time-averaged intensities are

- Round-trip optical path difference: Δ = 2(L2 − L1) = 2x.
- Relative propagation phase: φ = 2πΔ/λ.
- Detector: I_D = I0 sin²(πΔ/λ).
- Returning toward the source: I_S = I0 cos²(πΔ/λ).
- Conservation: I_D + I_S = I0.

The selected beam-splitter phase convention makes the detector dark at equal
arms. The source readout means the returning output beam; it excludes the
incident source beam. Input intensity is 1 W/m². In this scene the detector
maximum occurs at x = λ/4 = 158.2 nm, with Δ = 316.4 nm. Moving a mirror by
λ/2 = 316.4 nm completes one full fringe. The maximum scan reaches x = 949.2 nm,
with Δ = 1898.4 nm.

`michelson_physics.py` is independent of ManimGL and also supports an initial
round-trip optical path offset. Tests check the two ports at known fringe
positions, negative displacement, input validation, and energy conservation.

### GitHub render

The **Render Michelson animation** workflow checks syntax and physical
checkpoints, renders a 720p/24 fps movie under software OpenGL, verifies the
movie and CSV, and uploads a `michelson-animation` artifact containing the
MP4, CSV, and four checkpoint PNGs. It runs on relevant pushes to main and
can also be started from the repository's Actions tab. Artifacts remain for
30 days. Generated media stays out of the Git history.
