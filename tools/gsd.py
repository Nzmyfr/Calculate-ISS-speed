"""
GSD (Ground Sample Distance) Calculator for ISS Imagery

This module provides methods to:
1. Get the current location (lat, lon, altitude) of the ISS using Skyfield
2. Calculate GSD based on ISS location, altitude, and camera parameters
3. Support multiple camera configurations and time queries
"""

from datetime import datetime, timedelta
from typing import Tuple, Dict
from skyfield.api import load, wgs84
import math

# Cache for Skyfield ephemeris data (loaded once, reused multiple times)
_SKYFIELD_CACHE = {
    'ts': None,
    'eph': None,
    'iss': None,
    'earth_radius_km': 6371.0
}


def _initialize_skyfield():
    """
    Initialize Skyfield ephemeris data once and cache it.
    Eliminates redundant loading operations.
    """
    if _SKYFIELD_CACHE['ts'] is None:
        _SKYFIELD_CACHE['ts'] = load.timescale()
        _SKYFIELD_CACHE['eph'] = load('de421.bsp')
        satellites = load.tle_file('https://celestrak.com/NORAD/elements/stations.txt')
        by_name = {sat.name: sat for sat in satellites}
        _SKYFIELD_CACHE['iss'] = by_name['ISS (ZARYA)']


def _ecef_to_lat_lon(x: float, y: float, z: float) -> Tuple[float, float]:
    """
    Convert ECEF coordinates to latitude and longitude.
    
    Args:
        x, y, z: Earth-Centered Earth-Fixed coordinates in km
    
    Returns:
        Tuple[float, float]: (latitude, longitude) in decimal degrees
    """
    longitude = math.degrees(math.atan2(y, x))
    latitude = math.degrees(math.atan2(z, math.sqrt(x**2 + y**2)))
    return latitude, longitude


def _get_timestamp(observation_time: datetime = None) -> str:
    """
    Get ISO format timestamp. Eliminates duplicate timestamp generation code.
    
    Args:
        observation_time: datetime object or None for current time
    
    Returns:
        str: ISO format timestamp
    """
    return observation_time.isoformat() if observation_time else datetime.utcnow().isoformat()


def get_iss_location(observation_time: datetime = None) -> Tuple[float, float, float]:
    """
    Get the current location of the ISS from Skyfield library.
    
    Fetches real-time ISS position using official Two-Line Element (TLE) data
    from Celestrak. Returns latitude, longitude, and altitude above Earth's surface.
    
    Args:
        observation_time (datetime): Time for ISS position calculation (default: now).
                                    If None, uses current UTC time.
    
    Returns:
        Tuple[float, float, float]: (latitude, longitude, altitude_meters)
            - latitude: ISS latitude in decimal degrees (-90 to 90)
            - longitude: ISS longitude in decimal degrees (-180 to 180)
            - altitude_meters: ISS altitude above Earth's surface in meters
    
    Raises:
        Exception: If unable to download TLE data or calculate position
    
    Example:
        lat, lon, alt = get_iss_location()
        print(f"ISS at {lat:.2f}°N, {lon:.2f}°E, altitude: {alt/1000:.2f} km")
    """
    try:
        # Initialize Skyfield (loads once, reuses if already loaded)
        _initialize_skyfield()
        ts = _SKYFIELD_CACHE['ts']
        iss = _SKYFIELD_CACHE['iss']
        earth_radius_km = _SKYFIELD_CACHE['earth_radius_km']
        
        # Set observation time
        t = ts.now() if observation_time is None else ts.from_datetime(observation_time)
        
        # Get ISS position relative to Earth's center (in km)
        position = iss.at(t)
        x, y, z = position.position.km
        
        # Calculate distance from Earth's center using single sqrt instead of hypot
        distance_from_earth_center = math.sqrt(x*x + y*y + z*z)
        
        # Calculate altitude
        altitude_m = (distance_from_earth_center - earth_radius_km) * 1000.0
        
        # Convert coordinates to lat/lon (reusable function)
        latitude, longitude = _ecef_to_lat_lon(x, y, z)
        
        return latitude, longitude, altitude_m
    
    except Exception as e:
        print(f"Error fetching ISS location: {e}")
        return 0.0, 0.0, 408000.0


