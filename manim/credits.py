from PIL.ImageFile import ImageFile
from manim import *
from PIL import Image

uva_logo: ImageFile = Image.open(fp = "uva-logo.png")
uva_rgb: Image.Image = uva_logo.convert(mode = "RGB")

class Credits(Scene):
    def construct(self):
        background = ImageMobject(filename_or_array = "credits_background.jpeg")
        background.scale_to_fit_height(height = config.frame_height)
        background.scale_to_fit_width(width = config.frame_width)
        self.add(background)

        # dark overlay
        overlay = Rectangle(
            width = config.frame_width,
            height = config.frame_height,
            fill_color = BLACK,
            fill_opacity = 0.8,
            stroke_width = 0,
        )
        self.add(overlay)

        # white stroke at the top
        top_bar = Rectangle(
            width = config.frame_width,
            height = 1,
            fill_color = WHITE,
            fill_opacity = 1,
            stroke_width = 0,
        )
        top_bar.to_edge(edge = UP, buff = 0)
        self.add(top_bar)

        # Logo's
        logo_height: float = 0.9 * top_bar.height

        uva = ImageMobject(filename_or_array = uva_rgb)
        vu = ImageMobject(filename_or_array = "vu-logo.png")
        cwi = ImageMobject(filename_or_array = "cwi-logo.png")
        uva.set_height(0.8 * logo_height)
        vu.set_height(logo_height)
        cwi.set_height(logo_height)

        logos = Group(uva, vu, cwi)
        logos.arrange(direction = RIGHT, buff = 1)
        logos.move_to(point_or_mobject = top_bar.get_center())

        # left column
        left_title = Tex(r"\texttt{manimations}", font_size = 30, color = WHITE)
        left_roles = Paragraph(
            "Setup.py",
            "Ray.py",
            "Detector.py",
            "screens.py",
            "credits.py",
            alignment = "right",
            font_size = 20,
            line_spacing = 1.2
        )
        left_names = Paragraph(
            "Charlie Mauer",
            "Charlie Mauer",
            "Charlie Mauer",
            "Jeamin Lin",
            "Jeamin Lin",
            alignment = "left",
            font_size = 20,
            line_spacing = 1.2
        )
        left_credits = VGroup(left_roles, left_names)
        left_credits.arrange(direction = RIGHT, buff = 0.5)

        left_group = VGroup(left_title, left_credits)
        left_group.arrange(direction = DOWN, buff = 0.4)
        left_group.move_to(point_or_mobject = 5 * LEFT + 1.2 * UP)

        # center column
        center_title = Text(text = "Film Credits", font_size = 30, color = WHITE)
        center_roles = Paragraph(
            "Editor",
            "Script\n",
            "Voice Over",
            "Music",
            alignment = "right",
            font_size = 20,
            line_spacing = 1.2
        )
        center_names = Paragraph(
            "Kaoi Hermes",
            "Marijn van de Beek\n & Thijmen Sombroek",
            "Kaio Hermes",
            "Wii music",
            alignment = "left",
            font_size = 20,
            line_spacing = 1.2
        )
        center_credits = VGroup(center_roles, center_names)
        center_credits.arrange(direction = RIGHT, buff = 0.5)

        center_group = VGroup(center_title, center_credits)
        center_group.arrange(direction = DOWN, buff = 0.4)
        center_group.move_to(point_or_mobject = 1.2 * UP)

        # right column
        right_title = Text(text = "Special Thanks to", font_size = 30, color = WHITE)
        right_names = Paragraph(
            "Tristan van Leeuwen",
            "Alexander Skorikov",
            alignment = "center",
            font_size = 20,
            line_spacing = 1.2
        )
        right_credits = VGroup(right_names)
        right_credits.arrange(direction = LEFT, buff = 0.5)

        right_group = VGroup(right_title, right_credits)
        right_group.arrange(direction = DOWN, buff = 0.4)
        right_group.move_to(point_or_mobject = 5 * RIGHT + 1.9 * UP)

        # lower right column
        lower_right_title = Text(text = "Supported by", font_size = 30, color = WHITE)
        lower_right_names = Paragraph(
            "University of Amsterdam",
            "Vrije Universiteit Amsterdam",
            "CWI",
            alignment = "center",
            font_size = 20,
            line_spacing = 1.2
        )
        lower_right_credits = VGroup(lower_right_names)
        lower_right_credits.arrange(direction = LEFT, buff = 0.5)
        
        lower_right_group = VGroup(lower_right_title, lower_right_credits)
        lower_right_group.arrange(direction = DOWN, buff = 0.4)
        lower_right_group.move_to(point_or_mobject = 5 * RIGHT + 2 * DOWN)
        
        # animate
        self.play(
            LaggedStart(
                LaggedStart(*[FadeIn(logo) for logo in logos], lag_ratio = 0.5, run_time = 1),
                Write(vmobject = left_group),
                Write(vmobject = center_group),
                Write(vmobject = right_group),
                Write(vmobject = lower_right_group),
                lag_ratio = 0.2,
                run_time = 3,
            )
        )
        self.wait(duration = 2)
        