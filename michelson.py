"""Render: manimgl michelson.py MichelsonInterferometer -w -m --video_dir outputs"""
import csv
import math
import os
from pathlib import Path

import numpy as np
from manimlib import *
from michelson_physics import michelson_readout


class MichelsonInterferometer(Scene):
    wavelength_nm = 632.8
    input_intensity = 1.0  # W / m^2; equal beam areas at the two output ports

    def construct(self):
        # Motion is measured in wavelengths; the diagram magnifies it for visibility.
        motion = ValueTracker(0.0)
        clock = ValueTracker(0.0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(motion, clock)
        readout = lambda: michelson_readout(
            motion.get_value() * self.wavelength_nm,
            self.wavelength_nm, self.input_intensity,
        )

        def text_at(text, point, size=22, color=WHITE):
            return Text(text, font_size=size, color=color).move_to(point)

        title = text_at("Michelson interferometer", [0, 3.65, 0], 36)
        subtitle = text_at(
            "Monochromatic light  |  632.8 nm  |  ideal 50:50 beam splitter",
            [0, 3.14, 0], 21, GREY_B,
        )
        divider = Line([0.55, -3.38, 0], [0.55, 2.8, 0],
                       stroke_color=GREY_D, stroke_width=1)
        bs = np.array([-3.5, -0.65, 0.0])
        fixed_tip = np.array([-0.75, -0.65, 0.0])
        moving_tip = lambda: np.array([-3.5, 2.10 + 0.4 * motion.get_value(), 0.0])
        source_tip = np.array([-6.1, -0.65, 0.0])
        detector_tip = np.array([-3.5, -2.75, 0.0])

        splitter = Line(bs + [-0.33, -0.33, 0], bs + [0.33, 0.33, 0],
                        stroke_color=WHITE, stroke_width=7)
        splitter_label = text_at("50:50", [-2.98, -1.14, 0], 20, GREY_B)
        fixed_mirror = Line(fixed_tip + [0, -0.43, 0],
                            fixed_tip + [0, 0.43, 0],
                            stroke_color=GREY_A, stroke_width=9)
        fixed_label = text_at("Fixed mirror", [-1.12, 0.1, 0], 20)
        moving_mirror = Line([-0.43, 0, 0], [0.43, 0, 0],
                             stroke_color=GREY_A, stroke_width=9)
        moving_mirror.add_updater(lambda m: m.move_to(moving_tip()))
        moving_label = text_at("Moving mirror", [-4.8, 2.55, 0], 20, YELLOW)
        moving_arrow = Arrow([-4.15, 1.84, 0], [-4.15, 2.65, 0],
                             color=YELLOW, stroke_width=2, buff=0)
        laser = RoundedRectangle(width=0.85, height=0.48, corner_radius=0.08,
                                 color=GREEN).move_to(source_tip + [-0.15, 0, 0])
        source_label = text_at("Source", [-5.95, 0.0, 0], 22, GREEN)
        return_label = text_at("Returning to source", [-5.1, -1.32, 0], 18, BLUE)
        detector = RoundedRectangle(width=0.85, height=0.44, corner_radius=0.06,
                                    color=ORANGE).move_to(detector_tip + [0, -0.16, 0])
        detector_label = text_at("Detector", [-3.5, -3.33, 0], 22, ORANGE)
        arm_h = text_at("L1", [-1.94, -0.03, 0], 20, BLUE)
        arm_v = text_at("L2 = L1 + x", [-2.37, 1.3, 0], 20, YELLOW)
        diagram_note = text_at(
            "Schematic: motion magnified, optical oscillations slowed",
            [-3.0, -3.75, 0], 16, GREY_B,
        )
        guides = VGroup(
            Line(source_tip, bs, stroke_color=GREEN, stroke_width=1),
            Line(bs, fixed_tip, stroke_color=BLUE, stroke_width=1),
            Line(bs, detector_tip, stroke_color=ORANGE, stroke_width=1),
        )
        vertical_guide = Line(bs, moving_tip(), stroke_color=YELLOW, stroke_width=1)
        vertical_guide.add_updater(lambda m: m.put_start_and_end_on(bs, moving_tip()))

        # Traveling electric-field traces. Arm colors identify the two paths.
        # Each arm's returning phase includes its complete round trip.
        def wave(start, end, optical_distance, phase_offset=0.0,
                 amplitude=0.075, color=BLUE, lateral=0.0):
            curve = VMobject().set_stroke(color, width=2)
            def update(m):
                a = np.array(start() if callable(start) else start, dtype=float)
                b = np.array(end() if callable(end) else end, dtype=float)
                direction = b - a
                normal = np.array([-direction[1], direction[0], 0.0])
                normal /= np.linalg.norm(normal)
                u = np.linspace(0.0, 1.0, 100)
                distance = optical_distance() if callable(optical_distance) else optical_distance
                phase = phase_offset() if callable(phase_offset) else phase_offset
                amp = amplitude() if callable(amplitude) else amplitude
                field = amp * np.sin(math.tau * (0.65 * clock.get_value() - distance * u) + phase)
                points = a + u[:, None] * direction + (lateral + field)[:, None] * normal
                m.set_points_as_corners(points)
            curve.add_updater(update)
            update(curve)
            return curve

        incoming = wave(source_tip + [0.28, 0.10, 0], bs + [0, 0.10, 0],
                        3.5, phase_offset=math.tau * 3.5, color=GREEN)
        h_out = wave(bs, fixed_tip, 4, color=BLUE, lateral=0.10)
        h_back = wave(fixed_tip, bs, 4, phase_offset=-math.tau * 4,
                      color=BLUE, lateral=0.10)
        v_out = wave(bs, moving_tip, lambda: 4 + motion.get_value(),
                     color=YELLOW, lateral=0.10)
        v_back = wave(moving_tip, bs, lambda: 4 + motion.get_value(),
                      phase_offset=lambda: -math.tau * (4 + motion.get_value()),
                      color=YELLOW, lateral=0.10)
        # Complex field sum/difference; signed amplitudes preserve the phase.
        source_wave = wave(
            bs + [0, -0.15, 0], source_tip + [0.28, -0.15, 0], 3.5,
            phase_offset=lambda: math.pi / 2 - readout().phase_rad / 2,
            amplitude=lambda: 0.15 * math.cos(readout().phase_rad / 2),
            color=BLUE,
        )
        detector_wave = wave(
            bs, detector_tip, 3,
            phase_offset=lambda: -readout().phase_rad / 2,
            amplitude=lambda: 0.15 * math.sin(readout().phase_rad / 2),
            color=ORANGE,
        )
        detector_glow = Dot(detector_tip, radius=0.14, color=ORANGE)
        source_glow = Dot(source_tip + [0.23, -0.15, 0], radius=0.11, color=BLUE)
        detector_glow.add_updater(
            lambda m: m.set_opacity(readout().detector_intensity / self.input_intensity)
        )
        source_glow.add_updater(
            lambda m: m.set_opacity(readout().source_return_intensity / self.input_intensity)
        )

        # A fixed left edge prevents shifting when the number of digits changes.
        labels, numbers = VGroup(), VGroup()
        specs = [
            ("Mirror x (nm)", 2.3, lambda: readout().displacement_nm, YELLOW, 1),
            ("Path difference (nm)", 1.78, lambda: readout().path_difference_nm, WHITE, 1),
            ("Detector I (W/m²)", 1.26, lambda: readout().detector_intensity, ORANGE, 3),
            ("Source return I (W/m²)", 0.74, lambda: readout().source_return_intensity, BLUE, 3),
        ]
        for label, y, value, color, places in specs:
            name = Text(label, font_size=21, color=color).move_to([0.95, y, 0], LEFT)
            number = DecimalNumber(value(), num_decimal_places=places,
                                   font_size=25, color=color)
            number.move_to([5.05, y, 0], LEFT)
            number.add_updater(lambda m, fn=value: m.set_value(fn()))
            labels.add(name)
            numbers.add(number)
        formulas = VGroup(
            text_at("Δ = 2(L2 − L1) = 2x     φ = 2πΔ/λ", [3.72, 0.18, 0], 23),
            text_at("I detector = I0 sin²(πΔ/λ)", [3.72, -0.27, 0], 21, ORANGE),
            text_at("I source = I0 cos²(πΔ/λ)", [3.72, -0.65, 0], 21, BLUE),
        )

        # Complementary intensity curves, indexed by round-trip path difference.
        graph_left, graph_right = 1.35, 6.2
        graph_bottom, graph_top = -2.64, -1.22
        def graph_point(delta_lambdas, intensity):
            return np.array([
                graph_left + (graph_right - graph_left) * delta_lambdas / 3,
                graph_bottom + (graph_top - graph_bottom) * intensity / self.input_intensity,
                0.0,
            ])
        axes = VGroup(
            Line(graph_point(0, 0), graph_point(3, 0), stroke_color=GREY_B, stroke_width=1),
            Line(graph_point(0, 0), graph_point(0, self.input_intensity),
                 stroke_color=GREY_B, stroke_width=1),
        )
        for i in range(4):
            axes.add(text_at(str(i), graph_point(i, 0) + [0, -0.24, 0], 17, GREY_B))
        for fraction in (0, 0.5, 1):
            y = graph_point(0, fraction * self.input_intensity)[1]
            axes.add(text_at(str(fraction), [1.05, y, 0], 16, GREY_B))
        graph_caption = text_at("Round-trip path difference Δ / λ", [3.8, -3.13, 0], 20)
        graph_heading = text_at("Output intensity / I0", [3.8, -0.99, 0], 18, GREY_B)
        curves = VGroup()
        for fn, color in ((lambda q: math.sin(math.pi * q) ** 2, ORANGE),
                          (lambda q: math.cos(math.pi * q) ** 2, BLUE)):
            curve = VMobject().set_stroke(color, width=3)
            curve.set_points_as_corners([
                graph_point(q, self.input_intensity * fn(q))
                for q in np.linspace(0, 3, 301)
            ])
            curves.add(curve)
        cursor = Line(graph_point(0, 0), graph_point(0, self.input_intensity),
                      stroke_color=WHITE, stroke_width=1, stroke_opacity=0.45)
        cursor.add_updater(lambda m: m.put_start_and_end_on(
            graph_point(readout().path_difference_nm / self.wavelength_nm, 0),
            graph_point(readout().path_difference_nm / self.wavelength_nm, self.input_intensity),
        ))
        markers = VGroup(Dot(color=ORANGE, radius=0.065), Dot(color=BLUE, radius=0.065))
        markers[0].add_updater(lambda m: m.move_to(graph_point(
            readout().path_difference_nm / self.wavelength_nm, readout().detector_intensity)))
        markers[1].add_updater(lambda m: m.move_to(graph_point(
            readout().path_difference_nm / self.wavelength_nm, readout().source_return_intensity)))
        conservation = text_at("I detector + I source = I0 = 1 W/m²", [3.78, -3.63, 0], 19, GREY_B)

        apparatus = VGroup(
            guides, vertical_guide, laser, source_label, return_label,
            splitter, splitter_label, fixed_mirror, fixed_label,
            moving_mirror, moving_label, moving_arrow, arm_h, arm_v,
            detector, detector_label, diagram_note,
        )
        dashboard = VGroup(labels, numbers, formulas, axes, curves, cursor,
                           markers, graph_caption, graph_heading, conservation)
        self.add(title, subtitle, divider, apparatus, dashboard)
        self.play(ShowCreation(incoming), run_time=1.5)
        self.add(h_out, h_back, v_out, v_back, source_wave, detector_wave,
                 source_glow, detector_glow)
        # Draw the splitter/mirrors over the field traces.
        self.add(splitter, fixed_mirror, moving_mirror)

        rows = []
        last_sample = [-1.0]
        def sample(force=False):
            elapsed = clock.get_value()
            if force or elapsed - last_sample[0] >= 0.5 - 1e-8:
                r = readout()
                row = [elapsed, r.displacement_nm, r.path_difference_nm,
                       r.phase_rad, r.detector_intensity, r.source_return_intensity]
                rows.append(row)
                last_sample[0] = elapsed
                print(
                    f"t={elapsed:6.2f}s  x={r.displacement_nm:8.2f} nm  "
                    f"Δ={r.path_difference_nm:8.2f} nm  "
                    f"I_detector={r.detector_intensity:.4f} W/m²  "
                    f"I_source_return={r.source_return_intensity:.4f} W/m²",
                    flush=True,
                )
        logger = Mobject()
        logger.add_updater(lambda m, dt: sample())
        self.add(logger)
        sample(force=True)
        self.wait(2)
        # Quarter wavelength -> half wavelength OPD -> detector maximum.
        self.play(motion.animate.set_value(0.25), run_time=3, rate_func=linear)
        sample(force=True)
        self.wait(1.5)
        self.play(motion.animate.set_value(0.5), run_time=3, rate_func=linear)
        sample(force=True)
        self.wait(1.5)
        self.play(motion.animate.set_value(1.5), run_time=8, rate_func=linear)
        sample(force=True)
        self.wait(1.5)
        self.play(motion.animate.set_value(0.0), run_time=8, rate_func=linear)
        sample(force=True)
        self.wait(2)
        self.remove(logger)
        output_dir = Path(os.environ.get("MICHELSON_OUTPUT_DIR", "outputs"))
        output_dir.mkdir(parents=True, exist_ok=True)
        csv_path = output_dir / "michelson_readouts.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow([
                "animation_time_s", "mirror_displacement_nm", "path_difference_nm",
                "phase_rad", "detector_intensity_W_m2", "source_return_intensity_W_m2",
            ])
            writer.writerows(rows)
        print(f"Saved readouts: {csv_path.resolve()}", flush=True)
