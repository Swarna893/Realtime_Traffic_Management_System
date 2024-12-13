import time
import firebase_admin
from firebase_admin import credentials, db

# Initialize Firebase Admin
cred = credentials.Certificate('C:/Users/HP/PycharmProjects/Algorithm/credentials/Key.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://sihbytebenders2-default-rtdb.asia-southeast1.firebasedatabase.app/'
})


# Function to get car count from a specific node
def get_car_count(node):
    ref = db.reference(f'Car_Count/{node}/car_count')
    return ref.get()


# Function to update car count in a specific node
def update_car_count(node, count):
    ref = db.reference(f'Car_Count/{node}/car_count')
    ref.set(count)


# Function to fetch car counts from all four nodes
def fetch_traffic_data():
    car_counts = {
        "Lane_1": get_car_count('Lane_1'),
        "Lane_2": get_car_count('Lane_2'),
        "Lane_3": get_car_count('Lane_3'),
        "Lane_4": get_car_count('Lane_4'),
    }
    return car_counts


# Function to update traffic lights and time allocation in Firebase
def update_traffic_data(node, light_state, time_allocated):
    ref = db.reference(f'traffic_data/{node}')
    ref.update({
        'light_state': light_state,
        'time_allocated': time_allocated
    })


# Function to update proportion data in Firebase
def update_proportion_data(node, proportion):
    ref = db.reference(f'Density_Data/{node}')
    ref.set({
        'Density': proportion
    })


# Function to control traffic lights and update Firebase
def control_traffic_lights(selected_lane, idle_times, allocated_times):
    lights = {lane: 2 for lane in idle_times}  # Initialize all lights to red (2)

    # Transition all to red first
    for lane in idle_times:
        update_traffic_data(lane, 2, 0)  # Red light with no time allocated

    # Set the selected lane to yellow before green
    update_traffic_data(selected_lane, 1, 3)  # Yellow light for 3 seconds
    time.sleep(3)

    # Calculate green light time ensuring it's never negative
    green_light_time = max(allocated_times[selected_lane] - 6, 0)  # Ensure green time is non-negative

    # Now set to green
    lights[selected_lane] = 0  # Set the selected lane light to green (0)
    update_traffic_data(selected_lane, 0, green_light_time)
    time.sleep(green_light_time)

    # Transition from green to yellow before red
    update_traffic_data(selected_lane, 1, 3)  # Yellow light for 3 seconds
    time.sleep(3)

    # Finally set to red again
    update_traffic_data(selected_lane, 2, 0)  # Red light with no time allocated

    return lights


# Traffic control system with Weighted Round-Robin Scheduling
def traffic_control_system():
    lanes = ["Lane_1", "Lane_2", "Lane_3", "Lane_4"]
    node_mapping = {
        "Lane_1": "Lane_1",
        "Lane_2": "Lane_2",
        "Lane_3": "Lane_3",
        "Lane_4": "Lane_4",
    }
    total_cycle_time = 60  # Total cycle duration in seconds
    car_clearance_rate = 1  # Cars cleared per second
    min_time_threshold = 5  # Minimum time allocation for any lane

    while True:
        lane_counts = fetch_traffic_data()
        total_cars = sum(lane_counts.values())
        allocated_times = {}
        proportions = {}  # Dictionary to store the time proportions for each lane

        for lane in lanes:
            weight = lane_counts[lane] / total_cars if total_cars > 0 else 0
            allocated_times[lane] = max(weight * total_cycle_time, min_time_threshold)
            proportions[lane] = round(allocated_times[lane] / total_cycle_time, 2)  # Rounded to two decimal places
            update_proportion_data(node_mapping[lane], proportions[lane])

        for lane in lanes:
            update_car_count(node_mapping[lane],
                             max(lane_counts[lane] - int(allocated_times[lane] * car_clearance_rate), 0))
            control_traffic_lights(lane, {l: 2 for l in lanes}, allocated_times)


if __name__ == "__main__":
    try:
        traffic_control_system()
    except KeyboardInterrupt:
        print("\nTraffic control system stopped.")
