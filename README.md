# Escape PRP

A 2D top-down horror survival game built with Python and Pygame. You are trapped in an abandoned educational facility (PRP). Your only tool is a flashlight, but be careful—the monsters lurking in the dark (Shadow Walkers) will only chase you if you shine your light directly on them! 

Explore the classrooms, find the exit, and survive.

## Features
- **Dynamic Flashlight Mechanics**: A polygon-based lighting system that intersects with walls.
- **Light-Sensitive AI**: Shadow Walkers freeze in the dark, but will relentlessly hunt you if illuminated.
- **Resource Management**: Collect batteries to keep your flashlight alive and MedKits to restore health.
- **Custom Tilemap Engine**: Parses Tiled (`.tmx`) files for exact geometric hitboxes, including mathematical AABB collision for rotated/diagonal walls.
- **Anti-Tunneling Physics**: Robust collision detection ensuring players and monsters cannot clip through thin walls, even at high sprint speeds.

## Controls
- **W, A, S, D**: Move around
- **Left Shift**: Sprint (Use this to outrun monsters!)
- **Mouse**: Aim your flashlight
- **R**: Restart game (if you die or win)

## Installation & Setup

1. Make sure you have Python 3 installed.
2. Clone this repository:
   ```bash
   git clone https://github.com/Ashutosh-2109/Escape_PRP.git
   cd Escape_PRP
   ```
3. Install the required dependencies:
   ```bash
   pip install pygame pytmx
   ```
4. Run the game:
   ```bash
   python src/main.py
   ```

## Development
This game uses a highly modular Pygame architecture with isolated components for the camera, items, sounds, flashlight rendering, and map loading. Maps can be easily edited and expanded using the [Tiled Map Editor](https://www.mapeditor.org/).
