from astro_pi_orbit import ISS
from datetime import UTC, datetime
from skyfield.api import load
from time import sleep

time = 0.5 # seconds

iss = ISS()
time_scale = load.timescale()

average = 0
gsd = 0
sensor_width = 7.564  # in mm for Raspberry Pi Camera
focal_length = 35  # in mm
count 	= 0
altitude_values = []
for _ in range(100):
    time_1 = datetime.now(UTC)
    moment_1 = time_scale.from_datetime(time_1)
    position_1 = iss.at(moment_1)

    sleep(time)

    time_2 = datetime.now(UTC)
    moment_2 = time_scale.from_datetime(time_2)
    position_2 = iss.at(moment_2)

    diff = position_2 - position_1
    distance_km = diff.distance().km
    velocity = distance_km / time
    altitude = position_2.distance().m
    altitude_values.append(altitude)
    print(f'{velocity:.4f}')
    print(f'Altitude: {altitude:.4f} m')
    average = (count * average + velocity) / (count + 1)
    count += 1
    print(f'The average velocity of the ISS is {average:.4f}')
    gsd = sensor_width * altitude / (focal_length * 1000)  # in meters per pixel
    print(f'The gsd is {gsd:.4f}')


