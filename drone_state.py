"""
Drone State - The "Notebook" for One Drone
==========================================

This class is like a notebook that keeps track of EVERYTHING about one drone:
- Where is it? (GPS position)
- How much battery does it have?
- Is it flying or on the ground?
- What's it supposed to be doing?

Think of it like a player card in a video game - all the stats in one place.

We'll make 3 of these (one for each drone in your swarm).
"""

import time
from enum import Enum


class FlightMode(Enum):
    """
    What is the drone currently doing?
    
    This is like different "modes" in a video game:
    - IDLE = sitting on ground, motors off
    - ARMED = motors spinning but not flying yet
    - TAKEOFF = lifting off the ground
    - HOLD = hovering in place
    - WAYPOINT = flying to a specific GPS point
    - FORMATION = following the leader in formation
    - RTH = Return To Home (coming back to launch point)
    - LANDING = coming down to land
    - EMERGENCY = something went wrong, landing NOW
    """
    IDLE = 0
    ARMED = 1
    TAKEOFF = 2
    HOLD = 3
    WAYPOINT = 4
    FORMATION = 5
    RTH = 6
    LANDING = 7
    EMERGENCY = 8


class DroneState:
    """
    Stores ALL the data for one drone
    
    Every 100ms (10 times per second), we'll update this with fresh data
    from the drone's flight controller.
    """
    
    def __init__(self, drone_id, role="follower"):
        """
        Create a new drone state tracker
        
        Args:
            drone_id: Number to identify this drone (1, 2, or 3)
            role: Either "leader" or "follower"
        """
        # ===== IDENTITY =====
        self.id = drone_id
        self.role = role  # "leader" or "follower"
        
        # ===== POSITION (from GPS) =====
        # These come from the GPS module on the flight controller
        self.lat = 0.0          # Latitude in degrees
        self.lon = 0.0          # Longitude in degrees  
        self.alt = 0.0          # Altitude in meters above sea level
        self.heading = 0.0      # Which way drone is pointing (0=North, 90=East, etc.)
        self.ground_speed = 0.0 # How fast moving in m/s
        
        # ===== ATTITUDE (from IMU - the gyroscope/accelerometer) =====
        # These tell us if the drone is tilted
        self.roll = 0.0   # Tilt left/right (degrees)
        self.pitch = 0.0  # Tilt forward/back (degrees)
        self.yaw = 0.0    # Rotation/spin (degrees)
        
        # ===== BATTERY =====
        self.battery_voltage = 0.0     # Volts (12.6V = full, 9.9V = empty for 3S)
        self.battery_cells = 3         # 3S battery (3 cells)
        self.battery_percent = 100.0   # 0-100%
        
        # ===== STATUS =====
        self.armed = False           # Are motors spinning?
        self.flight_mode = FlightMode.IDLE
        self.gps_fix = False         # Does GPS have a good signal?
        self.num_satellites = 0      # How many GPS satellites can it see?
        
        # ===== FORMATION TRACKING =====
        # Where SHOULD this drone be (for followers)
        self.target_lat = 0.0
        self.target_lon = 0.0
        self.target_alt = 0.0
        self.formation_offset = (0, 0, 0)  # (north_m, east_m, up_m) from leader
        
        # ===== SAFETY =====
        self.last_update = time.time()  # When did we last hear from this drone?
        self.connection_healthy = False
    
    
    def update_position(self, lat, lon, alt, heading, speed):
        """
        Update where the drone is right now
        
        Called every time we get fresh GPS data from the flight controller
        (about 10 times per second)
        
        Args:
            lat: Current latitude (degrees)
            lon: Current longitude (degrees)
            alt: Current altitude (meters)
            heading: Which direction drone is pointing (0-360 degrees)
            speed: How fast it's moving (m/s)
        """
        self.lat = lat
        self.lon = lon
        self.alt = alt
        self.heading = heading
        self.ground_speed = speed
        self.last_update = time.time()  # Remember when we got this data
        
        # Debug: Print position updates (comment out later when it's too noisy)
        # print(f"Drone {self.id}: ({lat:.6f}, {lon:.6f}) alt={alt:.1f}m")
    
    
    def update_battery(self, voltage):
        """
        Update battery voltage and calculate percentage remaining
        
        For a 3S LiPo battery:
        - Full charge: 12.6V (4.2V per cell)
        - Empty: 9.9V (3.3V per cell - don't go below this!)
        
        We calculate percentage based on voltage.
        
        Args:
            voltage: Current battery voltage (volts)
        """
        self.battery_voltage = voltage
        
        # Calculate voltage range for this battery
        full_voltage = self.battery_cells * 4.2   # 3 cells * 4.2V = 12.6V
        empty_voltage = self.battery_cells * 3.3  # 3 cells * 3.3V = 9.9V
        
        # Calculate percentage (simple linear interpolation)
        # Formula: (current - min) / (max - min) * 100
        voltage_range = full_voltage - empty_voltage
        voltage_above_empty = voltage - empty_voltage
        self.battery_percent = (voltage_above_empty / voltage_range) * 100
        
        # Make sure it's between 0-100 (just in case of weird readings)
        self.battery_percent = max(0, min(100, self.battery_percent))
        
        # Debug: Warn if battery is low
        if self.battery_percent < 25:
            print(f"⚠️  Drone {self.id} battery LOW: {self.battery_percent:.1f}%")
    
    
    def update_attitude(self, roll, pitch, yaw):
        """
        Update how the drone is tilted/rotated
        
        Args:
            roll: Tilt left/right in degrees
            pitch: Tilt forward/back in degrees  
            yaw: Rotation in degrees
        """
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw
    
    
    def is_healthy(self, timeout=1.0):
        """
        Check if we've heard from this drone recently
        
        If we haven't gotten data in over 1 second, something is wrong:
        - USB cable unplugged?
        - Flight controller crashed?
        - Radio link lost?
        
        Args:
            timeout: How many seconds before we consider connection lost
        
        Returns:
            True if connection is good, False if too much time has passed
        """
        time_since_update = time.time() - self.last_update
        return time_since_update < timeout
    
    
    def needs_rtl(self):
        """
        Should this drone return to launch?
        
        Return True if ANY of these are true:
        - Battery below 25%
        - Lost GPS fix
        - Connection timeout
        
        Returns:
            True if drone should return home NOW
        """
        return (self.battery_percent < 25.0 or 
                not self.gps_fix or 
                not self.is_healthy())
    
    
    def get_status_string(self):
        """
        Get a nice readable status string for debugging
        
        Returns:
            String like "Drone 2 [FOLLOWER]: (28.0000, -82.0000) 15m, 87% battery, 12 sats"
        """
        return (
            f"Drone {self.id} [{self.role.upper()}]: "
            f"({self.lat:.6f}, {self.lon:.6f}) {self.alt:.1f}m, "
            f"{self.battery_percent:.0f}% battery, "
            f"{self.num_satellites} sats, "
            f"{self.flight_mode.name}"
        )
    
    
    def __repr__(self):
        """
        What to show when you print() this drone
        
        Example:
            drone = DroneState(1, "leader")
            print(drone)  # Uses this function
        """
        return self.get_status_string()


