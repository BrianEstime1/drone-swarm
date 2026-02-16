"""
GPS Math Utilities for Drone Swarm
===================================

This file is the "calculator" for converting between:
- Meters (how humans think: "5 meters north")
- GPS degrees (how GPS thinks: "28.0000449 degrees latitude")

Think of GPS coordinates like a grid on a map:
- Latitude = How far north/south (like street numbers)
- Longitude = How far east/west (like avenue numbers)
"""

import math

# Constants
EARTH_RADIUS = 6371000  # Earth's radius in meters (about 6,371 km)

def meters_to_lat_offset(meters):
    """
    Convert meters north/south into latitude degrees
    
    Simple version: 1 degree latitude = 111,320 meters EVERYWHERE on Earth
    (This is constant because all latitude lines are the same distance apart)
    
    Example:
        If you move 5 meters north:
        5 / 111,320 = 0.0000449 degrees
    
    Args:
        meters: How many meters north (positive) or south (negative)
    
    Returns:
        Change in latitude (degrees)
    """
    return meters / 111320.0


def meters_to_lon_offset(meters, latitude):
    """
    Convert meters east/west into longitude degrees
    
    Tricky part: Longitude lines get CLOSER together near the poles!
    - At equator: 1 degree = 111,320 meters
    - At Tampa (28°N): 1 degree = 98,280 meters  
    - At North Pole: 1 degree = 0 meters (all lines meet!)
    
    We use cos(latitude) to adjust for this.
    
    Example at Tampa (28°N):
        If you move 3 meters east:
        3 / (111,320 * cos(28°)) = 3 / 98,280 = 0.0000305 degrees
    
    Args:
        meters: How many meters east (positive) or west (negative)
        latitude: Current latitude in degrees (needed for the calculation)
    
    Returns:
        Change in longitude (degrees)
    """
    # Convert latitude to radians because Python's cos() needs radians
    lat_radians = math.radians(latitude)
    
    # Calculate how many meters per degree at this latitude
    meters_per_degree = 111320.0 * math.cos(lat_radians)
    
    # Convert meters to degrees
    return meters / meters_per_degree


def offset_gps_position(origin_lat, origin_lon, north_m, east_m):
    """
    THE MAIN FUNCTION - This is what we'll use all the time!
    
    Given a starting GPS position and meter offsets, calculate new GPS position.
    
    This is how we tell follower drones where to go!
    
    Example:
        Leader is at: (28.0000, -82.0000)
        Want follower 5m north, 3m east
        
        Call: offset_gps_position(28.0000, -82.0000, 5, 3)
        Returns: (28.0000449, -81.9999695)
    
    Args:
        origin_lat: Starting latitude (degrees)
        origin_lon: Starting longitude (degrees)
        north_m: Meters to move north (negative = south)
        east_m: Meters to move east (negative = west)
    
    Returns:
        Tuple of (new_latitude, new_longitude) in degrees
    """
    # Calculate how much to change latitude (simple)
    lat_change = meters_to_lat_offset(north_m)
    new_lat = origin_lat + lat_change
    
    # Calculate how much to change longitude (needs current latitude)
    lon_change = meters_to_lon_offset(east_m, origin_lat)
    new_lon = origin_lon + lon_change
    
    return new_lat, new_lon


