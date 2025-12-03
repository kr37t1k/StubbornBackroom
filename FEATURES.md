# Advanced Backrooms Game Features

## Overview
This enhanced version of the backrooms game includes all the features you requested:

- **Fog**: Atmospheric fog effect for the scary backrooms experience
- **Improved Map Loading**: Better map system with multiple entity types
- **Advanced Walls and Entities**: Walls, floors, doors, and other interactive objects
- **Player Physics**: Enhanced physics for the player character
- **Advanced Map Generation**: More complex map generation with rooms, corridors, and special areas
- **Map Editor**: GUI tool for creating and editing maps
- **Optimization**: Performance improvements for older laptops

## Features in Detail

### 1. Fog System
- Implemented atmospheric fog using Panda3D's fog system
- Yellow-tinted fog for the characteristic backrooms atmosphere
- Configurable fog density in the settings
- Toggle fog with the 'F' key

### 2. Advanced Map System
- **Multiple Entity Types**: Walls, floors, ceilings, doors, and decorative objects
- **JSON Map Format**: Extended format to support entities and special features
- **Entity Management**: Proper handling of doors, interactive objects, and decorations

### 3. Player Physics
- Enhanced First Person Controller with:
  - Customizable gravity
  - Jump height adjustments
  - Improved collision detection
  - Better movement controls

### 4. Interactive Doors
- Fully functional doors that can be opened/closed
- Locked/unlocked door states
- Visual door animations
- Door placement in map generation

### 5. Advanced Map Generation
- **Maze Generation**: Classic maze algorithm with improvements
- **Room-Based Maps**: Maps with distinct rooms connected by corridors
- **Open Space Maps**: More open layouts
- **Special Rooms**: Designated areas with different properties
- **Entity Placement**: Automatic placement of decorations and objects

### 6. Map Editor
- GUI-based map editor with multiple tools
- Support for walls, paths, start/end points, doors, and entities
- Entity type selection
- Save/load functionality
- Grid-based placement for precision

### 7. Performance Optimizations
- **Reduced Render Quality**: Lower texture resolution for older hardware
- **Limited Render Distance**: Only render nearby objects
- **Frame Skipping**: Update less frequently for better performance
- **Entity Culling**: Limit number of entities in large maps
- **Optimized Updates**: Less frequent updates for non-critical systems
- **Simplified Lighting**: Reduced lighting calculations

## New Files

### Game Files
- `advanced_game.py`: Main game with all new features
- `optimized_game.py`: Performance-optimized version for older laptops

### Map Tools
- `maps/advanced_map_generator.py`: Enhanced map generator with entity support
- `maps/advanced_map_editor.py`: GUI map editor with entity placement

### Configuration
- Updated `requirements.txt` with necessary dependencies

## Controls

### In-Game Controls
- **WASD**: Move around
- **Mouse**: Look around
- **Space**: Jump
- **R**: Reset player position
- **F**: Toggle fog (in advanced version)
- **Escape**: Quit game

### Map Editor Controls
- **Tool Selection**: Choose between wall, path, start, end, door, and entity tools
- **Entity Type**: Select specific entity type when using entity tool
- **Click/Drag**: Place objects on the map
- **File Menu**: New, Open, Save, Save As

## Running the Game

### Standard Version (with all features):
```bash
python advanced_game.py
```

### Optimized Version (for older laptops):
```bash
python optimized_game.py
```

### Running the Map Generator:
```bash
python maps/advanced_map_generator.py
```

### Running the Map Editor:
```bash
python maps/advanced_map_editor.py
```

## Performance Settings

The optimized version includes several performance settings in the Config class:

- `window_size`: Reduced to 1024x576 for better performance
- `fps`: Limited to 60 FPS
- `max_entities`: Limited to 500 entities
- `render_distance`: Limited to 20 units
- `texture_quality`: Set to low
- `enable_shadows`: Disabled by default

## Map File Format

The new map format includes:

```json
{
  "width": 100,
  "height": 100,
  "seed": 12345,
  "start_pos": [1, 1],
  "end_pos": [98, 98],
  "map": [...],  // 2D grid (0=path, 1=wall, 2=door, 3=special)
  "entities": [...]  // List of entities with positions and types
}
```

## Customization

You can customize the game by modifying the `Config` class in either game file:

- Adjust fog density
- Modify player speed and sensitivity
- Change gravity and physics parameters
- Adjust performance settings
- Modify reality distortion effects