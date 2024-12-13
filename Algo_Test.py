import tkinter as tk
from tkinter import Label
import threading
import time
import firebase_admin
from firebase_admin import credentials, db

# Initialize Firebase Admin
cred = credentials.Certificate('C:/Users/HP/PycharmProjects/Algorithm/credentials/Key.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://sihbytebenders2-default-rtdb.asia-southeast1.firebasedatabase.app/'
})


def get_traffic_data():
    """Fetch the remaining car count and light state for each lane."""
    traffic_data = {}
    for lane in ["Lane_1", "Lane_2", "Lane_3", "Lane_4"]:
        ref = db.reference(f'traffic_data/{lane}')
        data = ref.get()
        traffic_data[lane] = {
            'light_state': data.get('light_state', 2),
            'time_allocated': data.get('time_allocated', 0),
            'car_count': db.reference(f'Car_Count/{lane}/car_count').get()
        }
    return traffic_data


def update_ui():
    """Periodically update the UI with real-time data."""
    traffic_data = get_traffic_data()
    for lane, data in traffic_data.items():
        car_count_labels[lane].config(text=f"Cars: {data['car_count']}")

        # Manage the countdown locally
        remaining_time = int(time_labels[lane].cget("text").split(":")[1][:-1])  # Extract remaining time from label
        if remaining_time > 0:
            remaining_time -= 1
        else:
            remaining_time = data['time_allocated']

        time_labels[lane].config(text=f"Time: {remaining_time}s")

        # Update light colors
        if data['light_state'] == 0:  # Green
            light_labels[lane]['green'].config(bg='green')
            light_labels[lane]['yellow'].config(bg='gray')
            light_labels[lane]['red'].config(bg='gray')
        elif data['light_state'] == 1:  # Yellow
            light_labels[lane]['green'].config(bg='gray')
            light_labels[lane]['yellow'].config(bg='yellow')
            light_labels[lane]['red'].config(bg='gray')
        else:  # Red
            light_labels[lane]['green'].config(bg='gray')
            light_labels[lane]['yellow'].config(bg='gray')
            light_labels[lane]['red'].config(bg='red')

    root.after(1000, update_ui)  # Schedule the update_ui function to run every second



# Create the main Tkinter window
root = tk.Tk()
root.title("Traffic Control System")
root.geometry("600x400")
root.configure(bg="black")

# Create a frame for each lane
lanes = ["Lane_1", "Lane_2", "Lane_3", "Lane_4"]
frames = {}
car_count_labels = {}
time_labels = {}
light_labels = {}

for i, lane in enumerate(lanes):
    frame = tk.Frame(root, width=150, height=200, relief='solid', bd=1, bg="black")
    frame.grid(row=0, column=i, padx=10, pady=10)

    lane_label = Label(frame, text=lane, font=("Arial", 16), bg="black", fg="white")
    lane_label.pack(pady=5)

    car_count_label = Label(frame, text="Cars: 0", font=("Arial", 14), bg="black", fg="white")
    car_count_label.pack(pady=5)
    car_count_labels[lane] = car_count_label

    time_label = Label(frame, text="Time: 0s", font=("Arial", 14), bg="black", fg="white")
    time_label.pack(pady=5)
    time_labels[lane] = time_label

    light_frame = tk.Frame(frame, bg="black")
    light_frame.pack(pady=10)

    red_light = Label(light_frame, bg="gray", width=5, height=2, relief='ridge')
    red_light.pack(side='top', pady=2)

    yellow_light = Label(light_frame, bg="gray", width=5, height=2, relief='ridge')
    yellow_light.pack(side='top', pady=2)

    green_light = Label(light_frame, bg="gray", width=5, height=2, relief='ridge')
    green_light.pack(side='top', pady=2)

    light_labels[lane] = {
        'red': red_light,
        'yellow': yellow_light,
        'green': green_light
    }

# Start the initial update
update_ui()

# Run the Tkinter main loop
root.mainloop()