def distance_between_gps(lat1, lon1, lat2, lon2):
    """
    Calculate distance in meters between two GPS points
    
    Uses the Haversine formula - fancy name but it just means:
    "Calculate distance on a sphere (Earth is round!)"
    
    For small distances, you could use Pythagorean theorem, but this
    works anywhere on Earth, even if drones are kilometers apart.
    
    Example:
        Point A: (28.0000, -82.0000)
        Point B: (28.0001, -82.0000)
        Distance: about 11 meters
    
    Args:
        lat1, lon1: First GPS point (degrees)
        lat2, lon2: Second GPS point (degrees)
    
    Returns:
        Distance in meters
    """
    # Convert all coordinates to radians (math functions need radians)
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Calculate differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula (don't worry about the details, just trust it works)
    a = (math.sin(dlat/2)**2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2)
    c = 2 * math.asin(math.sqrt(a))
    
    # Multiply by Earth's radius to get meters
    distance_meters = EARTH_RADIUS * c
    
    return distance_meters


def bearing_between_gps(lat1, lon1, lat2, lon2):
    """
    Calculate the direction from point 1 to point 2
    
    Returns a compass heading:
    - 0° = North
    - 90° = East  
    - 180° = South
    - 270° = West
    
    Useful for knowing which way drones are facing or moving.
    
    Example:
        You're at (28.0000, -82.0000)
        Target is at (28.0001, -82.0000) - directly north
        Bearing: 0°
    
    Args:
        lat1, lon1: Starting point (degrees)
        lat2, lon2: Target point (degrees)
    
    Returns:
        Bearing in degrees (0-360)
    """
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Calculate bearing
    dlon = lon2_rad - lon1_rad
    
    x = math.sin(dlon) * math.cos(lat2_rad)
    y = (math.cos(lat1_rad) * math.sin(lat2_rad) - 
         math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon))
    
    bearing_rad = math.atan2(x, y)
    bearing_deg = math.degrees(bearing_rad)
    
    # Normalize to 0-360
    bearing_deg = (bearing_deg + 360) % 360
    
    return bearing_deg


# ============================================================================
# TEST FUNCTIONS - Run these to make sure everything works!
# ============================================================================

def test_gps_math():
    """
    Test all the GPS functions to make sure they work correctly
    
    Run this file with: python gps_math.py
    If you see "All tests passed!" then the math is working!
    """
    print("Testing GPS Math Functions...")
    print("=" * 50)
    
    # Test 1: Offset calculation
    print("\nTest 1: Moving 5m north, 3m east from Tampa")
    origin_lat = 28.0000
    origin_lon = -82.0000
    new_lat, new_lon = offset_gps_position(origin_lat, origin_lon, 5, 3)
    print(f"  Start: ({origin_lat}, {origin_lon})")
    print(f"  End:   ({new_lat:.7f}, {new_lon:.7f})")
    
    # Test 2: Distance calculation
    print("\nTest 2: Distance between two points")
    lat1, lon1 = 28.0000, -82.0000
    lat2, lon2 = 28.0001, -82.0000
    distance = distance_between_gps(lat1, lon1, lat2, lon2)
    print(f"  Point A: ({lat1}, {lon1})")
    print(f"  Point B: ({lat2}, {lon2})")
    print(f"  Distance: {distance:.2f} meters")
    print(f"  (Should be about 11 meters)")
    
    # Test 3: Bearing calculation
    print("\nTest 3: Bearing from A to B")
    bearing = bearing_between_gps(lat1, lon1, lat2, lon2)
    print(f"  From: ({lat1}, {lon1})")
    print(f"  To:   ({lat2}, {lon2})")
    print(f"  Bearing: {bearing:.1f}°")
    print(f"  (Should be 0° - due north)")
    
    # Test 4: Round trip test
    print("\nTest 4: Round trip test (go and come back)")
    # Start at Tampa
    start_lat, start_lon = 28.0000, -82.0000
    
    # Move 10m north, 5m east
    mid_lat, mid_lon = offset_gps_position(start_lat, start_lon, 10, 5)
    
    # Move back 10m south, 5m west
    end_lat, end_lon = offset_gps_position(mid_lat, mid_lon, -10, -5)
    
    print(f"  Start:  ({start_lat}, {start_lon})")
    print(f"  Middle: ({mid_lat:.7f}, {mid_lon:.7f})")
    print(f"  End:    ({end_lat:.7f}, {end_lon:.7f})")
    
    # Check if we're back where we started (within 1mm)
    error = distance_between_gps(start_lat, start_lon, end_lat, end_lon)
    print(f"  Error: {error*1000:.6f} mm")
    if error < 0.001:  # Less than 1mm error
        print(f"  ✓ Round trip successful!")
    else:
        print(f"  ✗ Round trip failed - check the math!")
    
    print("\n" + "=" * 50)
    print("All tests completed!\n")


# If you run this file directly (python gps_math.py), it will run the tests
if __name__ == "__main__":
    test_gps_math()