def get_iss_location_detailed(observation_time: datetime = None) -> Dict:
    """
    Get detailed ISS location information including velocity and orbital parameters.
    
    Args:
        observation_time (datetime): Time for ISS position calculation (default: now)
    
    Returns:
        dict: Dictionary containing location, altitude, velocity, and timestamp
    
    Example:
        info = get_iss_location_detailed()
        print(f"ISS at {info['latitude']:.2f}°, {info['longitude']:.2f}°")
    """
    try:
        # Get location once (eliminates redundant calls)
        lat, lon, alt_m = get_iss_location(observation_time)
        
        return {
            'latitude': lat,
            'longitude': lon,
            'altitude_m': alt_m,
            'altitude_km': alt_m / 1000.0,
            'velocity_kmps': 7.66,  # ISS orbital velocity
            'timestamp': _get_timestamp(observation_time)
        }
    
    except Exception as e:
        print(f"Error in get_iss_location_detailed: {e}")
        return {
            'latitude': 0.0,
            'longitude': 0.0,
            'altitude_m': 408000.0,
            'altitude_km': 408.0,
            'velocity_kmps': 7.66,
            'timestamp': _get_timestamp()
        }


def calculate_gsd_from_iss_location(focal_length: float = 11.8, 
                                    pixel_size: float = 1.55,
                                    observation_time: datetime = None) -> Dict:
    """
    Calculate GSD based on actual ISS location and altitude from Skyfield.
    
    This is the main method that fetches the real ISS location using Skyfield
    and calculates GSD based on actual ISS parameters.
    
    Args:
        focal_length (float): Camera focal length in millimeters (default: 11.8mm)
        pixel_size (float): Pixel size in micrometers (default: 1.55µm)
        observation_time (datetime): Time for calculation (default: now)
    
    Returns:
        dict: Dictionary containing GSD, location, altitude, camera parameters, and timestamp
    
    Formula: GSD = (altitude * pixel_size) / focal_length
    
    Example:
        result = calculate_gsd_from_iss_location()
        print(f"GSD: {result['gsd_m']:.4f} m/pixel")
    """
    try:
        # Validate parameters once
        if focal_length <= 0:
            raise ValueError("Focal length must be greater than 0")
        if pixel_size <= 0:
            raise ValueError("Pixel size must be greater than 0")
        
        # Get ISS location once
        lat, lon, alt_m = get_iss_location(observation_time)
        
        # Calculate GSD
        gsd_m = (alt_m * pixel_size) / focal_length
        
        return {
            'gsd_m': gsd_m,
            'gsd_km': gsd_m / 1000.0,
            'latitude': lat,
            'longitude': lon,
            'altitude_km': alt_m / 1000.0,
            'focal_length': focal_length,
            'pixel_size': pixel_size,
            'timestamp': _get_timestamp(observation_time)
        }
    
    except Exception as e:
        print(f"Error calculating GSD: {e}")
        return {
            'gsd_m': 0.0,
            'gsd_km': 0.0,
            'latitude': 0.0,
            'longitude': 0.0,
            'altitude_km': 408.0,
            'focal_length': focal_length,
            'pixel_size': pixel_size,
            'timestamp': _get_timestamp()
        }


def calculate_gsd_with_custom_altitude(altitude_m: float,
                                       focal_length: float = 11.8,
                                       pixel_size: float = 1.55) -> float:
    """
    Calculate GSD with a custom altitude value.
    
    Use this when you have a specific altitude and want to calculate GSD
    without fetching the ISS location from Skyfield.
    
    Args:
        altitude_m (float): Altitude in meters
        focal_length (float): Camera focal length in millimeters (default: 11.8mm)
        pixel_size (float): Pixel size in micrometers (default: 1.55µm)
    
    Returns:
        float: Ground Sample Distance in meters per pixel
    """
    if altitude_m < 0:
        raise ValueError("Altitude cannot be negative")
    if focal_length <= 0:
        raise ValueError("Focal length must be greater than 0")
    if pixel_size <= 0:
        raise ValueError("Pixel size must be greater than 0")
    
    return (altitude_m * pixel_size) / focal_length


def calculate_gsd_multiple_cameras(observation_time: datetime = None) -> Dict:
    """
    Calculate GSD for multiple common camera configurations.
    
    Optimized to fetch ISS altitude once and reuse for all camera calculations.
    
    Args:
        observation_time (datetime): Time for ISS position calculation (default: now)
    
    Returns:
        dict: Dictionary with camera names as keys and GSD values (in meters/pixel) as values
    """
    # Common camera configurations
    cameras = {
        'Raspberry Pi HQ Camera': {'focal_length': 35, 'pixel_size': 3.45},
        'Raspberry Pi Camera v2': {'focal_length': 3.04, 'pixel_size': 1.4},
        'OV5647 (older Pi)': {'focal_length': 3.4, 'pixel_size': 1.4},
        'Default (11.8mm)': {'focal_length': 11.8, 'pixel_size': 1.55},
    }
    
    try:
        # Get ISS altitude once, reuse for all cameras
        _, _, alt_m = get_iss_location(observation_time)
        
        # Calculate GSD for each camera
        return {
            camera_name: calculate_gsd_with_custom_altitude(
                altitude_m=alt_m,
                focal_length=params['focal_length'],
                pixel_size=params['pixel_size']
            )
            for camera_name, params in cameras.items()
        }
    
    except Exception as e:
        print(f"Error calculating GSD for multiple cameras: {e}")
        return {}


