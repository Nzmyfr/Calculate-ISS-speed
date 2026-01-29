#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS Speed Calculator

This program calculates the average speed of the International Space Station (ISS)
by capturing multiple images using the Picamera, extracting timestamps from
EXIF data, and comparing ISS positions at different times. It also collects
sensor data from the Sense HAT including temperature, pressure, humidity,
orientation, magnetometer, accelerometer, and gyroscope readings.

The program runs for a specified time duration - 10 minutes,
saving results to a CSV file and computing the average ISS speed.

Authors: Alexander Tonev, Alexander Veselinov
Mentor: Nikolay Cholakov
Date: 2026-01-29
Version: 1.0

Dependencies:
    - picamzero: Camera control
    - exif: EXIF data extraction
    - astro_pi_orbit: ISS tracking
    - skyfield: Astronomical calculations
    - sense_hat: Sense HAT sensor readings
"""

from datetime import datetime, UTC
start_time = datetime.now()

from picamzero import Camera
from exif import Image
import os

from astro_pi_orbit import ISS
from skyfield.api import load

from sense_hat import SenseHat
from csv import writer

#image_index = 1
    
"""
Extract latitude, longitude, and altitude from ISS position.

Parameters:
    position: ISS position from astro_pi_orbit

Returns:
    latitude, longitude, altitude_km
"""
def get_iss_position_data(position):
    try:
        # Get subpoint (latitude, longitude on Earth's surface)
        subpoint = position.subpoint()
        latitude = subpoint.latitude.degrees
        longitude = subpoint.longitude.degrees
        
        # Get altitude (distance from Earth's center minus Earth's radius)
        distance = position.distance()
        altitude_km = distance.km - 6371.0  # Earth's mean radius in km
        
        return latitude, longitude, altitude_km
    except Exception as e:
        print(f'Error extracting ISS position: {e}')
        return 0.0, 0.0, 0.0
# End of get_iss_position_data()

"""
Extract the timestamp from an image's EXIF data.

Parameters:
    image: Path to the image file

Returns:
    datetime: The datetime when the photo was taken in UTC
"""
def get_time(image):
    try:
        with open(image, 'rb') as image_file:
            img = Image(image_file)
            time_str = img.get('datetime_original')
            if time_str is None:
                raise ValueError(f'No datetime_original EXIF data found in {image}')
            time = datetime.strptime(time_str, '%Y:%m:%d %H:%M:%S')
            return time.replace(tzinfo=UTC)
    except Exception as e:
        print(f'Error extracting time from {image}: {e}')
        raise
# End of get_time()

"""
Save the calculated ISS speed result to a file.

Parameters:
    estimate_kmps: The calculated ISS speed in km/s
    file_path: Path to the output file
"""
def save_result(estimate_kmps, file_path):
    try:
        # Format the estimate_kmps to have a precision of 4 decimal places
        estimate_kmps_formatted = f'{estimate_kmps:.4f}'

        # Write to the file
        with open(file_path, 'w') as file:
            file.write(estimate_kmps_formatted)
        print(f'Successfully saved result to {file_path}')
    except Exception as e:
        print(f'Unexpected error while saving result to {file_path}: {e}')
        raise
# End of save_result()

"""
Calculate the ISS speed by taking a second photo and comparing positions.

Parameters:
    iss           : ISS object from astro_pi_orbit
    time_scale    : Skyfield timescale object
    cam           : Camera object for taking photos
    image_filename: Filename for the second photo
    last_time     : Datetime of the first measurement
    last_position : ISS position at last_time

Returns:
    speed_kmps    : curent speed in km/s
    time          : datetime of the second photo
    position      : ISS position at the time of the second photo
"""
def calculate_speed(iss, time_scale, cam, image_filename, last_time, last_position):
    cam.take_photo(image_filename)
    time = get_time(image_filename)
    moment = time_scale.from_datetime(time)
    position = iss.at(moment)
    
    time_difference = (time - last_time).total_seconds()
    diff = position - last_position
    distance_km = diff.distance().km
    speed = distance_km / time_difference

    return speed, time, position
# End of calculate_speed()

"""
Collect all sensor data from the Sense HAT and optional ISS position.

Parameters:
    sense        : SenseHat object
    last_position: ISS position for data collection

Returns:
    sense_data: All sensor readings including temperature, pressure, humidity, color,
                orientation, magnetic field, acceleration, gyro data, datetime, and ISS position
