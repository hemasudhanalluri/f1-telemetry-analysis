import fastf1
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection

# Enable cache
fastf1.Cache.enable_cache('cache')

# Load session
session = fastf1.get_session(2025, 'Monaco', 'R')
session.load()

laps = session.laps

# Get driver list
drivers = session.drivers
team_colors = {
    'Red Bull': '#0600EF',     # Blue
    'Mercedes': '#000000',     # Black
    'Ferrari': '#DC0000',      # Red
    'McLaren': '#FF8700',      # Orange
    'Alpine': '#FF69B4',       # Pink
    'Williams': '#87CEEB',     # Sky Blue
    'AlphaTauri': '#2B4562',
    'RB': '#1E41FF',           # 🔵 Racing Bulls (similar to Red Bull but different)
    'Haas': '#BFBFBF'          # Grey
}

plt.figure()

for drv in drivers:
    drv_laps = laps.pick_drivers(drv)
    drv_laps = drv_laps[drv_laps['IsAccurate'] == True]

    if drv_laps.empty:
        continue 
    lap_times = drv_laps['LapTime'].dt.total_seconds()

    team = drv_laps['Team'].iloc[0]
    if team == 'AlphaTauri':
       team = 'RB'

    color = team_colors.get(team, 'black')

    plt.plot(drv_laps['LapNumber'], drv_laps['LapTime'],
             label=drv, color=color)

plt.title("Lap Time Comparison (All Drivers)")
plt.xlabel("Lap Number")
plt.ylabel("Lap Time")

plt.legend(fontsize=6)
plt.show()

# -------------------------------
# 3. AVERAGE SPEED COMPARISON
# -------------------------------
avg_speeds = []
driver_names = []
colors = []

for drv in session.drivers:
    drv_laps = laps.pick_drivers(drv)
    drv_laps = drv_laps[drv_laps['IsAccurate'] == True]

    if drv_laps.empty:
        continue

    lap = drv_laps.pick_fastest()
    car_data = lap.get_car_data()

    avg_speed = car_data['Speed'].mean()

    avg_speeds.append(avg_speed)
    driver_names.append(drv)

    team = drv_laps['Team'].iloc[0]
    colors.append(team_colors.get(team, 'black'))

plt.figure()
plt.bar(driver_names, avg_speeds, color=colors)
plt.title("Average Speed Comparison")
plt.xlabel("Drivers")
plt.ylabel("Speed (km/h)")
plt.xticks(rotation=90)
plt.show()
fastest_lap = laps.pick_fastest()

car_data = fastest_lap.get_car_data().add_distance()
pos_data = fastest_lap.get_pos_data()

# Merge safely (fix for KeyError 'X')
telemetry = car_data.merge(pos_data, on='Time')

x = telemetry['X']
y = telemetry['Y']
speed = telemetry['Speed']

points = np.array([x, y]).T.reshape(-1, 1, 2)
segments = np.concatenate([points[:-1], points[1:]], axis=1)

lc = LineCollection(segments)
lc.set_array(speed)
lc.set_linewidth(4)

plt.figure()
plt.gca().add_collection(lc)
plt.axis('equal')
plt.title("Track Map (Speed Visualization)")
plt.colorbar(lc, label="Speed (km/h)")
plt.show()

plt.figure()

plt.plot(car_data['Distance'], car_data['Throttle'], label='Throttle')
plt.plot(car_data['Distance'], car_data['Brake'], label='Brake')

# Some sessions may not have DRS → safe check
if 'DRS' in car_data.columns:
    plt.plot(car_data['Distance'], car_data['DRS'], label='DRS')

plt.legend()
plt.title("Throttle vs Brake vs DRS")
plt.xlabel("Distance (m)")
plt.show()

clean_laps = laps[laps['IsAccurate'] == True]

avg_time = clean_laps['LapTime'].dt.total_seconds().mean()

slow_laps = clean_laps[
    clean_laps['LapTime'].dt.total_seconds() > avg_time
]

print("\nPossible Safety Car / Slow Laps:")
print(slow_laps[['Driver', 'LapNumber', 'LapTime']])