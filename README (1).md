# Autonomous Drone Swarm Project

**Building a 3-drone autonomous swarm system for formation flight**

![Status](https://img.shields.io/badge/status-in_development-yellow)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![Hardware](https://img.shields.io/badge/hardware-STM32F405-green)

---

## 🎯 Project Goal

Create an autonomous drone swarm capable of coordinated formation flight using STM32F405 flight controllers running INAV firmware. Target completion: **May 2026** for aerospace internship portfolio.

## 🚁 Hardware

- **Flight Controllers:** STM32F405 with INAV firmware
- **Number of Drones:** 3 (1 leader, 2 followers)
- **Communication:** MSP (MultiWii Serial Protocol) over USB/UART
- **GPS:** Integrated GPS modules for positioning
- **Battery:** 3S LiPo batteries

## 🧠 Software Architecture

### Core Components

1. **GPS Math (`gps_math.py`)** - Converts between GPS coordinates (degrees) and meter offsets
2. **Drone State (`drone_state.py`)** - Tracks position, battery, status for each drone
3. **Formations** - Defines geometric patterns:
   - `formation_base.py` - Base class template
   - `triangle_formation.py` - V-formation (like geese)
   - `line_formation.py` - Single-file follow pattern
4. **Swarm Controller (`swarm_controller.py`)** - Main coordination logic
5. **Main Runner (`main.py`)** - Easy interface for testing

### How It Works

```
Every 0.1 seconds (10 Hz):
1. Poll all drones for GPS, battery, status
2. Calculate where followers should be based on formation
3. Convert leader's position + offsets → GPS waypoints
4. Send waypoint commands to followers
5. Monitor safety (battery, GPS fix, connection)
```

## 📁 Project Structure

```
drone-swarm/
├── gps_math.py              # GPS coordinate conversions
├── drone_state.py           # Individual drone data tracking
├── formation_base.py        # Formation pattern template
├── triangle_formation.py    # Triangle/V formation
├── line_formation.py        # Line formation
├── swarm_controller.py      # Main swarm coordinator
├── main.py                  # Entry point for running swarm
└── README.md                # This file
```

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/BrianEstime1/drone-swarm.git
cd drone-swarm

# Install dependencies (when hardware is ready)
pip install pymsp --break-system-packages
```

### Running Simulations (No Hardware Required)

```bash
# Interactive menu
python3 main.py

# Command line
python3 main.py --formation triangle --spacing 5 --duration 10

# Run all tests
python3 main.py --test

# Test individual components
python3 gps_math.py          # Test GPS calculations
python3 drone_state.py        # Test drone state tracking
python3 triangle_formation.py # Test triangle formation
python3 line_formation.py     # Test line formation
python3 swarm_controller.py   # Test full swarm
```

## 🧪 Testing Individual Components

### GPS Math
```python
from gps_math import offset_gps_position, distance_between_gps

# Move 5m north, 3m east from Tampa
new_lat, new_lon = offset_gps_position(28.0000, -82.0000, 5, 3)
print(f"New position: ({new_lat}, {new_lon})")

# Calculate distance between two points
dist = distance_between_gps(28.0000, -82.0000, 28.0001, -82.0000)
print(f"Distance: {dist:.2f} meters")
```

### Formations
```python
from triangle_formation import TriangleFormation

# Create triangle with 5m spacing
triangle = TriangleFormation(spacing_meters=5.0)
triangle.visualize()

# Change spacing
triangle.set_spacing(10.0)

# Add altitude stagger (followers fly 2m below leader)
triangle.set_altitude_stagger(2.0)
```

### Drone State
```python
from drone_state import DroneState

# Create a drone
drone = DroneState(drone_id=1, role="leader")

# Update with GPS data
drone.update_position(lat=28.0000, lon=-82.0000, alt=15.0, heading=45.0, speed=2.5)

# Update battery
drone.update_battery(voltage=12.6)

# Check if drone needs to return home
if drone.needs_rtl():
    print("Battery low or GPS lost - return to launch!")

# Print status
print(drone.get_status_string())
```

## 📊 Current Status

**Completed:**
- ✅ GPS coordinate conversion math
- ✅ Drone state tracking system
- ✅ Formation definitions (triangle, line)
- ✅ Main swarm controller logic
- ✅ Simulation framework (no hardware required)

**In Progress:**
- 🔄 Hardware assembly (drone build scheduled for Feb 21, 2026)

**To Do:**
- ⏳ Replace mock MSP with real pymsp library
- ⏳ Flight controller configuration
- ⏳ Bench testing with props off
- ⏳ First flight tests
- ⏳ Formation flight testing
- ⏳ Advanced features (dynamic heading, altitude control)

## 🎓 Educational Context

This project is part of my electrical engineering curriculum at Hillsborough Community College, focusing on:
- Embedded systems (STM32 microcontrollers)
- Control systems (PID, waypoint navigation)
- Real-time programming (10Hz control loop)
- Serial communication protocols (MSP)
- GPS coordinate transformations
- Multi-agent systems

Preparing for transfer to UCF's Intelligent Robotic Systems program (Fall 2026) and aerospace industry internships.

## 🛠️ Technologies

- **Language:** Python 3.8+
- **Hardware:** STM32F405 flight controllers
- **Firmware:** INAV
- **Protocol:** MSP (MultiWii Serial Protocol)
- **Libraries:** pymsp, math, time

## 📝 Development Log

**Week 1 (Feb 16, 2026):**
- Built complete software architecture
- Implemented GPS math, drone state tracking, formations
- Created swarm controller with simulation
- All components tested and working without hardware

**Next Steps:**
- Hardware build session (Feb 21)
- Integration with real flight controllers
- Flight testing

## 🔗 Links

- **GitHub:** https://github.com/BrianEstime1/drone-swarm
- **INAV Documentation:** https://github.com/iNavFlight/inav
- **STM32F405 Info:** https://www.st.com/en/microcontrollers-microprocessors/stm32f405-415.html

## 👤 Author

**Brian Estime**
- Electrical Engineering Student @ HCC → UCF (Fall 2026)
- Focus: Intelligent Robotic Systems, Aerospace Engineering
- Student-Athlete: Men's Basketball Team

## 📄 License

This project is open source for educational purposes.

---

**Last Updated:** February 16, 2026
