"""
Swarm Controller - The BRAIN
=============================

This is the main coordinator that makes everything work together!


"""

import time
from drone_state import DroneState, FlightMode
from triangle_formation import TriangleFormation
from line_formation import LineFormation
from gps_math import offset_gps_position, distance_between_gps


class MockMSPConnection:
    """
    FAKE flight controller connection for testing
    
    This simulates getting data from real drones.
    When we build the actual drones, we'll replace this with
    real pymsp code that talks to the STM32F405 flight controllers.
    
    For now, this lets us test everything without hardware!
    """
    
    def __init__(self, port, drone_id):
        self.port = port
        self.drone_id = drone_id
        self.connected = False
        
        # Fake GPS positions (Tampa area)
        # Each drone starts at slightly different position
        self.fake_lat = 28.0000 + (drone_id - 1) * 0.0001
        self.fake_lon = -82.0000 + (drone_id - 1) * 0.0001
        self.fake_alt = 15.0
        self.fake_battery = 12.6 - (drone_id - 1) * 0.5  # Drone 1 full, others slightly less
        
    def connect(self):
        """Pretend to connect to flight controller"""
        print(f"  [Mock] Connecting to {self.port}...")
        time.sleep(0.1)  # Simulate connection delay
        self.connected = True
        return True
    
    def get_gps(self):
        """Return fake GPS data"""
        # Add tiny random movement to simulate real drone drift
        import random
        drift = random.uniform(-0.000005, 0.000005)
        
        return {
            'lat': self.fake_lat + drift,
            'lon': self.fake_lon + drift,
            'alt': self.fake_alt,
            'ground_speed': 0.0,
            'num_sat': 12
        }
    
    def get_battery(self):
        """Return fake battery data"""
        # Slowly drain battery
        self.fake_battery -= 0.001
        return {'voltage': max(9.9, self.fake_battery)}
    
    def get_status(self):
        """Return fake status"""
        return {
            'armed': True,
            'flight_mode': 0
        }
    
    def send_waypoint(self, lat, lon, alt):
        """Pretend to send waypoint command"""
        # In real version, this sends MSP command to flight controller
        # For now, just simulate drone moving toward target
        self.fake_lat += (lat - self.fake_lat) * 0.1  # Move 10% toward target
        self.fake_lon += (lon - self.fake_lon) * 0.1
        self.fake_alt += (alt - self.fake_alt) * 0.1
        
        print(f"    [Drone {self.drone_id}] Waypoint set: ({lat:.6f}, {lon:.6f}) alt={alt:.1f}m")
    
    def arm(self):
        """Arm the drone (start motors)"""
        print(f"    [Drone {self.drone_id}] ARMED")
    
    def disarm(self):
        """Disarm the drone (stop motors)"""
        print(f"    [Drone {self.drone_id}] DISARMED")


