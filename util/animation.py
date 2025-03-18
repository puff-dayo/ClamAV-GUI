import colorsys
import math
from tkinter import *


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

    def create_canvas(self, master, bg, width=500, height=500):
        self.canvas = Canvas(master, width=width, height=height,
                             bg=bg, highlightthickness=0)
        self.draw_circle()
        self._calculate_scale()
        return self.canvas

    def _calculate_scale(self):
        """Dynamically calculate scale based on actual canvas size"""
        current_width = self.canvas.winfo_width()
        current_height = self.canvas.winfo_height()
        self.scale_factor = min(current_width, current_height) / self.base_size
        self.radius = self.base_radius * self.scale_factor
        self.line_width = self.base_line_width * self.scale_factor
        self.center = (current_width // 2, current_height // 2)

    def set_size(self, width, height):
        """Update canvas size and redraw"""
        self.width = width
        self.height = height
        self._calculate_scale()
        self.center = (self.width // 2, self.height // 2)
        self.canvas.config(width=self.width, height=self.height)
        self.draw_circle()

    def set_line_width(self, value):
        self.base_line_width = int(value)
        self.line_width = self.base_line_width * self.scale_factor
        self.draw_circle()

    def toggle_colors(self):
        self.hue_mode = True
        self.draw_circle()

    def toggle_animation(self):
        self.animating = not self.animating
        if self.animating:
            self.animate()

    def reset_animation(self):
        self.pulse = 0.0
        self.hue = 0.0
        self.phase = 0.0
        self.draw_circle()

    def set_color(self, color_string):
        self.color = color_string

    def get_color(self):
        if not self.hue_mode:
            return self.color
        else:
            hue = self.hue % 1.0
            rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            return "#{:02x}{:02x}{:02x}".format(*(int(c * 255) for c in rgb))

    def draw_circle(self):
        self.canvas.delete('all')
        self._calculate_scale()

        current_radius = self.radius + self.pulse
        x0 = self.center[0] - current_radius
        y0 = self.center[1] - current_radius
        x1 = self.center[0] + current_radius
        y1 = self.center[1] + current_radius
        self.canvas.create_oval(x0, y0, x1, y1,
                                width=self.line_width, outline=self.get_color())

        x, y = self.center
        if self.symbol_index == 1:  # Cross
            size = self.radius * 0.15
            self.canvas.create_line(x - size, y - size, x + size, y + size,
                                    width=self.line_width / 2, fill=self.get_color())
            self.canvas.create_line(x + size, y - size, x - size, y + size,
                                    width=self.line_width / 2, fill=self.get_color())
        elif self.symbol_index == 2:  # Check
            size = 25
            base_y = self.center[1] + 5
            points = [
                self.center[0] - size + 5,
                base_y - size // 6,
                self.center[0] - size // 4,
                base_y + size // 3,
                self.center[0] + size - 5,
                base_y - size // 2
            ]
            self.canvas.create_line(
                points,
                fill=self.get_color(),
                width=self.line_width / 2,
                smooth=False
            )
        elif self.symbol_index == 3:  # Ellipsis
            dot_size = self.radius * 0.06
            spacing = self.radius * 0.2
            self.canvas.create_oval(x - spacing - dot_size, y - dot_size,
                                    x - spacing + dot_size, y + dot_size,
                                    fill=self.get_color())
            self.canvas.create_oval(x - dot_size, y - dot_size,
                                    x + dot_size, y + dot_size,
                                    fill=self.get_color())
            self.canvas.create_oval(x + spacing - dot_size, y - dot_size,
                                    x + spacing + dot_size, y + dot_size,
                                    fill=self.get_color())

    def animate(self):
        if self.animating:
            self.phase += 0.025
            self.pulse = self.radius * 0.1 * math.sin(self.phase)
            self.hue = (self.hue + 0.01) % 1.0
            self.draw_circle()
            self.canvas.after(16, self.animate)

    def toggle_symbol(self):
        self.symbol_index = (self.symbol_index + 1) % 4
        self.draw_circle()

    def set_symbol(self, index):
        self.symbol_index = index
        self.draw_circle()


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
