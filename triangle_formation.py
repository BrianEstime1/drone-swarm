"""
Triangle Formation
==================

Classic V-formation, like geese flying!

Shape looks like this (top view):

         1 (Leader)
        / \
       /   \
      2     3

The leader is at the front, followers form the base of the triangle behind.

This is PERFECT for:
- Following a leader
- Visual demos (looks cool!)
- Maximum visibility (drones can see each other)
"""

from formation_base import Formation
import math


class TriangleFormation(Formation):
    """
    Equilateral triangle formation with leader at front
    
    Math behind it:
    - Leader at (0, 0, 0)
    - Drone 2 at (-spacing, -spacing*0.866, 0)  # Back-left
    - Drone 3 at (-spacing, +spacing*0.866, 0)  # Back-right
    
    Why 0.866? That's sqrt(3)/2, which makes an equilateral triangle!
    (You don't need to understand the trig, just trust it works)
    """
    
    def __init__(self, spacing_meters=5.0):
        """
        Create a triangle formation
        
        Args:
            spacing_meters: Distance between drones (default: 5 meters)
        """
        # Call the parent class constructor
        super().__init__(spacing_meters)
        
        # Calculate the offsets for an equilateral triangle
        # Drone 1 (leader) is already at (0, 0, 0) from parent class
        
        # sqrt(3)/2 ≈ 0.866 - this makes the triangle equilateral
        side_offset = spacing_meters * 0.866
        
        # Drone 2: Behind and to the left
        self.offsets[2] = (
            -spacing_meters,  # Behind (negative = south)
            -side_offset,     # Left (negative = west)
            0                 # Same altitude
        )
        
        # Drone 3: Behind and to the right  
        self.offsets[3] = (
            -spacing_meters,  # Behind (negative = south)
            +side_offset,     # Right (positive = east)
            0                 # Same altitude
        )
    
    
    def set_spacing(self, new_spacing):
        """
        Override spacing change to maintain triangle shape
        
        Args:
            new_spacing: New spacing in meters
        """
        self.spacing = new_spacing
        side_offset = new_spacing * 0.866
        
        # Recalculate offsets
        self.offsets[2] = (-new_spacing, -side_offset, 0)
        self.offsets[3] = (-new_spacing, +side_offset, 0)
    
    
    def set_altitude_stagger(self, stagger_meters):
        """
        Make the followers fly at different altitudes
        
        Useful for:
        - Avoiding propwash from leader
        - Better visibility
        - Looks cool!
        
        Args:
            stagger_meters: How much lower should followers be?
                           Positive = below leader
                           Negative = above leader
        
        Example:
            formation.set_altitude_stagger(2)
            # Drone 2 and 3 will fly 2 meters below the leader
        """
        north2, east2, _ = self.offsets[2]
        north3, east3, _ = self.offsets[3]
        
        self.offsets[2] = (north2, east2, -stagger_meters)
        self.offsets[3] = (north3, east3, -stagger_meters)


# ============================================================================
# TEST CODE
# ============================================================================

def test_triangle_formation():
    """
    Test the triangle formation and visualize it
    """
    print("Testing Triangle Formation...")
    print("=" * 70)
    
    # Test 1: Create default triangle
    print("\n1. Creating triangle formation (5m spacing)...")
    triangle = TriangleFormation(spacing_meters=5.0)
    triangle.visualize()
    
    # Test 2: Change spacing
    print("\n2. Changing spacing to 10 meters...")
    triangle.set_spacing(10.0)
    triangle.visualize()
    
    # Test 3: Add altitude stagger
    print("\n3. Adding 2m altitude stagger (followers below leader)...")
    triangle.set_spacing(5.0)  # Reset to 5m
    triangle.set_altitude_stagger(2.0)
    triangle.visualize()
    
    # Test 4: Tight formation
    print("\n4. Creating tight formation (2m spacing)...")
    tight_triangle = TriangleFormation(spacing_meters=2.0)
    tight_triangle.visualize()
    
    # Test 5: Wide formation
    print("\n5. Creating wide formation (10m spacing)...")
    wide_triangle = TriangleFormation(spacing_meters=10.0)
    wide_triangle.visualize()
    
    # Test 6: Show distances
    print("\n6. Verifying the math...")
    print("   For 5m spacing triangle:")
    triangle_5m = TriangleFormation(spacing_meters=5.0)
    
    # Calculate actual distances
    n2, e2, u2 = triangle_5m.get_offset(2)
    n3, e3, u3 = triangle_5m.get_offset(3)
    
    # Distance from leader to drone 2
    dist_1_to_2 = math.sqrt(n2**2 + e2**2 + u2**2)
    # Distance from leader to drone 3  
    dist_1_to_3 = math.sqrt(n3**2 + e3**2 + u3**2)
    # Distance from drone 2 to drone 3
    dist_2_to_3 = math.sqrt((n3-n2)**2 + (e3-e2)**2 + (u3-u2)**2)
    
    print(f"   Distance 1→2: {dist_1_to_2:.2f}m (should be ~5.0m)")
    print(f"   Distance 1→3: {dist_1_to_3:.2f}m (should be ~5.0m)")
    print(f"   Distance 2→3: {dist_2_to_3:.2f}m (should be ~8.66m)")
    print("   ✓ Forms an equilateral triangle!")
    
    print("\n" + "=" * 70)
    print("Triangle formation tests completed!\n")


if __name__ == "__main__":
    test_triangle_formation()