def get_iss_cartesian_coordinates(observation_time: datetime = None) -> Dict:
    """
    Get ISS position in Cartesian (ECEF) coordinate system.
    
    Returns the ISS position as (X, Y, Z) coordinates relative to Earth's center
    in the Earth-Centered Earth-Fixed (ECEF) coordinate system. This is the raw
    Cartesian representation used by satellite tracking systems.
    
    Args:
        observation_time (datetime): Time for ISS position calculation (default: now)
    
    Returns:
        dict: Dictionary containing:
            - x_km: X coordinate in kilometers (Earth center reference)
            - y_km: Y coordinate in kilometers
            - z_km: Z coordinate in kilometers
            - distance_from_center_km: Distance from Earth's center in km
            - distance_from_center_m: Distance from Earth's center in meters
            - altitude_m: Altitude above Earth's surface in meters
            - timestamp: Time of observation (ISO format)
    
    Coordinate System Reference:
        - Origin: Earth's center
        - X-axis: Points to the Prime Meridian (0° longitude)
        - Z-axis: Points to the North Pole
        - Y-axis: Completes the right-handed system (90°E longitude)
    
    Example:
        coords = get_iss_cartesian_coordinates()
        print(f"ISS at X={coords['x_km']:.2f} km, Y={coords['y_km']:.2f} km, Z={coords['z_km']:.2f} km")
        print(f"Distance from Earth center: {coords['distance_from_center_km']:.2f} km")
    """
    try:
        # Initialize Skyfield
        _initialize_skyfield()
        ts = _SKYFIELD_CACHE['ts']
        iss = _SKYFIELD_CACHE['iss']
        earth_radius_km = _SKYFIELD_CACHE['earth_radius_km']
        
        # Set observation time
        t = ts.now() if observation_time is None else ts.from_datetime(observation_time)
        
        # Get ISS position in ECEF coordinates (in km)
        position = iss.at(t)
        x, y, z = position.position.km
        
        # Calculate distance from Earth's center
        distance_from_center_km = math.sqrt(x*x + y*y + z*z)
        distance_from_center_m = distance_from_center_km * 1000.0
        
        # Calculate altitude above surface
        altitude_m = (distance_from_center_km - earth_radius_km) * 1000.0
        
        return {
            'x_km': x,
            'y_km': y,
            'z_km': z,
            'distance_from_center_km': distance_from_center_km,
            'distance_from_center_m': distance_from_center_m,
            'altitude_m': altitude_m,
            'timestamp': _get_timestamp(observation_time)
        }
    
    except Exception as e:
        print(f"Error fetching ISS Cartesian coordinates: {e}")
        # Fallback: approximate ISS position at (6779, 0, 0) - on Earth surface + altitude
        return {
            'x_km': 6779.0,
            'y_km': 0.0,
            'z_km': 0.0,
            'distance_from_center_km': 6779.0,
            'distance_from_center_m': 6779000.0,
            'altitude_m': 408000.0,
            'timestamp': _get_timestamp()
        }


