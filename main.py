from datetime import datetime, UTC
start_time = datetime.now()

from exif import Image
from astro_pi_orbit import ISS
from picamzero import Camera
from skyfield.api import load

image_1 = 'Photo1.jpg'
image_2 = 'Photo2.jpg'

def get_time(image):
    with open(image, 'rb') as image_file:
        img = Image(image_file)
        time_str = img.get("datetime_original")
        time = datetime.strptime(time_str, '%Y:%m:%d %H:%M:%S')
        return time
   
def get_time_difference(image_1, image_2):
    time_1 = get_time(image_1)
    time_2 = get_time(image_2)
    time_difference = time_2 - time_1
    return time_difference.seconds

def save_result(estimate_kmps, file_path):
    # Format the estimate_kmps to have a precision
    # of 5 significant figures
    estimate_kmps_formatted = f'{estimate_kmps:.4f}'
    
    # Create a string to write to the file
    output_string = estimate_kmps_formatted

    # Write to the file
    with open(file_path, 'w') as file:
        file.write(output_string)

def calculate_speed(iss, time_scale, cam):
    print()
    
    cam.take_photo(image_1)
    cam.take_photo(image_2)
    
    time_1 = get_time(image_1).replace(tzinfo=UTC)
    moment_1 = time_scale.from_datetime(time_1)
    position_1 = iss.at(moment_1)

    time_2 = get_time(image_2).replace(tzinfo=UTC)
    moment_2 = time_scale.from_datetime(time_2)
    position_2 = iss.at(moment_2)
    
    time_difference = get_time_difference(image_1, image_2) # Get time difference between images
    print(f'Time difference between images: {time_difference} seconds')

    diff = position_2 - position_1
    distance_km = diff.distance().km
    speed = distance_km / time_difference

    return speed

def main():
    time_scale = load.timescale()
    iss = ISS()

    cam = Camera()
    time_delta = 0.5 #minutes
    file_path = 'result.txt'    # Replace with your desired file path
    
    # Create a variable to store the current time
    # (these will be almost the same at the start)
    # Run a loop for 1 minute
    average_ISS_speed = 0
    step_count        = 0
    max_loop_time     = 0.0
    
    now_time = datetime.now()
    while ((now_time - start_time).total_seconds() < (time_delta * 60 - max_loop_time)):
        loop_start = datetime.now()
        
        ISS_speed = calculate_speed(iss, time_scale, cam)
        average_ISS_speed = (step_count * average_ISS_speed + ISS_speed) / (step_count + 1)
        print(f'The calculated speed of the ISS on step {step_count} is {ISS_speed}, average speed is {average_ISS_speed:.4f}')
        step_count += 1
        
        # Update the current time
        now_time  = datetime.now()
        loop_time = (now_time - loop_start).total_seconds()
        if loop_time > max_loop_time:
            max_loop_time = loop_time
        print(loop_time, max_loop_time) 

    save_result(average_ISS_speed, file_path)
    print('\nResult is written to', file_path)
    
    print(f'\nProgram was running for {now_time - start_time}')
    # Out of the loop — stopping
    
    
main()