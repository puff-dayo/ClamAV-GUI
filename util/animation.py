import colorsys
import math
import time
from tkinter import *
from PIL import Image, ImageTk, ImageDraw


class BreathingCircle:
    def __init__(self, width=500, height=500):
        self.animating = False
        self.hue = 0.0
        self.phase = 0.0
        self.base_size = 500
        self.base_radius = 100
        self.base_line_width = 2
        self.width = width
        self.height = height
        self.pulse = 0.0
        self.center = (self.width // 2, self.height // 2)
        self.symbol_index = 0
        self.color = "#89b4fa"
        self.hue_mode = False
        self.scale_factor = 1.0
        self.radius = self.base_radius
        self.line_width = self.base_line_width

        # For Pillow rendering
        self.pil_image = None
        self.tk_image = None
        self.image_id = None

        self.last_frame_time = 0
        self.animation_step = 0.025
        self.high_res_factor = 1

    def create_canvas(self, master, bg, width=500, height=500):
        self.canvas = Canvas(master, width=width, height=height,
                             bg=bg, highlightthickness=0)
        self._calculate_scale()
        self.render_image()
        return self.canvas

    def _calculate_scale(self):
        self.canvas.update_idletasks()
        current_width = self.canvas.winfo_width()
        current_height = self.canvas.winfo_height()
        self.scale_factor = min(current_width, current_height) / self.base_size
        self.radius = self.base_radius * self.scale_factor
        self.line_width = self.base_line_width * self.scale_factor
        self.center = (current_width // 2, current_height // 2)

    def render_image(self):
        # Create high-resolution image
        hr_width = int(self.width * self.high_res_factor)
        hr_height = int(self.height * self.high_res_factor)
        hr_radius = self.radius * self.high_res_factor
        hr_pulse = self.pulse * self.high_res_factor
        hr_line_width = self.line_width * self.high_res_factor
        hr_center = (hr_width // 2, hr_height // 2)

        # Create blank image
        self.pil_image = Image.new("RGBA", (hr_width, hr_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(self.pil_image)

        # Draw circle
        current_radius = hr_radius + hr_pulse
        bbox = [
            hr_center[0] - current_radius,
            hr_center[1] - current_radius,
            hr_center[0] + current_radius,
            hr_center[1] + current_radius
        ]

        color = self.get_color()
        draw.ellipse(bbox, outline=color, width=int(hr_line_width))

        self.draw_symbols(draw, hr_center, hr_radius, hr_line_width)

        self.tk_image = ImageTk.PhotoImage(
            self.pil_image.resize((self.width, self.height), Image.LANCZOS)
        )

        if self.image_id is None:
            self.image_id = self.canvas.create_image(
                self.width // 2, self.height // 2, image=self.tk_image
            )
        else:
            self.canvas.itemconfig(self.image_id, image=self.tk_image)

    def draw_symbols(self, draw, center, radius, line_width):
        color = self.get_color()
        x, y = center
        hr_line_width = line_width / 2

        if self.symbol_index == 1:  # Cross
            size = radius * 0.15
            draw.line(
                [x - size, y - size, x + size, y + size],
                fill=color,
                width=int(hr_line_width)
            )
            draw.line(
                [x + size, y - size, x - size, y + size],
                fill=color,
                width=int(hr_line_width))

        elif self.symbol_index == 2:  # Check
            size = 25 * self.high_res_factor
            base_y = y + 5 * self.high_res_factor
            points = [
                x - size + 5 * self.high_res_factor, base_y - size // 6,
                x - size // 4, base_y + size // 3,
                x + size - 5 * self.high_res_factor, base_y - size // 2
            ]
            draw.line(points, fill=color, width=int(hr_line_width))

        elif self.symbol_index == 3:  # Ellipsis
            dot_size = radius * 0.06
            spacing = radius * 0.2
            offsets = [-spacing, 0, spacing]
            for i, offset in enumerate(offsets):
                bounce_height = radius * 0.1 * math.sin(self.phase + i * 0.5)
                bbox = [
                    x + offset - dot_size, y - dot_size + bounce_height,
                    x + offset + dot_size, y + dot_size + bounce_height
                ]
                draw.ellipse(bbox, fill=color)

    def set_size(self, width, height):
        self.width = width
        self.height = height
        self._calculate_scale()
        self.center = (self.width // 2, self.height // 2)
        self.canvas.config(width=self.width, height=self.height)
        self.render_image()

    def set_line_width(self, value):
        self.base_line_width = int(value)
        self.line_width = self.base_line_width * self.scale_factor
        self.render_image()

    def toggle_colors(self):
        self.hue_mode = not self.hue_mode
        self.render_image()

    def toggle_animation(self):
        self.animating = not self.animating
        if self.animating:
            self.animate()

    def reset_animation(self):
        self.pulse = 0.0
        self.hue = 0.0
        self.phase = 0.0
        self.render_image()

    def set_color(self, color_string):
        self.color = color_string
        self.render_image()

    def get_color(self):
        if not self.hue_mode:
            return self.color
        else:
            hue = self.hue % 1.0
            rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            return "#{:02x}{:02x}{:02x}".format(*(int(c * 255) for c in rgb))

    def animate(self):
        if not self.animating:
            self.last_frame_time = 0
            return

        now = time.time() * 1000
        if self.last_frame_time == 0:
            delta_time = 16
        else:
            delta_time = now - self.last_frame_time
            delta_time = max(delta_time, 1)

        self.last_frame_time = now

        self.phase += self.animation_step * (delta_time / 16)
        self.pulse = self.radius * 0.1 * math.sin(self.phase)

        if self.hue_mode:
            self.hue += 0.005

        self.render_image()
        self.canvas.after(10, self.animate)

    def toggle_symbol(self):
        self.symbol_index = (self.symbol_index + 1) % 4
        self.render_image()

    def set_symbol(self, index):
        self.symbol_index = index
        self.render_image()


if __name__ == "__main__":
    root = Tk()
    breathing_circle = BreathingCircle(width=600, height=600)
    canvas = breathing_circle.create_canvas(root, "white")
    canvas.pack()

    Button(root, text="Resize",
           command=lambda: breathing_circle.set_size(300, 300)).pack()
    Button(root, text="Start/Stop", command=breathing_circle.toggle_animation).pack()
    Button(root, text="Change Color", command=breathing_circle.toggle_colors).pack()
    Button(root, text="Toggle Symbol", command=breathing_circle.toggle_symbol).pack()
    Scale(root, from_=1, to=10, orient=HORIZONTAL,
          command=breathing_circle.set_line_width).pack()

    root.mainloop()