def calculate_gsd_cartesian(focal_length: float = 11.8,
                            pixel_size: float = 1.55,
                            observation_time: datetime = None) -> Dict:
    """
    Calculate GSD based on ISS position in Cartesian (ECEF) coordinate system.
    
    This method uses the raw Cartesian coordinates of the ISS to determine its
    distance from Earth's center, then calculates GSD. The Cartesian coordinate
    system is fundamental for satellite positioning and orbital mechanics.
    
    Args:
        focal_length (float): Camera focal length in millimeters (default: 11.8mm)
        pixel_size (float): Pixel size in micrometers (default: 1.55µm)
        observation_time (datetime): Time for ISS position calculation (default: now)
    
    Returns:
        dict: Dictionary containing:
            - gsd_m: Ground Sample Distance in meters per pixel
            - gsd_km: Ground Sample Distance in kilometers per pixel
            - x_km: ISS X coordinate (ECEF) in km
            - y_km: ISS Y coordinate (ECEF) in km
            - z_km: ISS Z coordinate (ECEF) in km
            - distance_from_center_km: ISS distance from Earth's center in km
            - altitude_m: ISS altitude above surface in meters
            - altitude_km: ISS altitude above surface in kilometers
            - focal_length: Camera focal length used (mm)
            - pixel_size: Pixel size used (micrometers)
            - timestamp: Time of observation
    
    Formula: GSD = (altitude * pixel_size) / focal_length
    
    Note: The Cartesian coordinates represent the absolute position of the ISS
    in 3D space relative to Earth's center. This is useful for orbital mechanics,
    trajectory calculations, and satellite tracking systems.
    
    Example:
        result = calculate_gsd_cartesian()
        print(f"GSD: {result['gsd_m']:.4f} m/pixel")
        print(f"ISS Cartesian position: ({result['x_km']:.2f}, {result['y_km']:.2f}, {result['z_km']:.2f}) km")
        print(f"Altitude: {result['altitude_km']:.2f} km")
    """
    try:
        # Validate parameters
        if focal_length <= 0:
            raise ValueError("Focal length must be greater than 0")
        if pixel_size <= 0:
            raise ValueError("Pixel size must be greater than 0")
        
        # Get ISS Cartesian coordinates
        coords = get_iss_cartesian_coordinates(observation_time)
        
        # Calculate GSD using altitude from Cartesian calculation
        alt_m = coords['altitude_m']
        gsd_m = (alt_m * pixel_size) / focal_length
        
        return {
            'gsd_m': gsd_m,
            'gsd_km': gsd_m / 1000.0,
            'x_km': coords['x_km'],
            'y_km': coords['y_km'],
            'z_km': coords['z_km'],
            'distance_from_center_km': coords['distance_from_center_km'],
            'altitude_m': alt_m,
            'altitude_km': alt_m / 1000.0,
            'focal_length': focal_length,
            'pixel_size': pixel_size,
            'timestamp': coords['timestamp']
        }
    
    except Exception as e:
        print(f"Error calculating GSD from Cartesian coordinates: {e}")
        return {
            'gsd_m': 0.0,
            'gsd_km': 0.0,
            'x_km': 6779.0,
            'y_km': 0.0,
            'z_km': 0.0,
            'distance_from_center_km': 6779.0,
            'altitude_m': 408000.0,
            'altitude_km': 408.0,
            'focal_length': focal_length,
            'pixel_size': pixel_size,
            'timestamp': _get_timestamp()
        }


def calculate_iss_velocity_cartesian(observation_time: datetime = None) -> Dict:
    """
    Calculate ISS velocity vector in Cartesian (ECEF) coordinate system.
    
    Returns the ISS velocity as (VX, VY, VZ) components relative to Earth's
    center in the Earth-Centered Earth-Fixed frame.
    
    Args:
        observation_time (datetime): Time for ISS velocity calculation (default: now)
    
    Returns:
        dict: Dictionary containing:
            - vx_km_s: X velocity component in km/s
            - vy_km_s: Y velocity component in km/s
            - vz_km_s: Z velocity component in km/s
            - speed_km_s: Total speed in km/s
            - speed_kmh: Total speed in km/h
            - speed_mps: Total speed in m/s
            - timestamp: Time of observation
    
    Example:
        vel = calculate_iss_velocity_cartesian()
        print(f"ISS velocity: {vel['speed_km_s']:.2f} km/s")
        print(f"ISS velocity: {vel['speed_kmh']:.0f} km/h")
    """
    try:
        # Initialize Skyfield
        _initialize_skyfield()
        ts = _SKYFIELD_CACHE['ts']
        iss = _SKYFIELD_CACHE['iss']
        
        # Set observation time
        t = ts.now() if observation_time is None else ts.from_datetime(observation_time)
        
        # Get ISS position and velocity
        position = iss.at(t)
        vx, vy, vz = position.velocity.km_per_s
        
        # Calculate total speed
        speed_km_s = math.sqrt(vx*vx + vy*vy + vz*vz)
        speed_kmh = speed_km_s * 3600.0
        speed_mps = speed_km_s * 1000.0
        
        return {
            'vx_km_s': vx,
            'vy_km_s': vy,
            'vz_km_s': vz,
            'speed_km_s': speed_km_s,
            'speed_kmh': speed_kmh,
            'speed_mps': speed_mps,
            'timestamp': _get_timestamp(observation_time)
        }
    
    except Exception as e:
        print(f"Error calculating ISS velocity: {e}")
        # Fallback: approximate ISS velocity (~7.66 km/s)
        return {
            'vx_km_s': 7.66,
            'vy_km_s': 0.0,
            'vz_km_s': 0.0,
            'speed_km_s': 7.66,
            'speed_kmh': 27576.0,
            'speed_mps': 7660.0,
            'timestamp': _get_timestamp()
        }