class SwarmController:
    """
    Main coordinator for the drone swarm
    
    This is what you'll actually run to fly the swarm!
    
    Workflow:
    1. Create controller
    2. Add drones
    3. Connect to all drones
    4. Set formation
    5. Run main loop
    """
    
    def __init__(self):
        """Initialize the swarm controller"""
        self.drones = {}          # drone_id -> DroneState
        self.connections = {}     # drone_id -> MSPConnection
        self.current_formation = None
        self.running = False
        
        print("SwarmController initialized")
    
    def add_drone(self, drone_id, port, role="follower"):
        """
        Add a drone to the swarm
        
        Args:
            drone_id: ID number (1, 2, or 3)
            port: Serial port (e.g., "/dev/ttyUSB0")
            role: "leader" or "follower"
        """
        self.drones[drone_id] = DroneState(drone_id, role)
        self.connections[drone_id] = MockMSPConnection(port, drone_id)
        print(f"Added Drone {drone_id} as {role.upper()}")
    
    def connect_all(self):
        """
        Connect to all drones
        
        This establishes serial communication with each flight controller
        """
        print("\nConnecting to all drones...")
        success_count = 0
        
        for drone_id, conn in self.connections.items():
            if conn.connect():
                print(f"  ✓ Drone {drone_id} connected")
                success_count += 1
            else:
                print(f"  ✗ Drone {drone_id} FAILED to connect")
        
        if success_count == len(self.drones):
            print(f"✓ All {success_count} drones connected!\n")
            return True
        else:
            print(f"✗ Only {success_count}/{len(self.drones)} drones connected\n")
            return False
    
    def update_telemetry(self):
        """
        Poll all drones for latest data
        
        This runs 10 times per second in the main loop.
        Gets GPS, battery, status from each drone.
        """
        for drone_id in self.drones:
            conn = self.connections[drone_id]
            drone = self.drones[drone_id]
            
            # Get GPS position
            gps = conn.get_gps()
            drone.update_position(
                gps['lat'],
                gps['lon'],
                gps['alt'],
                0,  # heading (we'll add this later)
                gps['ground_speed']
            )
            drone.num_satellites = gps['num_sat']
            drone.gps_fix = gps['num_sat'] >= 6
            
            # Get battery
            battery = conn.get_battery()
            drone.update_battery(battery['voltage'])
            
            # Get status
            status = conn.get_status()
            drone.armed = status['armed']
    
    def set_formation(self, formation_type, spacing=5.0):
        """
        Set the current formation
        
        Args:
            formation_type: "triangle" or "line"
            spacing: Distance between drones in meters
        """
        if formation_type == "triangle":
            self.current_formation = TriangleFormation(spacing)
            print(f"Formation set to TRIANGLE ({spacing}m spacing)")
        elif formation_type == "line":
            self.current_formation = LineFormation(spacing)
            print(f"Formation set to LINE ({spacing}m spacing)")
        else:
            print(f"❌ Unknown formation: {formation_type}")
            return
        
        # Show the formation
        self.current_formation.visualize()
    
    def maintain_formation(self):
        """
        Calculate and send waypoints to maintain formation
        
        This is THE CORE FUNCTION - where the magic happens!
        
        Steps:
        1. Find the leader drone
        2. For each follower:
           a. Get formation offset (e.g., "5m behind, 3m left")
           b. Convert offset to GPS coordinates
           c. Send waypoint command
        """
        if not self.current_formation:
            return
        
        # Find the leader
        leader = None
        for drone in self.drones.values():
            if drone.role == "leader":
                leader = drone
                break
        
        if not leader:
            print("❌ No leader drone found!")
            return
        
        # Update each follower
        for drone_id, drone in self.drones.items():
            if drone.role == "follower":
                # Get where this drone SHOULD be (formation offset)
                north_m, east_m, up_m = self.current_formation.get_offset(drone_id)
                
                # Convert to GPS coordinates using our GPS math!
                target_lat, target_lon = offset_gps_position(
                    leader.lat,
                    leader.lon,
                    north_m,
                    east_m
                )
                target_alt = leader.alt + up_m
                
                # Save target for monitoring
                drone.target_lat = target_lat
                drone.target_lon = target_lon
                drone.target_alt = target_alt
                
                # Send command to flight controller
                self.connections[drone_id].send_waypoint(
                    target_lat,
                    target_lon,
                    target_alt
                )
                
                # Calculate how far off we are (formation error)
                error = distance_between_gps(
                    drone.lat, drone.lon,
                    target_lat, target_lon
                )
                
                print(f"    [Drone {drone_id}] Formation error: {error:.2f}m")
    
    def check_safety(self):
        """
        Monitor safety conditions for all drones
        
        Checks:
        - Connection health (are we getting data?)
        - Battery level (time to come home?)
        - GPS fix (do we know where we are?)
        """
        for drone_id, drone in self.drones.items():
            # Check connection
            if not drone.is_healthy(timeout=1.0):
                print(f"⚠️  WARNING: Drone {drone_id} connection timeout!")
                self.emergency_land(drone_id)
                return False
            
            # Check battery
            if drone.battery_percent < 25:
                print(f"⚠️  WARNING: Drone {drone_id} battery LOW ({drone.battery_percent:.1f}%)")
                self.return_to_launch(drone_id)
            
            # Check GPS
            if not drone.gps_fix:
                print(f"⚠️  WARNING: Drone {drone_id} lost GPS fix!")
                self.hold_position(drone_id)
        
        return True
    
    def hold_position(self, drone_id):
        """Tell drone to hover in place"""
        drone = self.drones[drone_id]
        print(f"🛑 Drone {drone_id} HOLDING POSITION")
        drone.flight_mode = FlightMode.HOLD
    
    def return_to_launch(self, drone_id):
        """Tell drone to return home"""
        print(f"🏠 Drone {drone_id} RETURNING TO LAUNCH")
        self.drones[drone_id].flight_mode = FlightMode.RTH
    
    def emergency_land(self, drone_id):
        """Emergency landing NOW"""
        print(f"🚨 EMERGENCY: Landing Drone {drone_id} IMMEDIATELY")
        self.drones[drone_id].flight_mode = FlightMode.EMERGENCY
    
    def print_status(self):
        """Print current status of all drones"""
        print("\n" + "="*80)
        print("SWARM STATUS")
        print("="*80)
        for drone_id in sorted(self.drones.keys()):
            drone = self.drones[drone_id]
            print(drone.get_status_string())
        print("="*80 + "\n")
    
    def run(self, update_rate_hz=10, duration_seconds=None):
        """
        Main control loop
        
        This is what actually flies the swarm!
        
        Args:
            update_rate_hz: How many times per second to update (default: 10)
            duration_seconds: How long to run (None = forever until Ctrl+C)
        """
        self.running = True
        update_interval = 1.0 / update_rate_hz
        
        start_time = time.time()
        iteration = 0
        
        print(f"\n{'='*80}")
        print(f"STARTING SWARM CONTROLLER")
        print(f"Update rate: {update_rate_hz} Hz ({update_interval*1000:.0f}ms per loop)")
        if duration_seconds:
            print(f"Duration: {duration_seconds} seconds")
        else:
            print("Duration: Unlimited (press Ctrl+C to stop)")
        print(f"{'='*80}\n")
        
        try:
            while self.running:
                loop_start = time.time()
                iteration += 1
                
                # Main control loop
                print(f"\n--- Iteration {iteration} ---")
                
                # 1. Get fresh data from all drones
                self.update_telemetry()
                
                # 2. Calculate and send formation waypoints
                self.maintain_formation()
                
                # 3. Check safety
                if not self.check_safety():
                    print("❌ Safety check failed - stopping")
                    break
                
                # 4. Print status every 10 iterations (once per second at 10Hz)
                if iteration % 10 == 0:
                    self.print_status()
                
                # 5. Check if we should stop
                if duration_seconds:
                    elapsed = time.time() - start_time
                    if elapsed >= duration_seconds:
                        print(f"\n✓ Duration complete ({duration_seconds}s)")
                        break
                
                # 6. Sleep to maintain update rate
                elapsed = time.time() - loop_start
                sleep_time = max(0, update_interval - elapsed)
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Ctrl+C detected - shutting down gracefully...")
        
        finally:
            self.running = False
            print("\n" + "="*80)
            print("SWARM CONTROLLER STOPPED")
            print("="*80)
            self.print_status()


# ============================================================================
# TEST CODE - Run a simulation!
# ============================================================================

def test_swarm_controller():
    """
    Test the swarm controller with fake drones
    
    This simulates what will happen when you fly for real!
    """
    print("\n" + "="*80)
    print("SWARM CONTROLLER SIMULATION")
    print("="*80 + "\n")
    
    # 1. Create the swarm controller
    swarm = SwarmController()
    
    # 2. Add 3 drones
    swarm.add_drone(1, "/dev/ttyUSB0", role="leader")
    swarm.add_drone(2, "/dev/ttyUSB1", role="follower")
    swarm.add_drone(3, "/dev/ttyUSB2", role="follower")
    
    # 3. Connect to all drones
    if not swarm.connect_all():
        print("❌ Failed to connect to all drones")
        return
    
    # 4. Set formation
    print("\n" + "="*80)
    swarm.set_formation("triangle", spacing=5.0)
    print("="*80)
    
    # 5. Run for 5 seconds
    print("\nStarting swarm operation...")
    swarm.run(update_rate_hz=2, duration_seconds=5)  # Slow update for readable output
    
    print("\n✓ Simulation complete!\n")


if __name__ == "__main__":
    test_swarm_controller()
