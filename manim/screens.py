# manim scene showing detector screens across voltage and power settings.
from manim import *
from manim.utils.space_ops import rotation_matrix
import numpy as np
import random

# random pixel colors
def random_pixel_color():
    tint: float = random.uniform(a = 0.25, b =  0.5)
    return interpolate(BLACK, WHITE, tint)

class Grid_of_Screens(ThreeDScene):
    def construct(self):
        cols = 4
        rows = 5
        pixel_length = 0.1
        
        # all screens
        all_screens = VGroup()
        for _ in range(rows * cols):
            screen = Rectangle(fill_color = DARK_GRAY, fill_opacity = 1, height = 1.1, stroke_color = BLUE, width = 1.3)
            pixel = Square(fill_color = random_pixel_color(), fill_opacity = 0, stroke_width = 0, side_length = pixel_length)
            sensor = VGroup(screen, pixel)
            all_screens.add(sensor)
        
        all_screens.arrange_in_grid(buff = 0.25, cols = cols, rows = rows)
        all_screens.move_to(point_or_mobject = ORIGIN)
        
        col_labels = VGroup()
        row_labels = VGroup()
        wattages: list = [10, 20, 30, 40]
        voltages: list = [30, 45, 60, 75, 90]
        
        # labels
        for c in range(cols):
            screen: Group = all_screens[c]
            label = MathTex(f"{wattages[c]}\\text{{ W}}", color = YELLOW, font_size = 30)
            label.next_to(buff = 0.25, direction = UP, mobject_or_point = screen)
            col_labels.add(label)

        for r in range(rows):
            screen = all_screens[cols * (r + 1) - 1]
            label = MathTex(f"{voltages[r]}\\text{{ kV}}", color = YELLOW, font_size = 30)
            label.next_to(buff = 0.25, direction = RIGHT, mobject_or_point = screen)
            row_labels.add(label)
        
        # screens
        rows_of_screens: list = []
        for r in range(rows):
            row_of_screens: Group = all_screens[cols * r : cols * (r + 1)]
            rows_of_screens.append(row_of_screens)
        
        # start animations
        self.wait(duration = 1)
        
        # play labels
        self.play(
            LaggedStart(*[Write(vmobject = label) for label in row_labels], lag_ratio = 0),
            LaggedStart(*[Write(vmobject = label) for label in col_labels], lag_ratio = 0),
            run_time = 1
        )
        
        # play screens
        self.play(
            LaggedStart(
                *[LaggedStart(*[FadeIn(screen) for screen in row_of_screens], lag_ratio = 0.1) for row_of_screens in rows_of_screens],
                lag_ratio = 0.1
            ),
            run_time = 2
        )
        self.wait(duration = 1)
        
        # zoom into screen
        target_screen: Group = all_screens[0]
        translation: np.ndarray  = ORIGIN - target_screen.get_center()
        self.play(
            all_screens.animate.shift(translation),
            row_labels.animate.shift(translation),
            col_labels.animate.shift(translation),
            run_time = 1
        )
        self.move_camera(zoom = 4, run_time = 1)
        self.wait(duration = 0.5)
        
        # fade out other screens and labels
        other_screens = VGroup(*[all_screens[screen] for screen in range(1, len(all_screens))])
        self.play(FadeOut(other_screens, row_labels, col_labels), run_time = 0.5)
        self.wait(duration = 0.5)
        
        # turn the screen
        self.play(
            target_screen.animate
            .rotate(angle = -PI / 3, axis = UP)
            .rotate(angle = PI / 6, axis = RIGHT)
            .shift(0.05 * DOWN + 1.2 * LEFT),
            run_time = 1
        )
        
        # adding layers of screens
        shift_screen = 0.4
        back_screens = VGroup()
        normal_vector: np.ndarray = np.array(object = [0, 0, 1])
        normal_vector = np.dot(a = rotation_matrix(angle = PI / 2, axis = UP), b = normal_vector)
        normal_vector = np.dot(a = rotation_matrix(angle = PI / 4, axis = RIGHT), b = normal_vector)
        
        # three back layers
        for i in range(1, 4):
            back_screen: Group = target_screen.copy()
            back_screen.shift(i * shift_screen * normal_vector)
            back_screens.add(back_screen)

        # 6 dots
        dots = VGroup(*[Dot3D(color = WHITE, radius = 0.01) for _ in range(6)])
        dots.arrange(buff = 0.05, direction = RIGHT)
        dots.move_to(point_or_mobject = target_screen.get_center() + 4.5 * shift_screen * normal_vector)
        
        # last screen
        last_screen: Group = target_screen.copy()
        last_screen.shift(6 * shift_screen * normal_vector)
        
        # labels
        last_label = MathTex("10^3\\text{ images}", font_size = 40, color = YELLOW)
        last_label.to_edge(buff = 0.5, edge = 8.75 * RIGHT + 4 * UP)
        self.add_fixed_in_frame_mobjects(last_label)
        self.remove(last_label)
        
        # grouping elements
        back_elements = VGroup()
        back_elements.add(last_screen)
        back_elements.add(dots)
        for back_screen in back_screens:
            back_elements.add(back_screen)
        
        for element in back_elements:
            self.mobjects.insert(0, element)
        
        screen_animations: list = [
            LaggedStart(
                *[LaggedStart(*[FadeIn(screen, shift = 0.2 * normal_vector) for screen in back_screens], lag_ratio = 0.25)],
                *[LaggedStart(Write(vmobject = dots), FadeIn(last_screen, shift = 0.02 * normal_vector), lag_ratio = 0.75)],
                lag_ratio = 0.75
            ),
        ]
        
        # animating back layers
        self.play(screen_animations, run_time = 2)
        self.play(Write(vmobject = last_label), run_time = 1)
        self.wait(duration = 0.5)
        
        # adding pixels
        front_pixel: Group = target_screen[1]
        middle_pixels: list = [layer[1] for layer in back_screens]
        last_pixel: Group = last_screen[1]
        all_pixels = VGroup(front_pixel, *middle_pixels, last_pixel)
        
        # animating pixels
        self.play(
            LaggedStart(*[pixel.animate.set_fill(random_pixel_color(), opacity = 1) for pixel in all_pixels], lag_ratio = 0.1),
            run_time = 1
        )
        self.wait(duration = 0.5)
        
        # moving labels
        self.play(last_label.animate.to_edge(UP, buff = 0.5), run_time = 1)
        label_average = MathTex("1^1", "\\text{ average}", "1^1", font_size = 40, color = WHITE)
        label_average[0].set_opacity(0)
        label_average[2].set_opacity(0)
        label_average.to_edge(buff = 0.5, edge = 11.5 * LEFT + UP)
        self.add_fixed_in_frame_mobjects(label_average)
        self.play(Write(vmobject = label_average), run_time = 0.5)
        self.wait(duration = 0.5)
        
        # adjusting the layering of visual elements
        target_screen.set_z_index(10)
        for i, back_screen in enumerate(iterable = back_screens):
            back_screen.set_z_index(z_index_value = 5 - i)
        dots.set_z_index(z_index_value = 1)
        last_screen.set_z_index(0)

        # collapsing the screens
        collapse_animations: list = []
        speed: float = 1.5
        for i, back_screen in enumerate(iterable = back_screens):
            distance: float = shift_screen * (i + 1)
            collapse_animations.append(back_screen.animate(run_time = distance / speed, rate_func = linear).shift(-distance * normal_vector))
        distance_dots: float = 4.5 * shift_screen
        collapse_animations.append(dots.animate(run_time = distance_dots / speed, rate_func = linear).shift(-distance_dots * normal_vector))
        distance_last: float = 6 * shift_screen
        
        collapse_animations.append(
            last_screen.animate(run_time = distance_last / speed, rate_func = linear).shift(-distance_last * normal_vector)
        )
        collapse_animations.append(target_screen[1].animate(run_time = distance_last / speed).set_fill(GRAY))
        
        # animating collapsing screens
        self.play(AnimationGroup(*collapse_animations, lag_ratio = 0), run_time = 1)
        
        # move back
        self.play(FadeOut(*back_screens, dots, last_screen), run_time = 0.1)
        self.play(
            target_screen.animate
            .rotate(angle = -PI / 6, axis = RIGHT)
            .rotate(angle = PI / 3, axis = UP)
            .move_to(point_or_mobject = ORIGIN),
            run_time = 0.5
        )

        # pixelate the full screen
        height = 11
        width = 13
        grid_of_pixels = VGroup()
        for _ in range(height * width):
            grid_pixel = Square(fill_color = random_pixel_color(), fill_opacity = 1, stroke_width = 0.25, side_length = pixel_length)
            grid_of_pixels.add(grid_pixel)

        grid_of_pixels.arrange_in_grid(buff = 0, cols = width, rows = height)
        grid_of_pixels.move_to(point_or_mobject = target_screen.get_center())
        grid_of_pixels.set_z_index(z_index_value = 11)
        target_screen[1].set_z_index(z_index_value = 12)
        pixel_list: list = list(grid_of_pixels)
        random.shuffle(x = pixel_list)

        # animating the pixel grid
        self.play(
            FadeOut(last_label, run_time = 0.1),
            target_screen[1].animate.set_stroke(width = 0.25),
            LaggedStart(*[FadeIn(pixel) for pixel in pixel_list], lag_ratio = 0.01),
            label_average.animate.to_edge(UP, buff = 0.5).set_x(x = 0),
            FadeOut(target_screen[0]),
            run_time = 2
        )
        self.wait(duration = 0.5)
        
        # pixelate other screens
        all_pixelated_screens = VGroup()
        for i in range(rows * cols):
            pixelated_screen = VGroup()
            for _ in range(height * width):
                grid = Square(fill_color = random_pixel_color(), fill_opacity = 1, stroke_width = 0.25, side_length = 0.1)
                pixelated_screen.add(grid)
            pixelated_screen.arrange_in_grid(buff = 0, cols = width, rows = height)
            pixelated_screen.move_to(point_or_mobject = all_screens[i].get_center())
            all_pixelated_screens.add(pixelated_screen)
        
        # animating everything
        zoom = 0.8
        shift_label = 4
        self.play(FadeOut(label_average), run_time = 0.5)
        self.play(
            FadeIn(*all_pixelated_screens),
            LaggedStart(*[Write(vmobject = label) for label in row_labels], lag_ratio = 0),
            LaggedStart(*[Write(vmobject = label) for label in col_labels], lag_ratio = 0),
            run_time = 1
        )
        self.move_camera(zoom = zoom, run_time = 1)
        self.play(
            grid_of_pixels.animate.shift(-translation),
            target_screen[1].animate.shift(-translation),
            all_pixelated_screens.animate.shift(-translation),
            row_labels.animate.shift(-translation),
            col_labels.animate.shift(-translation),
            run_time = 1
        )
        all_pixelated_screens.add(grid_of_pixels, target_screen[1])
        label_average.to_edge(buff = 0.5, edge = DOWN).set_x(x = 0)
        self.play(Write(vmobject = label_average))
        
        # copying the grid for variance
        grid_average = VGroup(all_pixelated_screens, row_labels, col_labels)
        self.play(
            grid_average.animate.shift(shift_label * LEFT),
            label_average.animate.shift(shift_label * zoom * LEFT),
            run_time = 1
        )
        grid_variance: VGroup = grid_average.copy()
        for screen in grid_variance[0]:
            pixel_group: Group = screen[0] if len(screen) > 1 else screen
            pixels_list: list = list(pixel_group)
            random.shuffle(x = pixels_list)
            for pixel in pixels_list:
                pixel.set_fill(color = random_pixel_color())
        grid_variance.shift(2 * shift_label * RIGHT)
        label_variance = MathTex("\\text{variance}", font_size = 40, color = WHITE)
        label_variance.to_edge(buff = 0.5, edge = DOWN).set_x(x = 0).shift(shift_label * zoom * RIGHT)
        self.add_fixed_in_frame_mobjects(label_variance)
        self.remove(label_variance)
        
        # animating everything
        variance_pixel_list: list = [pixel for screen in grid_variance for pixel in screen]
        random.shuffle(x = variance_pixel_list)

        self.play(
            LaggedStart(*[FadeIn(pixel) for pixel in variance_pixel_list], lag_ratio = 0.01),
            Write(vmobject = label_variance),
            run_time = 2
        )
        self.wait(duration = 7)
        