from datetime import datetime, timedelta
start_time = datetime.now()
from exif import Image
import cv2
import math
from time import sleep
from picamzero import Camera
from typing import Tuple
from skyfield.api import Topos, load, wgs84

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
    
def get_iss_altitude_meters(observation_time: datetime = None) -> float:
    """
    Get the current altitude of the ISS in meters using Skyfield's API.
    
    This method fetches the real-time ISS altitude above Earth's surface
    using official Two-Line Element (TLE) data from Celestrak.
    
    Args:
        observation_time (datetime): Time for altitude calculation (default: now)
    
    Returns:
        float: ISS altitude above Earth's surface in meters
    
    Raises:
        Exception: If unable to download TLE data or calculate position
    
    Example:
        altitude_m = get_iss_altitude_meters()
        altitude_km = altitude_m / 1000
        print(f"ISS altitude: {altitude_km:.2f} km ({altitude_m:.2f} m)")
        
        # Get altitude at a specific time
        from datetime import datetime, timedelta
        future_time = datetime.now() + timedelta(hours=2)
        alt_m = get_iss_altitude_meters(observation_time=future_time)
    """
    try:
        # Load ephemeris and ISS data
        ts = load.timescale()
        eph = load('de421.bsp')
        
        # Load ISS satellite TLE data from Celestrak
        satellites = load.tle_file('https://celestrak.com/NORAD/elements/stations.txt')
        by_name = {sat.name: sat for sat in satellites}
        iss = by_name['ISS (ZARYA)']
        
        # Set observation time (default to current time)
        if observation_time is None:
            t = ts.now()
        else:
            t = ts.from_datetime(observation_time)
        
        # Calculate ISS position relative to Earth's center
        earth = eph['earth']
        position_vector = earth.at(t).observe(iss)
        
        # Convert to WGS84 geographic coordinates
        location = wgs84.latlong_of(position_vector)
        
        # Extract altitude in kilometers and convert to meters
        altitude_km = location[2].km
        altitude_meters = altitude_km * 1000.0
        
        return altitude_meters
    
    except Exception as e:
        print(f"Error fetching ISS altitude: {e}")
        print("Using fallback ISS altitude: 408,000 meters")
        # Fallback to typical ISS altitude in meters
        return 408000.0
    
def calculate_gsd(altitude: float = None, focal_length: float = 11.8, pixel_size: float = 1.55) -> float:
    if altitude is None:
        altitude = get_iss_altitude_meters()  # Call it inside the function
    """
    Calculate Ground Sample Distance (GSD) for aerial/satellite imagery.
    
    GSD represents the physical distance (in meters) on the ground that corresponds
    to one pixel in the image. It's essential for determining the scale of features
    detected in satellite imagery.
    
    Args:
        altitude (float): Altitude of the camera/satellite in meters
        focal_length (float): Focal length of the camera in millimeters
        pixel_size (float): Size of each pixel in micrometers
    
    Returns:
        float: Ground Sample Distance in meters per pixel
    
    Formula: GSD = (altitude * pixel_size) / focal_length
    
    Example for ISS:
        - ISS altitude: ~408,000 meters
        - Typical focal length: 35mm
        - Typical pixel size: 3.45 micrometers (for Raspberry Pi HQ Camera)
        GSD ≈ (408000 * 3.45e-6) / 35 ≈ 0.404 meters per pixel
    """
    if focal_length <= 0:
        raise ValueError("Focal length must be greater than 0")
    if pixel_size <= 0:
        raise ValueError("Pixel size must be greater than 0")
    if altitude < 0:
        raise ValueError("Altitude cannot be negative")
    
    # Convert pixel_size from micrometers to millimeters if needed
    # pixel_size should be in the same units as focal_length for calculation
    gsd = (altitude * pixel_size) / focal_length
    
    return gsd

def calculate_speed_in_kmps(feature_distance, GSD, time_difference):
    distance = feature_distance * GSD / 100000
    #distance = feature_distance * 4414.859 / 100000
    speed = distance / time_difference
    return speed

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
    
    print(image_1, image_2)
    
    cam = Camera()
    cam.take_photo(image_1)
    sleep(1)
    cam.take_photo(image_2)
    
    time_difference = get_time_difference(image_1, image_2) # Get time difference between images
    image_1_cv, image_2_cv = convert_to_cv(image_1, image_2) # Create OpenCV image objects
    keypoints_1, keypoints_2, descriptors_1, descriptors_2 = calculate_features(image_1_cv, image_2_cv, 1000) # Get keypoints and descriptors
    matches = calculate_matches(descriptors_1, descriptors_2) # Match descriptors
    #display_matches(image_1_cv, keypoints_1, image_2_cv, keypoints_2, matches) # Display matches
    coordinates_1, coordinates_2 = find_matching_coordinates(keypoints_1, keypoints_2, matches)
    average_feature_distance = calculate_mean_distance(coordinates_1, coordinates_2)
    gsd = calculate_gsd()
    speed = calculate_speed_in_kmps(average_feature_distance, 12648, time_difference)
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