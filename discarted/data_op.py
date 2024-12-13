import time
import firebase_admin
from firebase_admin import credentials, db
from collections import deque

# Initialize Firebase Admin
cred = credentials.Certificate('C:/Users/HP/PycharmProjects/Algorithm/credentials/Key.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://sihbytebenders2-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

# Function to get car count from a specific node
def get_car_count(node):
    ref = db.reference(f'data/{node}/car_count')
    return ref.get()

# Function to update car count in a specific node
def update_car_count(node, count):
    ref = db.reference(f'data/{node}/car_count')
    print(f"Updating {node} with count: {count}")
    ref.set(count)

# Function to fetch car counts from all four nodes
def fetch_traffic_data():
    car_counts = {
        "Lane_A": get_car_count('Reno'),
        "Lane_B": get_car_count('Swarna'),
        "Lane_C": get_car_count('Harshendu'),
        "Lane_D": get_car_count('anirban'),
    }
    print(f"Fetched car counts: {car_counts}")
    return car_counts

# Function to control traffic lights
def control_traffic_lights(selected_lane, idle_times):
    lights = {lane: "Red" for lane in idle_times.keys()}
    lights[selected_lane] = "Green"

    print(f"Traffic Light States: {lights}")
    return lights

# Traffic control system with Weighted Round-Robin Scheduling
def traffic_control_system():
    lanes = ["Lane_A", "Lane_B", "Lane_C", "Lane_D"]
    total_cycle_time = 60  # Total cycle duration in seconds
    car_clearance_rate = 1  # Cars cleared per second
    min_time_threshold = 5  # Minimum time allocation for any lane (to avoid starvation)

    while True:
        print("\nFetching real-time traffic data from Firebase...")
        lane_counts = fetch_traffic_data()
        print(f"Traffic counts: {lane_counts}")

        total_cars = sum(lane_counts.values())
        if total_cars == 0:
            print("No traffic detected. All lanes remain red.")
            time.sleep(5)
            continue

        # Calculate weights and allocate time for each lane
        allocated_times = {}
        for lane in lanes:
            if total_cars > 0:
                weight = lane_counts[lane] / total_cars
                allocated_times[lane] = max(weight * total_cycle_time, min_time_threshold)
            else:
                allocated_times[lane] = min_time_threshold

        print(f"Allocated times (in seconds) for each lane: {allocated_times}")

        # Execute traffic control for each lane
        for lane in lanes:
            green_time = allocated_times[lane]
            cars_to_release = min(lane_counts[lane], int(green_time * car_clearance_rate))

            print(f"Releasing {cars_to_release} cars from {lane} for {green_time:.2f} seconds.")
            lane_counts[lane] -= cars_to_release

            # Update Firebase with the new car count
            node_mapping = {
                "Lane_A": "Reno",
                "Lane_B": "Swarna",
                "Lane_C": "Harshendu",
                "Lane_D": "anirban",
            }
            update_car_count(node_mapping[lane], lane_counts[lane])

            # Update traffic light states
            print("Updating traffic light states...")
            control_traffic_lights(lane, {l: 0 for l in lanes})

            time.sleep(green_time)  # Keep the light green for the allocated duration

# Start the traffic control system
if __name__ == "__main__":
    try:
        traffic_control_system()
    except KeyboardInterrupt:
        print("\nTraffic control system stopped.")