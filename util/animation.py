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

        self.circle_id = None
        self.symbol_ids = []

    def create_canvas(self, master, bg, width=500, height=500):
        self.canvas = Canvas(master, width=width, height=height,
                             bg=bg, highlightthickness=0)
        self.init_shapes()
        self._calculate_scale()
        return self.canvas

    def init_shapes(self):
        self.circle_id = self.canvas.create_oval(0, 0, 0, 0, outline="")
        self.symbol_ids = [
            self.canvas.create_line(0, 0, 0, 0, fill="", width=0),  # cross
            self.canvas.create_line(0, 0, 0, 0, fill="", width=0),  # cross
            self.canvas.create_line(0, 0, 0, 0, fill="", smooth=False),  # check
            self.canvas.create_oval(0, 0, 0, 0, fill="", outline=""),  # dot1
            self.canvas.create_oval(0, 0, 0, 0, fill="", outline=""),  # dot2
            self.canvas.create_oval(0, 0, 0, 0, fill="", outline=""),  # dot3
        ]

    def _calculate_scale(self):
        current_width = self.canvas.winfo_width()
        current_height = self.canvas.winfo_height()
        self.scale_factor = min(current_width, current_height) / self.base_size
        self.radius = self.base_radius * self.scale_factor
        self.line_width = self.base_line_width * self.scale_factor
        self.center = (current_width // 2, current_height // 2)

    def update_circle(self):
        current_radius = self.radius + self.pulse
        x0 = self.center[0] - current_radius
        y0 = self.center[1] - current_radius
        x1 = self.center[0] + current_radius
        y1 = self.center[1] + current_radius

        self.canvas.coords(self.circle_id, x0, y0, x1, y1)
        self.canvas.itemconfig(self.circle_id,
                               outline=self.get_color(),
                               width=self.line_width)

    def update_symbols(self):
        color = self.get_color()
        x, y = self.center
        line_width = self.line_width / 2

        for item in self.symbol_ids:
            self.canvas.itemconfig(item, fill="")

        if self.symbol_index == 1:  # Cross
            size = self.radius * 0.15
            self.canvas.coords(self.symbol_ids[0],
                               x - size, y - size, x + size, y + size)
            self.canvas.itemconfig(self.symbol_ids[0],
                                   fill=color, width=line_width)
            self.canvas.coords(self.symbol_ids[1],
                               x + size, y - size, x - size, y + size)
            self.canvas.itemconfig(self.symbol_ids[1],
                                   fill=color, width=line_width)

        elif self.symbol_index == 2:  # Check
            size = 25
            base_y = y + 5
            points = [
                x - size + 5, base_y - size // 6,
                x - size // 4, base_y + size // 3,
                x + size - 5, base_y - size // 2
            ]
            self.canvas.coords(self.symbol_ids[2], *points)
            self.canvas.itemconfig(self.symbol_ids[2],
                                   fill=color, width=line_width)

        elif self.symbol_index == 3:  # Ellipsis
            dot_size = self.radius * 0.06
            spacing = self.radius * 0.2
            for i, offset in enumerate([-spacing, 0, spacing]):
                self.canvas.coords(self.symbol_ids[3 + i],
                                   x + offset - dot_size, y - dot_size,
                                   x + offset + dot_size, y + dot_size)
                self.canvas.itemconfig(self.symbol_ids[3 + i], fill=color)

    def set_size(self, width, height):
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
        self._calculate_scale()
        self.update_circle()
        self.update_symbols()

    def animate(self):
        if self.animating:
            self.phase += 0.025
            self.pulse = self.radius * 0.1 * math.sin(self.phase)
            self.hue = (self.hue + 0.01) % 1.0
            self.draw_circle()
            self.canvas.after_id = self.canvas.after(16, self.animate)

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
