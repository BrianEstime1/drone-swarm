"""
Line Formation
===============

Simple follow-the-leader formation

Shape looks like this (top view):

    1 → 2 → 3

All drones fly in a straight line, one behind the other.

This is for:
- Narrow spaces
- Simple testing
- Maximum safety (drones far apart)
- Racing through obstacles
"""

from formation_base import Formation


class LineFormation(Formation):
    """
    Single-file line formation
    
    Each drone follows directly behind the previous one.
    
    Math is super simple:
    - Leader at (0, 0, 0)
    - Drone 2 at (-spacing, 0, 0)
    - Drone 3 at (-2*spacing, 0, 0)
    
    Negative north = behind/south
    """
    
    def __init__(self, spacing_meters=5.0):
        """
        Create a line formation
        
        Args:
            spacing_meters: Distance between each drone (default: 5 meters)
        """
        super().__init__(spacing_meters)
        
        # Drone 1 (leader) already at (0, 0, 0)
        
        # Drone 2: Directly behind leader
        self.offsets[2] = (
            -spacing_meters,  # Behind
            0,                # Same east/west position
            0                 # Same altitude
        )
        
        # Drone 3: Behind drone 2
        self.offsets[3] = (
            -2 * spacing_meters,  # Twice as far back
            0,                    # Same east/west position
            0                     # Same altitude
        )
    
    
    def set_spacing(self, new_spacing):
        """
        Override spacing change to maintain line
        
        Args:
            new_spacing: New spacing in meters
        """
        self.spacing = new_spacing
        
        # Recalculate offsets
        self.offsets[2] = (-new_spacing, 0, 0)
        self.offsets[3] = (-2 * new_spacing, 0, 0)
    
    
    def set_staggered_altitude(self, altitude_step):
        """
        Make each drone fly at a different altitude
        
        Creates a "staircase" effect:
        - Leader at base altitude
        - Drone 2 at base + altitude_step
        - Drone 3 at base + 2*altitude_step
        
        Useful for avoiding propwash and looking cool!
        
        Args:
            altitude_step: Altitude difference between drones (meters)
                          Positive = each drone higher than the one in front
                          Negative = each drone lower
        
        Example:
            formation.set_staggered_altitude(2)
            # Leader at 0m, Drone 2 at +2m, Drone 3 at +4m
        """
        north2, east2, _ = self.offsets[2]
        north3, east3, _ = self.offsets[3]
        
        self.offsets[2] = (north2, east2, altitude_step)
        self.offsets[3] = (north3, east3, 2 * altitude_step)
    
    
    def set_offset_position(self, offset_east):
        """
        Shift the line to the left or right
        
        Instead of:  1 → 2 → 3
        
        You get:     1
                       → 2
                           → 3
        
        Useful for flying alongside something!
        
        Args:
            offset_east: How far to shift east (meters)
                        Positive = shift right
                        Negative = shift left
        """
        north2, _, up2 = self.offsets[2]
        north3, _, up3 = self.offsets[3]
        
        self.offsets[2] = (north2, offset_east, up2)
        self.offsets[3] = (north3, 2 * offset_east, up3)


# ============================================================================
# TEST CODE
# ============================================================================

def test_line_formation():
    """
    Test the line formation and all its variations
    """
    print("Testing Line Formation...")
    print("=" * 70)
    
    # Test 1: Basic line
    print("\n1. Creating basic line formation (5m spacing)...")
    line = LineFormation(spacing_meters=5.0)
    line.visualize()
    
    # Test 2: Change spacing
    print("\n2. Changing spacing to 10 meters...")
    line.set_spacing(10.0)
    line.visualize()
    
    # Test 3: Staggered altitude
    print("\n3. Creating staircase (each drone 2m higher)...")
    line.set_spacing(5.0)  # Reset to 5m
    line.set_staggered_altitude(2.0)
    line.visualize()
    
    # Test 4: Offset position
    print("\n4. Offsetting line to the right (3m east)...")
    line_offset = LineFormation(spacing_meters=5.0)
    line_offset.set_offset_position(3.0)
    line_offset.visualize()
    
    # Test 5: Combined effects
    print("\n5. Combining stagger + offset...")
    line_combo = LineFormation(spacing_meters=5.0)
    line_combo.set_staggered_altitude(1.5)
    line_combo.set_offset_position(2.0)
    line_combo.visualize()
    
    # Test 6: Tight formation
    print("\n6. Tight formation (2m spacing)...")
    tight_line = LineFormation(spacing_meters=2.0)
    tight_line.visualize()
    
    # Test 7: Wide formation  
    print("\n7. Wide formation (15m spacing)...")
    wide_line = LineFormation(spacing_meters=15.0)
    wide_line.visualize()
    
    print("\n" + "=" * 70)
    print("Line formation tests completed!\n")


if __name__ == "__main__":
    test_line_formation()