# ============================================================================
# TEST CODE - Run this to see how DroneState works!
# ============================================================================

def test_drone_state():
    """
    Create some fake drones and test all the functions
    
    This simulates what will happen when real data comes in
    """
    print("Testing DroneState Class...")
    print("=" * 70)
    
    # Create 3 drones (like we'll have in the real swarm)
    print("\n1. Creating 3 drones...")
    drone1 = DroneState(1, role="leader")
    drone2 = DroneState(2, role="follower")
    drone3 = DroneState(3, role="follower")
    print(f"   ✓ Created {drone1.id}, {drone2.id}, {drone3.id}")
    
    # Simulate getting GPS data
    print("\n2. Simulating GPS updates...")
    drone1.update_position(28.0000, -82.0000, 15.0, 45.0, 2.5)
    drone2.update_position(28.0001, -82.0001, 15.0, 45.0, 2.5)
    drone3.update_position(27.9999, -82.0001, 15.0, 45.0, 2.5)
    print(f"   ✓ Updated positions")
    
    # Simulate battery readings
    print("\n3. Simulating battery updates...")
    drone1.update_battery(12.6)  # Full battery
    drone2.update_battery(11.4)  # ~50% battery
    drone3.update_battery(10.2)  # ~25% battery (LOW!)
    print(f"   Drone 1: {drone1.battery_percent:.0f}%")
    print(f"   Drone 2: {drone2.battery_percent:.0f}%")
    print(f"   Drone 3: {drone3.battery_percent:.0f}%")
    
    # Check health
    print("\n4. Checking drone health...")
    print(f"   Drone 1 healthy: {drone1.is_healthy()}")
    print(f"   Drone 2 healthy: {drone2.is_healthy()}")
    print(f"   Drone 3 healthy: {drone3.is_healthy()}")
    
    # Check if any need to return home
    print("\n5. Checking if any drones need RTL...")
    for drone in [drone1, drone2, drone3]:
        if drone.needs_rtl():
            print(f"   ⚠️  Drone {drone.id} should return to launch!")
        else:
            print(f"   ✓ Drone {drone.id} is good to keep flying")
    
    # Print full status
    print("\n6. Full status of all drones:")
    print(f"   {drone1}")
    print(f"   {drone2}")
    print(f"   {drone3}")
    
    # Simulate connection timeout
    print("\n7. Simulating connection loss...")
    print("   (Waiting 1.5 seconds to simulate timeout...)")
    time.sleep(1.5)
    
    if not drone1.is_healthy():
        print(f"   ❌ Drone {drone1.id} connection timed out!")
    else:
        print(f"   ✓ Drone {drone1.id} connection still good")
    
    print("\n" + "=" * 70)
    print("All DroneState tests completed!\n")


# If you run this file directly, it will run the tests
if __name__ == "__main__":
    test_drone_state()
