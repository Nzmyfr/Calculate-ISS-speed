from datetime import datetime, UTC
from sense_hat import SenseHat
from numpy import imag
start_time = datetime.now()
import os
from exif import Image
from astro_pi_orbit import ISS
from picamzero import Camera
from skyfield.api import load
from csv import writer

image_index = 1

def get_time(image):
    with open(image, 'rb') as image_file:
        img = Image(image_file)
        time_str = img.get("datetime_original")
        time = datetime.strptime(time_str, '%Y:%m:%d %H:%M:%S')
        return time.replace(tzinfo=UTC)

def save_result(estimate_kmps, file_path):
    # Format the estimate_kmps to have a precision
    # of 5 significant figures
    estimate_kmps_formatted = f'{estimate_kmps:.4f}'
    
    # Create a string to write to the file
    output_string = estimate_kmps_formatted

    # Write to the file
    with open(file_path, 'w') as file:
        file.write(output_string)

def calculate_speed(iss, time_scale, cam, time_1, position_1):
    global image_index

    image_index += 1
    image_filename = f'Photo{image_index}.jpg'
    cam.take_photo(image_filename)
    time_2 = get_time(image_filename)
    moment_2 = time_scale.from_datetime(time_2)
    position_2 = iss.at(moment_2)
    
    time_difference = (time_2 - time_1).total_seconds()
    diff = position_2 - position_1
    distance_km = diff.distance().km
    speed = distance_km / time_difference

    return speed, time_2, position_2

def get_sense_data(sense):
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
    sense_data.append(orientation["yaw"])
    sense_data.append(orientation["pitch"])
    sense_data.append(orientation["roll"])
    # Get compass data
    mag = sense.get_compass_raw()
    sense_data.append(mag["x"])
    sense_data.append(mag["y"])
    sense_data.append(mag["z"])
    # Get accelerometer data
    acc = sense.get_accelerometer_raw()
    sense_data.append(acc["x"])
    sense_data.append(acc["y"])
    sense_data.append(acc["z"])
    #Get gyroscope data
    gyro = sense.get_gyroscope_raw()
    sense_data.append(gyro["x"])
    sense_data.append(gyro["y"])
    sense_data.append(gyro["z"])

    # Get the date and time
    sense_data.append(datetime.now())

    return sense_data

def main():
    time_scale = load.timescale()
    iss = ISS()

    cam = Camera()
    time_delta = 0.5 #minutes
    file_path = 'result.txt'    # Replace with your desired file path
    
    sense = SenseHat()
    sense.color.gain = 60
    sense.color.integration_cycles = 64

    # Create a variable to store the current time
    # (these will be almost the same at the start)
    # Run a loop for 1 minute
    average_ISS_speed = 0
    step_count        = 0
    max_loop_time     = 0.0

    image_1 = f'Photo{image_index}.jpg'
    cam.take_photo(image_1)
    last_time = get_time(image_1)
    moment_1 = time_scale.from_datetime(last_time)
    last_postion = iss.at(moment_1)
    with open('data.csv', 'w', newline='') as f: 
        data_writer = writer(f)
        data_writer.writerow(['temp', 'pres', 'hum',
                              'red', 'green', 'blue', 'clear', #only for Sense HAT version 2
                              'yaw', 'pitch', 'roll',
                              'mag_x', 'mag_y', 'mag_z',
                              'acc_x', 'acc_y', 'acc_z',
                              'gyro_x', 'gyro_y', 'gyro_z',
                              'datetime'])

        now_time = datetime.now()
        while ((now_time - start_time).total_seconds() < (time_delta * 60 - max_loop_time)):
            loop_start = datetime.now()
            print(f'\n--- Step {step_count + 1} ---')
            ISS_speed, last_time, last_postion = calculate_speed(iss, time_scale, cam, last_time, last_postion)
            average_ISS_speed = (step_count * average_ISS_speed + ISS_speed) / (step_count + 1)
            print(f'The calculated speed of the ISS on step {step_count} is {ISS_speed}, average speed is {average_ISS_speed:.4f}')
            step_count += 1
            if (image_index % 6) > 0:
                file_to_delete = f'Photo{image_index}.jpg'
                if os.path.exists(file_to_delete):
                    os.remove(file_to_delete)

            try:
                data = get_sense_data(sense)
                print(data)
                data_writer.writerow(data)
            except IOError as e:
                print(f"Error opening or writing to 'data.csv': {e}")
            except Exception as e:
                print(f"Unexpected error while collecting sensor data: {e}")

            # Update the current time
            now_time  = datetime.now()
            loop_time = (now_time - loop_start).total_seconds()
            if loop_time > max_loop_time:
                max_loop_time = loop_time
            print(loop_time)
        save_result(average_ISS_speed, file_path)
        print('\nResult is written to', file_path)
        
        print(f'\nProgram was running for {now_time - start_time}')
        # Out of the loop — stopping
        
    
main()