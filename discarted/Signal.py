import tkinter as tk

class TrafficControlGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Traffic Light Simulation")
        self.frames = {}
        self.car_counts = {}
        self.lights = {}
        self.init_gui()

    def init_gui(self):
        lanes = ["Lane 1", "Lane 2", "Lane 3", "Lane 4"]
        for index, lane in enumerate(lanes):
            frame = tk.Frame(self.root, relief=tk.RAISED, borderwidth=2, padx=10, pady=10)
            frame.grid(row=0, column=index, padx=10, pady=10)

            tk.Label(frame, text=lane, font=("Arial", 14)).pack(pady=5)

            # Traffic light representation
            canvas = tk.Canvas(frame, width=80, height=220, bg="white")  # Transparent canvas
            canvas.pack(pady=10)

            # Draw a rounded rectangle for the traffic light box
            self.draw_rounded_rectangle(canvas, 10, 10, 70, 210, 20, fill="black", outline="black")

            # Draw the lights inside the box
            red_light = canvas.create_oval(20, 20, 60, 60, fill="gray")
            yellow_light = canvas.create_oval(20, 80, 60, 120, fill="gray")
            green_light = canvas.create_oval(20, 140, 60, 180, fill="gray")

            self.lights[lane] = {
                "canvas": canvas,
                "ovals": {"red": red_light, "yellow": yellow_light, "green": green_light},
            }

            # Car count display
            tk.Label(frame, text="Car Count:", font=("Arial", 12)).pack()
            count_label = tk.Label(frame, text="0", font=("Arial", 14), fg="blue")
            count_label.pack()
            self.car_counts[lane] = count_label

    def draw_rounded_rectangle(self, canvas, x1, y1, x2, y2, radius, **kwargs):
        """Draw a rounded rectangle on the canvas."""
        points = [
            (x1 + radius, y1),
            (x2 - radius, y1),
            (x2 - radius, y1 + radius),
            (x2, y1 + radius),
            (x2, y2 - radius),
            (x2 - radius, y2 - radius),
            (x2 - radius, y2),
            (x1 + radius, y2),
            (x1 + radius, y2 - radius),
            (x1, y2 - radius),
            (x1, y1 + radius),
            (x1 + radius, y1 + radius),
        ]
        canvas.create_polygon(points, smooth=True, **kwargs)


if __name__ == "__main__":
    root = tk.Tk()
    gui = TrafficControlGUI(root)
    root.mainloop()
