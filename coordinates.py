from astro_pi_orbit import ISS
from datetime import UTC, datetime
from skyfield.api import load
from time import sleep

time = 1.0 # seconds

iss = ISS()
time_scale = load.timescale()

average = 0
gsd = 0
sensor_width = 7.564  # in mm for Raspberry Pi Camera
focal_length = 11.8  # in mm
count 	= 0
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
    altitude = position_2.distance().m * 1000
    print(f'velocity = {velocity:.4f} km/s, distance = {distance_km} km')
    print(f'Altitude: {altitude:.4f} m')
    average = (count * average + velocity) / (count + 1)
    count += 1
    print(f'The average velocity of the ISS is {average:.4f}')
    Dw = sensor_width * altitude / focal_length / 1000000  # in kilometers per pixel
    print(f'The Dw is {Dw:.4f}km')
    print(f'The velocity is {velocity:.4f}km/s \n')