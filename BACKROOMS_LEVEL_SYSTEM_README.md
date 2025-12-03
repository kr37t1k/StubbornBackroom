# Backrooms Level System

This system provides tools for generating, editing, and loading custom levels in the Backrooms game.

## Components

### 1. Level Generator (`backrooms_level_generator.py`)

A procedural level generator that creates backrooms-style levels with:

- Rooms of various sizes
- Connecting corridors
- Doors between rooms
- Hazard zones
- Wall structures

**Usage:**
```python
from backrooms_level_generator import BackroomsLevelGenerator

# Create a generator with specific dimensions
generator = BackroomsLevelGenerator(width=100, height=100, seed=42)

# Generate a level
level_data = generator.generate_level()

# Save to file
generator.save_level_to_file("levels/my_level.json")

# Visualize as image
generator.visualize_level("level_preview.png")
```

### 2. Level Editor (`backrooms_level_editor.py`)

A GUI-based level editor built with Tkinter that allows:

- Painting different tile types (walls, floors, doors, hazards, etc.)
- Loading and saving level files
- Procedural level generation
- Level preview functionality

**Usage:**
```bash
python backrooms_level_editor.py
```

**Features:**
- Click and drag to paint tiles
- Multiple tile types available
- File operations (New, Load, Save)
- Generate procedural levels
- Preview level as image

### 3. Game Integration

The main game now supports loading custom levels:

**Command line usage:**
```bash
python launch_game.py --level levels/my_level.json
```

**Programmatic usage:**
```python
from backrooms_game import BackroomsGame

# Load custom level
game = BackroomsGame(level_file="levels/my_level.json")
game.run()
```

## Tile Types

The system supports these tile types:

- **Empty (0)**: Empty space, walkable
- **Wall (1)**: Solid wall, blocks movement
- **Floor (2)**: Walkable floor
- **Door (3)**: Passable doorway
- **Corridor (4)**: Walkable corridor
- **Room (5)**: Walkable room area
- **Hazard (6)**: Hazardous area (treated as walkable but with special effects)

## Level File Format

Level files are JSON with this structure:

```json
{
  "width": 100,
  "height": 100,
  "seed": 42,
  "map": [
    [1, 1, 1, ...],  // 2D array of tile types
    [1, 2, 2, ...],
    ...
  ],
  "rooms": [[x, y], ...],      // Coordinates of room tiles
  "doors": [[x, y], ...],      // Coordinates of door tiles
  "corridors": [[x, y], ...],  // Coordinates of corridor tiles
  "hazards": [[x, y], ...],    // Coordinates of hazard tiles
  "metadata": {
    "generated_by": "BackroomsLevelGenerator",
    "tile_types": {...}
  }
}
```

## Integration with Game

When a level file is loaded:

1. The `BackroomsWorld` class loads the level data
2. The 3D environment is generated based on the tile map
3. The player starts in the first room if available
4. Collision detection works with the loaded level structure
5. The floor and ceiling sizes adjust to fit the level dimensions

## Creating Custom Levels

### Using the Editor:
1. Run `python backrooms_level_editor.py`
2. Select tile types from the toolbar
3. Click and drag to paint on the grid
4. Use "Save" to save your level as JSON
5. Load in game with `python launch_game.py --level path/to/your_level.json`

### Using the Generator:
1. Import the generator in your code
2. Configure dimensions and seed
3. Generate and save the level
4. Load in game

## Extending the System

The system is designed to be extensible:

- Add new tile types by modifying the constants in both generator and game
- Extend the editor with new tools
- Add more complex level features in the generator
- Modify the 3D rendering in the game to support new tile types

## Dependencies

- `numpy` - for array operations
- `PIL` (Pillow) - for image visualization
- `tkinter` - for the editor GUI (usually included with Python)
- `noise` - for procedural generation in the game
- `panda3d` - for the game engine

## Testing

Run the test suite to verify all components work:
```bash
python test_level_loading.py
```