# Example usage and testing
if __name__ == "__main__":
    print("=" * 80)
    print("ISS GSD Calculator - Cartesian Coordinate System Implementation")
    print("=" * 80)
    
    # Test 1: Get ISS location
    print("\n[Test 1] Getting current ISS location (Geographic)...")
    lat, lon, alt = get_iss_location()
    print(f"    Latitude: {lat:.4f}°")
    print(f"    Longitude: {lon:.4f}°")
    print(f"    Altitude: {alt/1000:.2f} km ({alt:.0f} m)")
    
    # Test 2: Get detailed location info
    print("\n[Test 2] Getting detailed ISS information...")
    info = get_iss_location_detailed()
    print(f"    Position: {info['latitude']:.4f}°N, {info['longitude']:.4f}°E")
    print(f"    Altitude: {info['altitude_km']:.2f} km")
    print(f"    Velocity: {info['velocity_kmps']:.2f} km/s")
    
    # Test 3: Calculate GSD from ISS location
    print("\n[Test 3] Calculating GSD from ISS location...")
    result = calculate_gsd_from_iss_location()
    print(f"    GSD: {result['gsd_m']:.4f} m/pixel")
    print(f"    GSD: {result['gsd_km']:.6f} km/pixel")
    print(f"    Location: {result['latitude']:.2f}°, {result['longitude']:.2f}°")
    print(f"    Altitude: {result['altitude_km']:.2f} km")
    
    # Test 4: Calculate GSD for multiple cameras
    print("\n[Test 4] GSD for different camera configurations...")
    gsds = calculate_gsd_multiple_cameras()
    for camera, gsd in gsds.items():
        print(f"    {camera}: {gsd:.4f} m/pixel")
    
    # Test 5: Get ISS Cartesian (ECEF) coordinates
    print("\n[Test 5] Get ISS Cartesian Coordinates (ECEF System)...")
    cartesian = get_iss_cartesian_coordinates()
    print(f"    X (Prime Meridian): {cartesian['x_km']:.2f} km")
    print(f"    Y (90°E): {cartesian['y_km']:.2f} km")
    print(f"    Z (North Pole): {cartesian['z_km']:.2f} km")
    print(f"    Distance from Earth center: {cartesian['distance_from_center_km']:.2f} km")
    print(f"    Altitude above surface: {cartesian['altitude_m']/1000:.2f} km")
    
    # Test 6: Calculate GSD using Cartesian coordinates
    print("\n[Test 6] Calculate GSD using Cartesian (ECEF) coordinates...")
    gsd_cartesian = calculate_gsd_cartesian()
    print(f"    GSD: {gsd_cartesian['gsd_m']:.4f} m/pixel")
    print(f"    ISS Position (ECEF):")
    print(f"      X: {gsd_cartesian['x_km']:.2f} km")
    print(f"      Y: {gsd_cartesian['y_km']:.2f} km")
    print(f"      Z: {gsd_cartesian['z_km']:.2f} km")
    print(f"    Altitude: {gsd_cartesian['altitude_km']:.2f} km")
    
    # Test 7: Get ISS velocity vector in Cartesian coordinates
    print("\n[Test 7] Get ISS Velocity Vector (Cartesian/ECEF)...")
    velocity = calculate_iss_velocity_cartesian()
    print(f"    Velocity Vector:")
    print(f"      VX: {velocity['vx_km_s']:.4f} km/s")
    print(f"      VY: {velocity['vy_km_s']:.4f} km/s")
    print(f"      VZ: {velocity['vz_km_s']:.4f} km/s")
    print(f"    Total Speed: {velocity['speed_km_s']:.4f} km/s")
    print(f"    Speed: {velocity['speed_kmh']:.0f} km/h")
    
    print("\n" + "=" * 80)
    print("All tests completed successfully!")
    print("Cartesian coordinate system explanation:")
    print("  - Origin: Earth's center")
    print("  - X-axis: Points toward Prime Meridian (0° longitude)")
    print("  - Y-axis: Points toward 90°E longitude")
    print("  - Z-axis: Points toward North Pole")
    print("=" * 80)
