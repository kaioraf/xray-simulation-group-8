from manim import *
import numpy as np

#code that animates the detector components, full comments on code still have to be added.

class Detector(ThreeDScene):
    def construct(self):
        self.camera.background_color = BLACK
        

        # Start directly at the same front-facing setup view used before
        # Setup.py removes the machine and enters the X-ray source.
        self.set_camera_orientation(
            phi=90 * DEGREES,
            theta=-90* DEGREES,
            zoom=0.9,
        )

        
        # # create x-ray machine box
        machine = Prism(
            dimensions=[7, 2.6, 3],
            fill_color=BLUE_E,
            fill_opacity=0.12,
            stroke_color=BLUE_B,
            stroke_width=2
        )

        # create source
        source = Prism(
            dimensions=[1, 0.6, 0.6],
            color=YELLOW_E,
            fill_opacity=0.9,
        ).move_to(LEFT * 2.6)

        source_label = Text("Source", font_size=28).next_to(source, DOWN * 2).rotate(PI / 2, axis=RIGHT).shift(IN * 0.5)

        # create object platform
        platform = Cylinder(
            radius=0.5,
            height=0.2,
            fill_color=GRAY_B,
            fill_opacity=0.85,
            stroke_color=WHITE,
        ).move_to(ORIGIN + IN * 0.35)

        platform_label = Text("Object platform", font_size=24).next_to(platform, DOWN).rotate(PI / 2, axis=RIGHT).shift(IN * 0.5)

        detector = Prism(
            dimensions=[0.18, 1.7, 2.2],
            fill_color=TEAL,
            fill_opacity=0.75,
            stroke_color=WHITE,
        ).move_to(RIGHT * 2.75)

        detector_label = Text("Detector", font_size=28).next_to(detector, DOWN).rotate(PI / 2, axis=RIGHT).shift(IN *1.2)

        beam_start = source.get_center()
        beam_end = detector.get_center()
        beam_length = np.linalg.norm(beam_end - beam_start)

        beam = Cone(
            base_radius=0.75,
            height=beam_length,
            direction=LEFT,
            fill_color=YELLOW,
            fill_opacity=0.22,
            stroke_color=YELLOW,
            stroke_opacity=0.35,
            resolution=(32, 8),
        ).move_to((beam_start + beam_end) / 2 + OUT * 2.2)


        labels = VGroup(
            source_label,
            platform_label,
            detector_label,
        )

        main_title = (
                    Text("A simple model of an X-Ray machine", font_size=48, color=WHITE)
                    .to_edge(UP)
                    .rotate(PI / 2, axis=RIGHT)
                    .shift(OUT * 3)
                )
        
        self.play(
            Write(main_title),
            FadeIn(source, shift=LEFT * 0.3),
            FadeIn(platform, shift=IN * 0.3),
            FadeIn(detector, shift=RIGHT * 0.3),
            Write(labels),
            Create(machine),
            Create(beam),
            run_time=1,
            rate_func=smooth)
        
        trash= VGroup(
            main_title,
            source,
            platform,
            labels,
            machine,
            beam
        )
        self.play(
            FadeOut(trash, rate_func=smooth, run_time=4)
        )

        self.move_camera(theta=-180 * DEGREES,
                         zoom=2,
                        run_time=1)

        
        split_detector_gap = 0.2
        split_detector_width = 1.7
        split_offset = split_detector_width / 2 + split_detector_gap / 2
        detector_height = 2.2
        scintillator_depth = 1
        ccd_depth = 0.14

        left_detector = Prism(
            dimensions=[scintillator_depth, split_detector_width, detector_height],
            fill_color=GREEN,
            fill_opacity=0.45,
            stroke_color=WHITE,
        ).move_to(detector.get_center() + np.array([0, split_offset, 0]))

        right_detector = Prism(
            dimensions=[ccd_depth, split_detector_width, detector_height],
            fill_color=BLUE_D,
            fill_opacity=0.75,
            stroke_color=WHITE,
        ).move_to(detector.get_center() + np.array([0, -split_offset, 0]))

        split_detector = VGroup(left_detector, right_detector)
        self.play(ReplacementTransform(detector, split_detector), run_time=2, rate_func=smooth)

        def surface_grid(target, depth, color):
            grid = VGroup()
            square_size = 0.28
            columns = 5
            rows = 7
            grid_width = columns * square_size
            grid_height = rows * square_size
            surface_x = target.get_center()[0] - depth / 2 - 0.01

            for row in range(rows):
                for column in range(columns):
                    square = Prism(
                        dimensions=[0.02, square_size * 0.88, square_size * 0.88],
                        fill_color=color,
                        fill_opacity=0.55,
                        stroke_color=WHITE,
                        stroke_width=0.35,
                    ).move_to([
                        surface_x,
                        target.get_center()[1] - grid_width / 2 + square_size * (column + 0.5),
                        target.get_center()[2] - grid_height / 2 + square_size * (row + 0.5),
                    ])
                    grid.add(square)

            return grid

        def hex_surface_grid(target, depth, color):
            grid = VGroup()
            columns = 5
            rows = 7
            hex_radius = 0.15
            horizontal_spacing = 0.29
            vertical_spacing = 0.28
            grid_width = (columns - 1) * horizontal_spacing
            grid_height = (rows - 1) * vertical_spacing
            surface_x = target.get_center()[0] - depth / 2 - 0.02

            def hexagonal_prism(center):
                angles = np.linspace(0, TAU, 6, endpoint=False) + PI / 6
                front_vertices = [
                    center + np.array([
                        -depth * 0.48,
                        hex_radius * np.cos(angle),
                        hex_radius * np.sin(angle),
                    ])
                    for angle in angles
                ]
                back_vertices = [
                    center + np.array([
                        depth * 0.48,
                        hex_radius * np.cos(angle),
                        hex_radius * np.sin(angle),
                    ])
                    for angle in angles
                ]

                faces = VGroup(
                    Polygon(
                        *front_vertices,
                        fill_color=color,
                        fill_opacity=0.9,
                        stroke_color=WHITE,
                        stroke_width=1,
                    ),
                    Polygon(
                        *reversed(back_vertices),
                        fill_color=color,
                        fill_opacity=0.9,
                        stroke_color=WHITE,
                        stroke_width=1,
                    ),
                )
                for index in range(6):
                    next_index = (index + 1) % 6
                    faces.add(
                        Polygon(
                            front_vertices[index],
                            front_vertices[next_index],
                            back_vertices[next_index],
                            back_vertices[index],
                            fill_color=color,
                            fill_opacity=0.9,
                            stroke_color=WHITE,
                            stroke_width=0.5,
                        )
                    )
                return faces

            for row in range(rows):
                for column in range(columns):
                    center = np.array([
                        target.get_center()[0],
                        target.get_center()[1] - grid_width / 2 + column * horizontal_spacing,
                        (
                            target.get_center()[2]
                            - grid_height / 2
                            + row * vertical_spacing
                            + (vertical_spacing / 2 if column % 2 else 0)
                            - 0.05
                        ),
                    ])
                    hexagon = hexagonal_prism(center)
                    grid.add(hexagon)

            return grid

        scintillator_grid = hex_surface_grid(left_detector, scintillator_depth, GREEN_A)
        ccd_grid = surface_grid(right_detector, ccd_depth, BLUE_B)

        scintillator_label = Text("Scintillator", font_size=28, color=GREEN_A).to_edge(DOWN).shift(LEFT * 1.9 + UP * 0.25)
        ccd_label = Text("CCD", font_size=28, color=BLUE_B).to_edge(DOWN).shift(RIGHT * 1.9 + UP * 0.25)

        self.add_fixed_in_frame_mobjects(scintillator_label, ccd_label)
        self.play(
            FadeIn(scintillator_grid),
            FadeIn(ccd_grid),
            Write(scintillator_label),
            Write(ccd_label),
            run_time=1,
            rate_func=smooth,
        )

        scintillator_group = VGroup(
            left_detector,
            scintillator_grid,
            scintillator_label,
        )
        ccd_group = VGroup(
            right_detector,
            ccd_grid,
            ccd_label,
        )

        self.play(
            Indicate(
                scintillator_group,
                color=GREEN_A,
                scale_factor=1.08,
            ),
            run_time=1.5,
        )
        self.play(
            Indicate(
                ccd_group,
                color=BLUE_B,
                scale_factor=1.08,
            ),
            run_time=1.5,
        )

        layer_gap = 0.02
        ccd_center = right_detector.get_center()
        scintillator_target = ccd_center + np.array([
            -(scintillator_depth + ccd_depth) / 2 - layer_gap,
            0,
            0,
        ])
        scintillator_shift = scintillator_target - left_detector.get_center()
        stacked_center = (scintillator_target + ccd_center) / 2

        self.move_camera(
            theta=-90 * DEGREES,
            phi=90 * DEGREES,
            zoom=2.4,
            frame_center=stacked_center,
            run_time=2,
            rate_func=smooth,
            added_anims=[
                left_detector.animate.shift(scintillator_shift),
                scintillator_grid.animate.shift(scintillator_shift),
                FadeOut(scintillator_label),
                FadeOut(ccd_label),
            ],
        )

        scintillator_front_x = scintillator_target[0] - scintillator_depth / 2
        ccd_front_x = ccd_center[0] - ccd_depth / 2
        entry_point = np.array([
            scintillator_front_x - 0.01,
            scintillator_target[1] - 0.02,
            scintillator_target[2] + 0.12,
        ])
        incoming_tip = entry_point + np.array([-1.25, 0, 0.72])

        def photon_wave(tip, direction, length=0.72):
            direction = direction / np.linalg.norm(direction)
            perpendicular = np.array([-direction[2], 0, direction[0]])
            return ParametricFunction(
                lambda t: (
                    tip
                    + direction * t
                    + perpendicular * 0.075 * np.sin(8 * PI * (t + length) / length)
                ),
                t_range=[-length, 0],
                color=YELLOW,
                stroke_width=6,
            )

        incoming_direction = entry_point - incoming_tip
        incoming_wave = photon_wave(incoming_tip, incoming_direction)

        self.play(Create(incoming_wave), run_time=0.4)
        self.play(
            incoming_wave.animate.shift(entry_point - incoming_tip),
            run_time=1.4,
            rate_func=linear,
        )

        straight_wave = photon_wave(entry_point, RIGHT)

        self.play(
            ReplacementTransform(incoming_wave, straight_wave),
            left_detector.animate.set_fill(WHITE, opacity=0.75),
            scintillator_grid.animate.set_fill(WHITE, opacity=1),
            run_time=0.2,
            rate_func=smooth,
        )

        ccd_surface = np.array([
            ccd_front_x,
            entry_point[1],
            entry_point[2],
        ])
        self.play(
            straight_wave.animate.shift(ccd_surface - entry_point),
            left_detector.animate.set_fill(GREEN, opacity=0.45),
            scintillator_grid.animate.set_fill(GREEN_A, opacity=0.9),
            run_time=1.3,
            rate_func=linear,
        )

        final_scene = Group(*self.mobjects)
        frame_center = np.array(self.camera.frame_center)
        ccd_back_point = ccd_center + np.array([ccd_depth / 2 + 0.08, 0, 0])
        final_image = (
            ImageMobject("Anim_pictur.png")
            .set_height(0.2)
            .move_to(ccd_back_point)
        )
        self.add_fixed_in_frame_mobjects(final_image)
        final_image.set_opacity(0)

        self.play(
            FadeOut(final_scene, scale=0.96),
            final_image.animate
            .set_opacity(1)
            .set_height(7)
            .move_to(frame_center),
            run_time=1,
            rate_func=linear,
        )

        self.wait(4)
