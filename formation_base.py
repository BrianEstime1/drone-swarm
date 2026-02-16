"""
Formation Base Class
====================

This is the "template" for all formation patterns.

Think of it like a blueprint - we'll use this to create:
- Triangle formation
- Line formation  
- V formation (later)
- Circle formation (later)
- Whatever cool patterns you dream up!

All formations share the same basic idea:
"Where should each drone be relative to the leader?"
"""

import math


class Formation:
    """
    Base class for all drone formations
    
    A formation is just a set of rules that say:
    "Drone 1 (leader) is at position (0, 0, 0)"
    "Drone 2 should be X meters north, Y meters east, Z meters up"
    "Drone 3 should be ..."
    
    We store these as "offsets" - distances from the leader.
    """
    
    def __init__(self, spacing_meters=5.0):
        """
        Create a new formation
        
        Args:
            spacing_meters: How far apart should drones be? (default: 5 meters)
        """
        self.spacing = spacing_meters
        
        # Dictionary to store where each drone should be
        # Key = drone ID (1, 2, 3)
        # Value = (north_meters, east_meters, up_meters)
        self.offsets = {}
        
        # Leader (drone 1) is always at origin
        self.offsets[1] = (0, 0, 0)
    
    
    def get_offset(self, drone_id):
        """
        Get the formation offset for a specific drone
        
        Args:
            drone_id: Which drone? (1, 2, or 3)
        
        Returns:
            Tuple of (north_m, east_m, up_m)
            Example: (-5, 0, 0) means "5 meters south of leader"
        """
        return self.offsets.get(drone_id, (0, 0, 0))
    
    
    def get_all_offsets(self):
        """
        Get offsets for all drones
        
        Returns:
            Dictionary of {drone_id: (north, east, up)}
        """
        return self.offsets.copy()
    
    
    def set_spacing(self, new_spacing):
        """
        Change the spacing between drones
        
        This will recalculate all the offsets based on the new spacing.
        Subclasses should override this if they need custom behavior.
        
        Args:
            new_spacing: New spacing in meters
        """
        scale_factor = new_spacing / self.spacing
        self.spacing = new_spacing
        
        # Scale all existing offsets (except leader at origin)
        for drone_id in self.offsets:
            if drone_id != 1:  # Don't move the leader
                north, east, up = self.offsets[drone_id]
                self.offsets[drone_id] = (
                    north * scale_factor,
                    east * scale_factor,
                    up * scale_factor
                )
    
    
    def rotate(self, heading_deg):
        """
        Rotate the formation to match a heading
        
        For example, if the leader is flying northeast (45°),
        the followers should rotate to maintain the formation
        relative to the leader's direction.
        
        This is ADVANCED - we'll implement it later when we want
        formations to maintain their shape regardless of direction.
        
        Args:
            heading_deg: Heading in degrees (0 = North, 90 = East)
        """
        # Convert heading to radians
        heading_rad = math.radians(heading_deg)
        
        # Rotate each offset point
        for drone_id in self.offsets:
            if drone_id != 1:  # Don't rotate the leader
                north, east, up = self.offsets[drone_id]
                
                # 2D rotation matrix
                # new_north = north * cos(θ) - east * sin(θ)
                # new_east = north * sin(θ) + east * cos(θ)
                new_north = north * math.cos(heading_rad) - east * math.sin(heading_rad)
                new_east = north * math.sin(heading_rad) + east * math.cos(heading_rad)
                
                self.offsets[drone_id] = (new_north, new_east, up)
    
    
    def visualize(self):
        """
        Print a simple ASCII visualization of the formation
        
        This helps you see what the formation looks like!
        """
        print(f"\n{self.__class__.__name__} (spacing: {self.spacing}m)")
        print("=" * 50)
        
        for drone_id, (north, east, up) in sorted(self.offsets.items()):
            role = "LEADER" if drone_id == 1 else "FOLLOWER"
            print(f"  Drone {drone_id} [{role}]: "
                  f"N={north:+6.1f}m, E={east:+6.1f}m, U={up:+6.1f}m")
        
        print("=" * 50)
    
    
    def __repr__(self):
        """
        String representation of the formation
        """
        return f"{self.__class__.__name__}(spacing={self.spacing}m, drones={len(self.offsets)})"


# ============================================================================
# TEST CODE
# ============================================================================

def test_formation_base():
    """
    Test the base Formation class
    """
    print("Testing Formation Base Class...")
    print("=" * 70)
    
    # Create a basic formation
    print("\n1. Creating a basic formation...")
    formation = Formation(spacing=5.0)
    print(f"   Created: {formation}")
    
    # Check leader offset
    print("\n2. Checking leader position...")
    leader_offset = formation.get_offset(1)
    print(f"   Leader offset: {leader_offset}")
    print(f"   (Should be (0, 0, 0) - leader is always at origin)")
    
    # Manually add some followers for testing
    print("\n3. Adding test followers...")
    formation.offsets[2] = (-5, 0, 0)  # 5m behind leader
    formation.offsets[3] = (-5, 5, 0)  # 5m behind, 5m right
    formation.visualize()
    
    # Test spacing change
    print("\n4. Testing spacing change (5m → 10m)...")
    formation.set_spacing(10.0)
    formation.visualize()
    
    # Test rotation
    print("\n5. Testing rotation (45° clockwise)...")
    formation.rotate(45)
    formation.visualize()
    
    print("\n" + "=" * 70)
    print("Formation base tests completed!\n")


if __name__ == "__main__":
    test_formation_base()
