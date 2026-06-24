from manim import *
import numpy as np
import math


class Setup(ThreeDScene):
    def construct(self):

        # change camera angle
        self.set_camera_orientation(
            phi=65 * DEGREES,  # angle z/x axis
            theta=-55 * DEGREES,  # angle x/y axis
            zoom=0.8
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

        source_label = Text("Source", font_size=28).next_to(source, DOWN * 2)

        # create object platform
        platform = Cylinder(
            radius=0.5,
            height=0.2,
            fill_color=GRAY_B,
            fill_opacity=0.85,
            stroke_color=WHITE,
        ).move_to(ORIGIN + IN * 0.35)

        platform_label = Text("Object platform", font_size=24).next_to(platform, DOWN)

        detector = Prism(
            dimensions=[0.18, 1.7, 2.2],
            fill_color=TEAL,
            fill_opacity=0.75,
            stroke_color=WHITE,
        ).move_to(RIGHT * 2.75)

        detector_label = Text("Detector", font_size=28).next_to(detector, DOWN)

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

        components = VGroup(
            source,
            platform,
            detector,
        )

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
        self.play(Write(main_title, rate_func=smooth, run_time=1))
        self.play(Create(machine), run_time=0.5)
        self.play(
            FadeIn(source, shift=LEFT * 0.3),
            FadeIn(platform, shift=IN * 0.5),
            FadeIn(detector, shift=RIGHT * 0.3),
            run_time=1,
        )
        self.play(Write(labels), run_time=1)
        self.play(Create(beam), run_time=1, rate_func=smooth)

        front_phi = 90 * DEGREES
        front_theta = -90 * DEGREES

        self.move_camera(
            phi=front_phi,
            theta=front_theta,
            zoom=0.9,
            run_time=1,
            added_anims=[
                source_label.animate.rotate(PI / 2, axis=RIGHT).shift(IN * 0.5),
                platform_label.animate.rotate(PI / 2, axis=RIGHT).shift(IN * 0.5),
                detector_label.animate.rotate(PI / 2, axis=RIGHT).shift(IN * 0.5),
            ],
        )

        self.play(
            Indicate(source_label),
            run_time=2
        )
        self.play(
            Indicate(platform_label),
            run_time=2
        )
        self.play(
            Indicate(detector_label),
            run_time=2
        )

        trash = VGroup(
            detector,
            detector_label,
            platform,
            platform_label,
            machine,
            source_label, 
            main_title,
        )

        source_outline = Prism(
            dimensions=[3.2*3, 1.8*3, 1.8*3],
            fill_opacity=0,
            stroke_color=YELLOW,
            stroke_width=3,
        ).move_to(ORIGIN)

        self.play(
            FadeOut(trash, scale=0.5),
            FadeOut(beam, scale=0.4),
            Transform(source, source_outline),
            run_time=1.5,
            rate_func=smooth,
        )

        # Cathode filament attached to the left side of the source box
        box_left_x = -4.8
        coil_center_x = -3.8
        top_y = 1.35
        bottom_y = -1.35
        z_pos = 0

        coil_turns = 11
        coil_radius = 0.28
        coil_height = top_y - bottom_y
        rotation_center = np.array([coil_center_x, 0, z_pos])

        def coil_point(t):
            return np.array([
                coil_center_x + coil_radius * np.sin(t),
                top_y - coil_height * (t / (coil_turns * TAU)),
                z_pos + coil_radius * np.cos(t),
            ])

        coil_start = coil_point(0)
        coil_end = coil_point(coil_turns * TAU)

        top_lead = Line3D(
            start=np.array([box_left_x, top_y, z_pos]),
            end=coil_start,
            color=ORANGE,
            thickness=0.035,
        )

        cathode_coil = Surface(
            lambda u, v: coil_point(u) + np.array([
                coil_radius*0.15*np.cos(v),
                0,
                coil_radius*0.15*np.sin(v)
            ]),
            u_range=[0, coil_turns * TAU],
            v_range=[0, TAU],
            resolution=(80, 8),
            fill_color=ORANGE,
            fill_opacity=1,
        )

        bottom_lead = Line3D(
            start=coil_end,
            end=np.array([box_left_x, bottom_y, z_pos]),
            color=ORANGE,
            thickness=0.035,
        )

        cathode = VGroup(top_lead, cathode_coil, bottom_lead)
        cathode.rotate(PI / 2, axis=RIGHT, about_point=rotation_center)

        # Make glow after rotating, so it has the same orientation
        # cathode_glow = cathode.copy().set_color(YELLOW).set_opacity(0.25)
        cathode_text = (
            Text("Cathode", font_size=48, color=WHITE)
            .to_edge(UP)
            .rotate(PI / 2, axis=RIGHT)
            .shift(IN * 0.5)
        )

        #make anode
        anode_text = (
            Text("Anode", font_size=48, color=WHITE)
            .to_edge(UP)
            .rotate(PI / 2, axis=RIGHT)
            .shift(IN * 0.5)
        )
        anode = Prism(
            dimensions=[0.4, 1.5, 3],
            fill_opacity = 1,
            fill_color=WHITE,
        ).move_to([3,0,0]).set_opacity(1)

        # add title
        Source_title = (
            Text("Inside the X-Ray source", font_size=48, color=WHITE)
            .to_edge(UP)
            .rotate(PI / 2, axis=RIGHT)
            .shift(IN * 0.5)
        )

        # Write title and remove again
        self.play(
            Write(Source_title, run_time=1, rate_func=smooth),
            Succession(
                Wait(2),
                Unwrite(Source_title, run_time=1, rate_func=rate_functions.ease_in_expo)
            )
        )
        cathode_set= VGroup(top_lead, cathode_coil, bottom_lead)
        #spawn everything in
        self.play(Write(cathode_text, run_time=0.5, rate_func=smooth),
                  Succession(
                            Wait(2),
                             ReplacementTransform(cathode_text, cathode_set), run_time=2, rate_func=smooth)
                             )
        
        self.play(Write(anode_text, rate_func=smooth, run_time=1),
                  Succession(
                      Wait(2),
                      ReplacementTransform(anode_text, anode), run_time=2, rate_func=smooth)
                      )
        
        # self.add(cathode_glow)

        # Build electron path from the same points, then rotate it exactly like the cathode
        electron_path = VMobject()
        electron_path.set_points_as_corners([
            np.array([box_left_x, top_y, z_pos]),
            coil_start,
            *[
                coil_point(t)
                for t in np.linspace(0, coil_turns * TAU, 260)
            ],
            coil_end,
            np.array([box_left_x, bottom_y, z_pos]),
        ])
        electron_path.rotate(PI / 2, axis=RIGHT, about_point=rotation_center)

        electrons = VGroup(*[
            Sphere(
                radius=0.1,
                color=BLUE_B,
                fill_opacity=1,
            )
            for _ in range(5)
        ])

        minus_signs = VGroup()

        for i, electron in enumerate(electrons):
            electron.move_to(electron_path.point_from_proportion(i / len(electrons)))

            minus = (
                Text("-", font_size=28, color=WHITE)
                .rotate(PI / 2, axis=RIGHT)
            )
            minus.add_updater(lambda m, e=electron: m.move_to(e.get_center()))
            minus_signs.add(minus)

        self.add(electrons, minus_signs)

        electron_anims = []

        for i, electron in enumerate(electrons):
            offset = i / len(electrons)

            shifted_path = electron_path.copy()
            shifted_path.pointwise_become_partial(
                electron_path,
                offset,
                1
            )

            continued_path = electron_path.copy()
            continued_path.pointwise_become_partial(
                electron_path,
                0,
                offset
            )

            full_shifted_path = VMobject()
            full_shifted_path.set_points_as_corners([
                *shifted_path.get_points(),
                *continued_path.get_points(),
            ])

            electron.move_to(full_shifted_path.point_from_proportion(0))

            electron_anims.append(
                MoveAlongPath(
                    electron,
                    full_shifted_path,
                    rate_func=linear,
                )
            )
        

        anode_center = anode.get_center()

        anode_spin = Rotate(
            anode,
            angle=TAU * 5,          # number of full spins
            axis=RIGHT,             # change this if your prism should spin around another axis
            about_point=anode_center,
            rate_func=linear,
        )

        # Multiple electron arrows shooting from cathode coil to anode.
        # They disappear when they hit the anode.

        # Multiple electron arrows shooting from cathode coil to anode.
        def rotated_point(point):
            dot = Dot3D(point=point, radius=0.001)
            dot.rotate(PI / 2, axis=RIGHT, about_point=rotation_center)
            return dot.get_center()


        electron_starts = [
            rotated_point(np.array([coil_center_x, 1.0, 0.18])),
            rotated_point(np.array([coil_center_x, 0.55, -0.18])),
            rotated_point(np.array([coil_center_x, 0.15, 0.12])),
            rotated_point(np.array([coil_center_x, -0.25, -0.15])),
            rotated_point(np.array([coil_center_x, -0.70, 0.16])),
            rotated_point(np.array([coil_center_x, -1.05, -0.10])),
        ]

        anode_center = anode.get_center()

        electron_ends = [
            anode_center + np.array([-0.05, 0.65, 0.25]),
            anode_center + np.array([-0.05, 0.38, -0.20]),
            anode_center + np.array([-0.05, 0.10, 0.15]),
            anode_center + np.array([-0.05, -0.15, -0.18]),
            anode_center + np.array([-0.05, -0.42, 0.22]),
            anode_center + np.array([-0.05, -0.68, -0.12]),
        ]

        electron_motion_paths = []
        shooting_arrows = VGroup()
        shooting_minus_signs = VGroup()

        for start, end in zip(electron_starts, electron_ends):
            direction = end - start
            direction = direction / np.linalg.norm(direction)

            path = VMobject()
            path.set_points_as_corners([start, end])
            electron_motion_paths.append(path)

            arrow_length = 0.45

            electron_arrow = Arrow3D(
                start=start,
                end=start + direction * arrow_length,
                color=BLUE_B,
                thickness=0.025,
                height=0.16,
                base_radius=0.055,
            )

            minus = Text("-", font_size=20, color=WHITE)
            minus.rotate(PI / 2, axis=RIGHT)
            minus.add_updater(lambda m, a=electron_arrow: m.move_to(a.get_center()))

            shooting_arrows.add(electron_arrow)
            shooting_minus_signs.add(minus)

        # Important: add the children directly, not the parent VGroup.
        self.add(*shooting_arrows, *shooting_minus_signs)

        shooting_motion = LaggedStart(
            *[
                Succession(
                    MoveAlongPath(
                        arrow,
                        path,
                        rate_func=linear,
                        run_time=1.2,
                    ),
                    AnimationGroup(
                        FadeOut(arrow),
                        FadeOut(minus),
                        run_time=0.15,
                    ),
                )
                for arrow, minus, path in zip(
                    shooting_arrows,
                    shooting_minus_signs,
                    electron_motion_paths,
                )
            ],
            lag_ratio=0.12,
            run_time=8,
        )

        # Use an updater for spinning, so it does not fight the color animation.
        anode.add_updater(
            lambda m, dt: m.rotate(
                TAU * dt,
                axis=RIGHT,
                about_point=anode.get_center(),
            )
        )

        anode_heat = UpdateFromAlphaFunc(
            anode,
            lambda m, alpha: m.set_fill(
                interpolate_color(WHITE, RED, alpha),
                opacity=1,
            ).set_stroke(
                interpolate_color(WHITE, YELLOW, alpha),
                width=2,
            )
        )

        cathode_heat = UpdateFromAlphaFunc(
            cathode_coil,
            lambda m, alpha: m.set_fill(
                interpolate_color(WHITE, RED, alpha),
                opacity=1,
            ).set_stroke(
                interpolate_color(WHITE, YELLOW, alpha),
                width=2,
            )
        )

        self.move_camera(
            theta=90 * DEGREES,
            phi=80 * DEGREES,
            run_time=25,
            rate_func=linear,
            added_anims=[
                *electron_anims,
                shooting_motion,
                anode_heat,
                cathode_heat,
            ],
        )

        anode.clear_updaters()

        for minus in minus_signs:
            minus.clear_updaters()

        for minus in shooting_minus_signs:
            minus.clear_updaters()

        self.remove(*shooting_arrows, *shooting_minus_signs)

        self.move_camera(
            frame_center=anode.get_center(),
            zoom=6,
            run_time=2,
            rate_func=linear,
        )
        self.wait()