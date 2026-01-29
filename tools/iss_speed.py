from datetime import datetime, timedelta, UTC
start_time = datetime.now()
from exif import Image
import cv2
#import math
from time import sleep
from astro_pi_orbit import ISS
from picamzero import Camera
from skyfield.api import load

sleep_time = 1 #sec

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
'''
def convert_to_cv(image_1, image_2):
    image_1_cv = cv2.imread(image_1, 0)
    image_2_cv = cv2.imread(image_2, 0)
    return image_1_cv, image_2_cv

def calculate_features(image_1_cv, image_2_cv, feature_number):
    orb = cv2.ORB_create(nfeatures = feature_number)
    keypoints_1, descriptors_1 = orb.detectAndCompute(image_1_cv, None)
    keypoints_2, descriptors_2 = orb.detectAndCompute(image_2_cv, None)
    return keypoints_1, keypoints_2, descriptors_1, descriptors_2


def calculate_matches(descriptors_1, descriptors_2):
    brute_force = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = brute_force.match(descriptors_1, descriptors_2)
    matches = sorted(matches, key=lambda x: x.distance)
    return matches

def display_matches(image_1_cv, keypoints_1, image_2_cv, keypoints_2, matches):
    match_img = cv2.drawMatches(image_1_cv, keypoints_1, image_2_cv, keypoints_2, matches[:100], None)
    resize = cv2.resize(match_img, (1600,600), interpolation = cv2.INTER_AREA)
    cv2.imshow('matches', resize)
    cv2.waitKey(0)
    cv2.destroyWindow('matches')
  
def find_matching_coordinates(keypoints_1, keypoints_2, matches):
    coordinates_1 = []
    coordinates_2 = []
    for match in matches:
        image_1_idx = match.queryIdx
        image_2_idx = match.trainIdx
        (x1,y1) = keypoints_1[image_1_idx].pt
        (x2,y2) = keypoints_2[image_2_idx].pt
        coordinates_1.append((x1,y1))
        coordinates_2.append((x2,y2))
    return coordinates_1, coordinates_2

def calculate_mean_distance(coordinates_1, coordinates_2):
    all_distances = 0
    merged_coordinates = list(zip(coordinates_1, coordinates_2))
    for coordinate in merged_coordinates:
        x_difference = coordinate[0][0] - coordinate[1][0]
        y_difference = coordinate[0][1] - coordinate[1][1]
        distance = math.hypot(x_difference, y_difference)
        all_distances = all_distances + distance
        return all_distances / len(merged_coordinates)

    
def calculate_speed_in_kmps(feature_distance, GSD, time_difference):
    distance = feature_distance * GSD / 100000
    #distance = feature_distance * 4414.859 / 100000
    speed = distance / time_difference
    return speed
'''
def save_result(estimate_kmps, file_path):
    # Format the estimate_kmps to have a precision
    # of 5 significant figures
    estimate_kmps_formatted = f'{estimate_kmps:.4f}'
    
    # Create a string to write to the file
    output_string = estimate_kmps_formatted

    # Write to the file
    with open(file_path, 'w') as file:
        file.write(output_string)

def calculate_speed():
    image_1 = 'Photo1.jpg'
    image_2 = 'Photo2.jpg'
    time_scale = load.timescale()
    iss = ISS()
    
    print(image_1, image_2)
    
    cam = Camera()
    cam.take_photo(image_1)
    sleep(1)
    cam.take_photo(image_2)
    
    time_difference = get_time_difference(image_1, image_2) # Get time difference between images
    print(f'Time difference between images: {time_difference} seconds')
    
    time_1 = get_time(image_1).replace(tzinfo=UTC)
    print(f'Time 1: {time_1}')
    moment_1 = time_scale.from_datetime(time_1)
    position_1 = iss.at(moment_1)

    sleep(sleep_time)

    time_2 = get_time(image_2).replace(tzinfo=UTC)
    print(f'Time 2: {time_2}')
    moment_2 = time_scale.from_datetime(time_2)
    position_2 = iss.at(moment_2)

    diff = position_2 - position_1
    distance_km = diff.distance().km
    speed = distance_km / time_difference

    '''
    image_1_cv, image_2_cv = convert_to_cv(image_1, image_2) # Create OpenCV image objects
    keypoints_1, keypoints_2, descriptors_1, descriptors_2 = calculate_features(image_1_cv, image_2_cv, 1000) # Get keypoints and descriptors
    matches = calculate_matches(descriptors_1, descriptors_2) # Match descriptors
    #display_matches(image_1_cv, keypoints_1, image_2_cv, keypoints_2, matches) # Display matches
    coordinates_1, coordinates_2 = find_matching_coordinates(keypoints_1, keypoints_2, matches)
    average_feature_distance = calculate_mean_distance(coordinates_1, coordinates_2)
    speed = calculate_speed_in_kmps(average_feature_distance, 12648, time_difference)
    '''

    #print(speed)
    return speed

def main():
    time_delta = 0.5 #minutes
    file_path = 'result.txt'    # Replace with your desired file path
    
    # Create a variable to store the current time
    # (these will be almost the same at the start)
    # Run a loop for 1 minute
    average_ISS_speed = 0
    count   = 0
    max_loop_time = 0.0
    
    now_time = datetime.now()
    while ((now_time - start_time).total_seconds() < (time_delta * 60 - max_loop_time)):
        loop_start = datetime.now()
        
        ISS_speed = calculate_speed()
        average_ISS_speed = (count * average_ISS_speed + ISS_speed) / (count + 1)
        print(f'The calculated speed of the ISS on step {count} is {ISS_speed}, average speed is {average_ISS_speed:.4f}')
        count += 1
        
        # Update the current time
        now_time  = datetime.now()
        loop_time = (now_time - loop_start).total_seconds()
        if loop_time > max_loop_time:
            max_loop_time = loop_time
        #print(loop_time, max_loop_time) 

    save_result(average_ISS_speed, file_path)  
    print('Result is written to', file_path)
    
    print(f'Program was running for {now_time - start_time}')
    # Out of the loop — stopping
    
    
main()