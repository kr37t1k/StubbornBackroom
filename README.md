# Liminalcore Backrooms Game

Advanced 3D backrooms experience with enhanced features, debugging tools, and customization options.

## Features

### Core Game Features
- **Liminalcore Aesthetics**: Enhanced visual design with liminal space themes
- **Reality Distortion System**: Dynamic reality states that affect gameplay and visuals
- **Procedural Generation**: Advanced room-based backrooms generation
- **Entity System**: Various objects and decorations in the backrooms
- **Atmospheric Effects**: Particle systems, lighting, and fog effects

### Quality Settings
- **Low**: Optimized for older hardware
- **Normal**: Balanced performance and visuals
- **High**: Enhanced visuals with more effects
- **Ultra**: Maximum visual quality

### Debugging Features
- **FPS Counter**: Real-time performance monitoring
- **Debug Panel**: Shows reality state, performance metrics, and map info
- **Collision Visualization**: Toggle collision boxes for debugging
- **Performance Profiling**: Monitor game performance

### Map System
- **Multiple Generation Styles**: Maze, open space, room-based, liminal, chaotic
- **Entity Placement**: Various objects like chairs, tables, plants, lights, monitors
- **Door System**: Functional doors with locking mechanics
- **Special Rooms**: Unique areas with different properties

### Map Editors
- **3D Map Editor**: Visual 3D map creation tool
- **Debug Map Editor**: Advanced debugging and editing capabilities
- **Map Generator**: Procedural map generation with customization

## Controls

### Main Game
- **WASD**: Move
- **Mouse**: Look around
- **Space**: Jump
- **F1-F4**: Quality levels (Low, Normal, High, Ultra)
- **F5-F10**: Debug toggles
- **Tab**: Reality distortion view
- **M**: Switch maps
- **E**: Open 3D Map Editor
- **Esc**: Quit

### Map Editors
- **Left Click**: Place/remove objects
- **Right Click**: Context menu (set start/end, get info, etc.)
- **Tool Selection**: Choose different editing tools
- **Entity Types**: Select from various entity types to place

## Files

### Main Game
- `liminalcore_backrooms_game.py`: Main game implementation with all enhanced features

### Map Editors
- `liminalcore_3d_map_editor.py`: Standalone 3D map editor
- `liminalcore_debug_map_editor.py`: Advanced debugging map editor
- `liminalcore_map_generator.py`: Procedural map generator with customization

### Configuration
- `liminalcore_config.json`: Game settings, quality levels, and optimization options

### Original Files
- `stubborn_backrooms_game.py`: Original backrooms game
- `maps/`: Directory containing map files and editors

## Installation

1. Ensure you have Python 3.7+ installed
2. Install required dependencies:
   ```bash
   pip install ursina
   ```
3. Run the main game:
   ```bash
   python liminalcore_backrooms_game.py
   ```

## Map Editor Usage

### 3D Map Editor
1. Run `python liminalcore_3d_map_editor.py`
2. Use WASD to navigate the 3D space
3. Select different tools to build your map
4. Save your map for use in the main game

### Debug Map Editor
1. Run `python liminalcore_debug_map_editor.py`
2. Use the toolbar to select tools
3. Click and drag to modify the map
4. Right-click for additional options
5. Generate maps with different styles and parameters

## Configuration

Edit `liminalcore_config.json` to customize:
- Quality settings for different performance levels
- Reality state parameters
- Map generation settings
- Optimization options
- Audio and control settings

## Reality States

The game features four reality states that dynamically change the environment:

1. **Stable**: Normal backrooms experience
2. **Distorted**: Subtle visual and audio distortions
3. **Liminal**: Enhanced atmospheric effects and reality distortion
4. **Chaotic**: Maximum distortion with unpredictable behavior

The reality state changes based on player movement and time spent in one location.

## Optimization

The game includes several optimization features:
- Dynamic Level of Detail (LOD)
- Frustum culling
- Texture streaming
- Object pooling
- Configurable quality settings

## Custom Maps

Place custom map files in the `maps/` directory in JSON format. The game will automatically detect and allow switching between available maps.

## Development

The project is structured to allow easy expansion:
- Modular design with separate systems
- Configurable parameters
- Extensible entity system
- Multiple generation algorithms
- Debugging tools for development