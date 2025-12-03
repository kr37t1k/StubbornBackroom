# 3D Backrooms Python Prototype

Welcome to the 3D Backrooms Python 3.11 Prototype - "StubbornBackroom: Psycho Dream"

## Project Overview

This project is a 3D backrooms exploration game built with Panda3D, featuring:
- First-person exploration in an infinite maze-like environment
- Reality distortion system that affects the player's perception
- Procedural maze generation
- GUI map editor and generator tools
- Atmospheric audio system

## Project Structure

```
/workspace/
├── game.py                    # Main 3D backrooms game
├── maps/                      # Map-related files
│   ├── map_generator.py       # GUI tool for generating maze maps
│   ├── map_editor.py          # GUI tool for editing maps
│   └── generated_map.json     # Default generated map
├── textures/                  # Game textures
│   ├── floor_texture.png      # Floor texture
│   └── wall_texture.png       # Wall texture
├── audio/                     # Audio files
│   └── atomiste.mp3           # Background music
├── 3d_models/                 # 3D models
│   └── model.blend            # Blender model file
└── GUIDE_PANDA3D.md           # Panda3D development guide
```

## How to Run

### Prerequisites
- Python 3.11+
- Panda3D library

### Running the Game
```bash
# Install dependencies
pip install panda3d

# Run the main game
python game.py
```

> **Note**: The game requires a display to run. In headless environments, you may need to use X11 forwarding or a virtual display.

### Running the Map Generator
```bash
# Generate a new map interactively
python maps/map_generator.py
```

### Running the Map Editor
```bash
# Open the GUI map editor
python maps/map_editor.py
```

## Game Controls

- **W/S/A/D**: Move forward/backward/left/right
- **Mouse**: Look around (movement follows mouse direction)
- **Space**: Jump
- **Right Mouse Button**: Toggle mouse cursor visibility
- **Escape**: Exit the game

## Features

### Reality Distortion System
- Reality stability decreases over time in isolation
- Visual effects change as reality becomes more unstable
- Player's perception is altered based on psychological state

### Map System
- Procedurally generated mazes
- JSON-based map storage
- GUI editor for custom maps
- Multiple generation algorithms (maze, open space, room-based)

### Audio
- Background music from the `audio/` directory
- Dynamic audio system for atmospheric effects

## Customization

### Adding New Maps
1. Use `maps/map_generator.py` to create new procedural maps
2. Use `maps/map_editor.py` to create custom maps
3. Place JSON map files in the `maps/` directory

### Textures and Assets
- Add new textures to the `textures/` directory
- Modify the game to use new textures in the `create_floor()` and `create_walls_from_map()` functions

## Development Notes

The game uses the Panda3D engine and follows these key concepts:
- First-person camera with mouse look
- Collision detection with walls
- Procedural content generation
- Dynamic lighting and atmospheric effects
- Reality distortion system for psychological horror elements

## Troubleshooting

- If the game fails to start, ensure Panda3D is properly installed
- In headless environments, the game won't display a window
- Make sure all asset files exist in their respective directories.