"""
def get_sense_data(sense, last_position):
    sense_data = []

    # Get environmental data
    sense_data.append(sense.get_temperature())
    sense_data.append(sense.get_pressure())
    sense_data.append(sense.get_humidity())

    # Get colour sensor data (version 2 Sense HAT only)
    red, green, blue, clear = sense.colour.colour
    sense_data.append(red)
    sense_data.append(green)
    sense_data.append(blue)
    sense_data.append(clear)

    # Get orientation data
    orientation = sense.get_orientation()
    sense_data.append(orientation['yaw'])
    sense_data.append(orientation['pitch'])
    sense_data.append(orientation['roll'])

    # Get compass data
    mag = sense.get_compass_raw()
    sense_data.append(mag['x'])
    sense_data.append(mag['y'])
    sense_data.append(mag['z'])
    
    # Get accelerometer data
    acc = sense.get_accelerometer_raw()
    sense_data.append(acc['x'])
    sense_data.append(acc['y'])
    sense_data.append(acc['z'])
    #Get gyroscope data
    gyro = sense.get_gyroscope_raw()
    sense_data.append(gyro['x'])
    sense_data.append(gyro['y'])
    sense_data.append(gyro['z'])

    # Get the date and time
    sense_data.append(datetime.now())
    
    # Get ISS position data
    lat, lon, alt_km = get_iss_position_data(last_position)
    sense_data.append(lat)
    sense_data.append(lon)
    sense_data.append(alt_km)

    return sense_data
# End of get_sense_data()

"""
Main program that runs ISS speed calculations and sensor data collection.
Takes periodic photos to calculate ISS speed, collects Sense HAT sensor data,
and saves results to CSV and output files.
"""
def main():
    time_delta = 10 #minutes
    file_path = 'result.txt'    # Replace with your desired file path

    cam = Camera()

    time_scale = load.timescale()
    iss = ISS()
    
    sense = SenseHat()
    sense.color.gain = 60
    sense.color.integration_cycles = 64

    average_ISS_speed = 0
    step_count        = 0
    max_loop_time     = 0.0

    image_index = 1
    image_filename = f'Photo{image_index}.jpg'
    
    cam.take_photo(image_filename)
    last_time = get_time(image_filename)
    moment_1 = time_scale.from_datetime(last_time)
    last_position = iss.at(moment_1)

    f = open('data.csv', 'w', newline='')
    data_writer = writer(f)
    data_writer.writerow(['temp', 'pres', 'hum',
                            'red', 'green', 'blue', 'clear', #only for Sense HAT version 2
                            'yaw', 'pitch', 'roll',
                            'mag_x', 'mag_y', 'mag_z',
                            'acc_x', 'acc_y', 'acc_z',
                            'gyro_x', 'gyro_y', 'gyro_z',
                            'datetime', 'iss_latitude', 'iss_longitude', 'iss_altitude_km',
                            'speed'])

    # Create a variable to store the current time
    # (these will be almost the same at the start)
    # Run a loop for 10 minute
    now_time = datetime.now()
    while ((now_time - start_time).total_seconds() < (time_delta * 60 - max_loop_time)):
        loop_start = datetime.now()

        image_index += 1
        image_filename = f'Photo{image_index}.jpg'
        ISS_speed, last_time, last_position = calculate_speed(iss, time_scale, cam, image_filename, last_time, last_position)

        average_ISS_speed = (step_count * average_ISS_speed + ISS_speed) / (step_count + 1)
        print(f'The calculated speed of the ISS on step {step_count + 1} is {ISS_speed}, average speed is {average_ISS_speed:.4f}')
        step_count += 1

        # Remove previous images to save space, but keep every 8th image (based on the real test)
        if (image_index % 8) > 0:
            try:
                if os.path.exists(image_filename):
                    os.remove(image_filename)
            except OSError as e:
                print(f'Warning: Could not delete image {image_filename}: {e}')

        try:
            data = get_sense_data(sense, last_position)
            data.append(ISS_speed)
            data_writer.writerow(data)
        except Exception as e:
            print(f'Unexpected error while collecting sensor data: {e}')

        # Update the current time
        now_time  = datetime.now()
        loop_time = (now_time - loop_start).total_seconds()
        if loop_time > max_loop_time:
            max_loop_time = loop_time
    # End of loop

    save_result(average_ISS_speed, file_path)
    print(f'\nResult is written to {file_path}')
    
    print(f'\nProgram was running for {now_time - start_time}')
# End of main()
    

main()