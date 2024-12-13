import time
import threading
import tkinter as tk
from tkinter import ttk
import firebase_admin
from firebase_admin import credentials, db

# Initialize Firebase Admin
cred = credentials.Certificate('C:/Users/HP/PycharmProjects/Algorithm/credentials/Key.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://sihbytebenders2-default-rtdb.asia-southeast1.firebasedatabase.app/'
})


# Function to get car count from a specific node
def get_car_count(node):
    ref = db.reference(f'data/{node}/car_count')
    return ref.get() or 0


# Function to update car count in a specific node
def update_car_count(node, count):
    ref = db.reference(f'data/{node}/car_count')
    ref.set(count)


# Function to fetch car counts from all four nodes
def fetch_traffic_data():
    return {
        "Lane_A": get_car_count('Reno'),
        "Lane_B": get_car_count('Swarna'),
        "Lane_C": get_car_count('Harshendu'),
        "Lane_D": get_car_count('anirban'),
    }


# GUI class for traffic signal system
class TrafficSignalGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("4-Way Traffic Signal System")

        self.lanes = ["Lane_A", "Lane_B", "Lane_C", "Lane_D"]
        self.lights = {lane: "Red" for lane in self.lanes}
        self.car_counts = {lane: 0 for lane in self.lanes}
        self.timers = {lane: 0.00 for lane in self.lanes}

        self.create_gui()
        self.update_traffic_data()

    def create_gui(self):
        self.frames = {}
        self.labels = {}
        self.timer_labels = {}
        self.light_canvases = {}

        for idx, lane in enumerate(self.lanes):
            frame = ttk.LabelFrame(self.root, text=f"{lane}")
            frame.grid(row=0, column=idx, padx=10, pady=10)
            self.frames[lane] = frame

            car_label = ttk.Label(frame, text=f"Cars: {self.car_counts[lane]}")
            car_label.pack(pady=5)
            self.labels[lane] = car_label

            timer_label = ttk.Label(frame, text=f"Time: {self.timers[lane]:.2f}s")
            timer_label.pack(pady=5)
            self.timer_labels[lane] = timer_label

            # Create Canvas for traffic lights with black background
            canvas = tk.Canvas(frame, width=80, height=220, bg="black")
            canvas.pack(pady=5)
            self.light_canvases[lane] = {
                "canvas": canvas,
                "red": canvas.create_oval(10, 10, 70, 70, fill="gray"),
                "yellow": canvas.create_oval(10, 80, 70, 140, fill="gray"),
                "green": canvas.create_oval(10, 150, 70, 210, fill="gray"),
            }

    def update_gui(self):
        for lane in self.lanes:
            self.labels[lane].config(text=f"Cars: {self.car_counts[lane]}")
            self.timer_labels[lane].config(text=f"Time: {self.timers[lane]:.2f}s")
            self.update_light(lane, self.lights[lane])

    def update_light(self, lane, state):
        canvas = self.light_canvases[lane]["canvas"]
        # Reset all lights to gray
        for light in ["red", "yellow", "green"]:
            canvas.itemconfig(self.light_canvases[lane][light], fill="gray")
        # Set the active light
        if state == "Red":
            canvas.itemconfig(self.light_canvases[lane]["red"], fill="red")
        elif state == "Yellow":
            canvas.itemconfig(self.light_canvases[lane]["yellow"], fill="yellow")
        elif state == "Green":
            canvas.itemconfig(self.light_canvases[lane]["green"], fill="green")

    def countdown_timer(self, lane, duration):
        for i in range(int(duration * 10), -1, -1):
            self.timers[lane] = i / 10.0
            self.update_gui()
            time.sleep(0.1)

    def update_traffic_data(self):
        self.car_counts = fetch_traffic_data()
        self.root.after(1000, self.update_traffic_data)  # Refresh every second

    def control_traffic_lights(self):
        total_cycle_time = 60
        min_time_threshold = 5
        car_clearance_rate = 1

        while True:
            lane_counts = fetch_traffic_data()
            total_cars = sum(lane_counts.values())

            if total_cars == 0:
                time.sleep(5)
                continue

            # Calculate time allocation for each lane
            allocated_times = {}
            for lane in self.lanes:
                if total_cars > 0:
                    weight = lane_counts[lane] / total_cars
                    allocated_times[lane] = max(weight * total_cycle_time, min_time_threshold)
                else:
                    allocated_times[lane] = min_time_threshold

            # Process each lane
            for lane in self.lanes:
                green_time = allocated_times[lane]
                yellow_time = 3  # Fixed duration for yellow light

                # Transition: Red → Yellow
                self.lights = {l: "Red" for l in self.lanes}
                self.lights[lane] = "Yellow"
                self.timers = {l: yellow_time if l == lane else 0 for l in self.lanes}
                self.update_gui()
                self.countdown_timer(lane, yellow_time)

                # Transition: Yellow → Green
                self.lights[lane] = "Green"
                self.timers = {l: green_time if l == lane else 0 for l in self.lanes}
                self.update_gui()
                self.countdown_timer(lane, green_time)

                # Transition: Green → Yellow → Red
                self.lights[lane] = "Yellow"
                self.timers = {l: yellow_time if l == lane else 0 for l in self.lanes}
                self.update_gui()
                self.countdown_timer(lane, yellow_time)

                # Update car counts after Green phase
                cars_released = min(lane_counts[lane], int(green_time * car_clearance_rate))
                lane_counts[lane] -= cars_released
                update_car_count(lane.split("_")[1].lower(), lane_counts[lane])


# Run the GUI and traffic control system
def main():
    root = tk.Tk()
    gui = TrafficSignalGUI(root)
    threading.Thread(target=gui.control_traffic_lights, daemon=True).start()
    root.mainloop()


if __name__ == "__main__":
    main()