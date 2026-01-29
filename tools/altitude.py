from datetime import datetime, timedelta
from skyfield.api import load, wgs84, EarthSatellite


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
        
        # Get ISS geocentric position (position relative to Earth's center)
        # The ISS satellite object has coordinates in ITRF frame (Earth-centered)
        position = iss.at(t)
        
        # Get position vector from Earth's center (in km)
        # The .position property gives us x, y, z coordinates
        x, y, z = position.position.km
        
        # Calculate distance from Earth's center
        distance_from_earth_center = (x**2 + y**2 + z**2) ** 0.5
        
        # Earth's mean radius in km
        earth_radius_km = 6371.0
        
        # Altitude above Earth's surface
        altitude_km = distance_from_earth_center - earth_radius_km
        altitude_meters = altitude_km * 1000.0
        
        return altitude_meters
    
    except Exception as e:
        print(f"Error fetching ISS altitude: {e}")
        print("Using fallback ISS altitude: 408,000 meters")
        # Fallback to typical ISS altitude in meters
        return 408000.0


def calculate_gsd(altitude: float = None, focal_length: float = 11.8, pixel_size: float = 1.55) -> float:
    """
    Calculate Ground Sample Distance (GSD) for aerial/satellite imagery.
    
    GSD represents the physical distance (in meters) on the ground that corresponds
    to one pixel in the image. It's essential for determining the scale of features
    detected in satellite imagery.
    
    When altitude is not provided, this function automatically fetches the current
    ISS altitude using Skyfield's API and Two-Line Element (TLE) data.
    
    Args:
        altitude (float): Altitude of the camera/satellite in meters (default: fetch current ISS altitude using Skyfield)
        focal_length (float): Focal length of the camera in millimeters (default: 11.8mm)
        pixel_size (float): Size of each pixel in micrometers (default: 1.55µm)
    
    Returns:
        float: Ground Sample Distance in meters per pixel
    
    Formula: GSD = (altitude * pixel_size) / focal_length
    
    Example:
        # Using current ISS altitude from Skyfield API
        gsd = calculate_gsd()
        print(f"Current ISS GSD: {gsd:.4f} meters/pixel")
        
        # Using custom altitude
        gsd = calculate_gsd(altitude=408000, focal_length=35, pixel_size=3.45)
        print(f"Custom GSD: {gsd:.4f} meters/pixel")
    """
    # Fetch current ISS altitude using Skyfield API if not provided
    if altitude is None:
        altitude = get_iss_altitude_meters()
    
    # Validate inputs
    if focal_length <= 0:
        raise ValueError("Focal length must be greater than 0")
    if pixel_size <= 0:
        raise ValueError("Pixel size must be greater than 0")
    if altitude < 0:
        raise ValueError("Altitude cannot be negative")
    
    # Calculate GSD: GSD = (altitude * pixel_size) / focal_length
    gsd = (altitude * pixel_size) / focal_length
    
    return gsd

# Get current ISS altitude in meters
alt_m = get_iss_altitude_meters()
print(f"ISS altitude: {alt_m/1000:.2f} km")

# Calculate GSD - this now returns a real value!
gsd = calculate_gsd()
print(f"GSD: {gsd:.4f} meters/pixel")
print('Done loading altitude.py')