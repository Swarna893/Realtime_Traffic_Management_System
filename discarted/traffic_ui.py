import tkinter as tk
from threading import Thread
import time
from discarted.data_op import fetch_traffic_data, update_car_count, control_traffic_lights

class TrafficControlGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Traffic Light Control System")
        self.lane_names = ["Lane_A", "Lane_B", "Lane_C", "Lane_D"]
        self.frames = {}
        self.car_counts = {}
        self.lights = {}
        self.time_labels = {}
        self.init_gui()

    def init_gui(self):
        for index, lane in enumerate(self.lane_names):
            frame = tk.Frame(self.root, relief=tk.RAISED, borderwidth=2, padx=10, pady=10)
            frame.grid(row=0, column=index, padx=10, pady=10)

            tk.Label(frame, text=lane, font=("Arial", 14)).pack(pady=5)

            # Traffic light representation
            canvas = tk.Canvas(frame, width=80, height=220, bg="white")
            canvas.pack(pady=10)
            self.draw_traffic_light_box(canvas)

            # Draw the lights inside the box
            red_light = canvas.create_oval(20, 20, 60, 60, fill="gray")
            yellow_light = canvas.create_oval(20, 80, 60, 120, fill="gray")
            green_light = canvas.create_oval(20, 140, 60, 180, fill="gray")

            self.lights[lane] = {
                "canvas": canvas,
                "ovals": {"red": red_light, "yellow": yellow_light, "green": green_light},
            }

            # Car count
            tk.Label(frame, text="Car Count:", font=("Arial", 12)).pack()
            count_label = tk.Label(frame, text="0", font=("Arial", 14), fg="blue")
            count_label.pack()
            self.car_counts[lane] = count_label

            # Time label
            tk.Label(frame, text="Time Allocated:", font=("Arial", 12)).pack()
            time_label = tk.Label(frame, text="0s", font=("Arial", 14), fg="green")
            time_label.pack()
            self.time_labels[lane] = time_label

    def draw_traffic_light_box(self, canvas):
        """Draw a rounded rectangle for the traffic light box."""
        canvas.create_rectangle(10, 10, 70, 210, fill="black", outline="black")

    def update_gui(self, traffic_data, lights_state, allocated_times):
        """Update the GUI with real-time traffic data and light states."""
        for lane in self.lane_names:
            # Update car counts
            self.car_counts[lane].config(text=str(traffic_data.get(lane, 0)))

            # Update allocated time
            self.time_labels[lane].config(text=f"{allocated_times.get(lane, 0):.0f}s")

            # Update lights
            for color in ["red", "yellow", "green"]:
                color_fill = "gray"
                if color == lights_state.get(lane, "red").lower():
                    color_fill = color
                self.lights[lane]["canvas"].itemconfig(self.lights[lane]["ovals"][color], fill=color_fill)

    def stop(self):
        """Stop the GUI."""
        self.running = False


# Traffic control logic in a separate thread
def traffic_control(gui):
    lanes = gui.lane_names
    idle_times = {lane: 0 for lane in lanes}
    total_cycle_time = 60  # Total cycle duration in seconds
    min_time_threshold = 5  # Minimum time per lane

    while True:
        # Fetch real-time traffic data
        traffic_data = fetch_traffic_data()
        total_cars = sum(traffic_data.values())

        # Calculate allocated times for each lane
        allocated_times = {}
        for lane in lanes:
            if total_cars > 0:
                weight = traffic_data[lane] / total_cars
                allocated_times[lane] = max(weight * total_cycle_time, min_time_threshold)
            else:
                allocated_times[lane] = min_time_threshold

        # Control traffic lights lane by lane
        for lane in lanes:
            # Set the current lane to green
            lights_state = control_traffic_lights(lane, idle_times)
            gui.update_gui(traffic_data, lights_state, allocated_times)

            # Simulate traffic clearance
            green_time = allocated_times[lane]
            time.sleep(green_time)  # Keep the light green for the allocated duration

            # Update traffic data
            cars_cleared = min(traffic_data[lane], int(green_time))
            traffic_data[lane] -= cars_cleared
            update_car_count(lane, traffic_data[lane])

        # Update idle times
        for lane in lanes:
            idle_times[lane] += 1


if __name__ == "__main__":
    root = tk.Tk()
    gui = TrafficControlGUI(root)

    # Start the traffic control system in a separate thread
    Thread(target=traffic_control, args=(gui,), daemon=True).start()

    try:
        root.mainloop()
    except KeyboardInterrupt:
        gui.stop()
