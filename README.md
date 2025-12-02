# StubbornBackroom - Psycho Cube

This is a 3D *horror* exploration game inspired by the `Backrooms` phenomenon, implemented using Ursina (Panda3D) instead of pygame. The game features psychological elements, procedural generation, and dream-like effects.

## Features

- **Procedural Backrooms Generation**: Infinite, maze-like ~~rooms~~ generated using hash-based algorithm
- **Psychological Effects**: Dream zones with different effects (slow, fast, glitch, panic)
- **First-Person Exploration**: Navigate through the endless backrooms with full mouse and keyboard controls
- **Dynamic Environment**: Walls, floors, ceilings, and random objects
- **Dream Messages**: Random psychological messages appear during gameplay
- **Player Stats**: Track dream level, sanity, and reality __stability__
- **Advanced Room Generation**: Hazards, entities, and environmental features

## Game Mechanics

- **Movement**: WASD keys or arrow keys to move, mouse to look around, spacebar to jump
- **Mouse Look**: Lock/unlock mouse with escape key
- **Dream Zones**: Special areas that affect player speed, sanity, and perception
- **Sanity System**: Your mental state degrades in certain areas
- **Visual Effects**: Breathing effect, glitches, and environmental distortions

## Installation

To run this game, you'll need Python 3.7+ and the following dependencies:

```bash
pip install ursina
```

Or install from requirements.txt:
```bash
pip install -r requirements.txt
```

## Running the Game

```bash
# First generate the world
python generate_backroom.py

# Then run the game
python ursina_backrooms.py
```

## Controls

- **WASD** or **Arrow Keys**: Move around
- **Mouse**: Look around (when locked)
- **Space**: Jump
- **Escape**: Toggle mouse lock/unlock
- **ESC**: Quit the game

## Game Elements

- **Walls**: Cream-colored walls that form the maze structure
- **Floors**: Subtle variations of yellowish-white floors
- **Ceiling**: Off-white ceiling for the backrooms
- **Furniture**: Random chairs, tables, and boxes scattered throughout
- **Lights**: Fluorescent lights that create atmosphere
- **Hazards**: Water puddles, broken glass, strange sounds
- **Entities**: Shadow figures, stray people, unknown objects

## Technical Details

The game uses:
- Ursina engine (built on Panda3D) for 3D rendering
- Hash-based algorithm for procedural world generation
- First-person controller with gravity and jumping mechanics
- Chunk-based generation for performance
- Dynamic UI elements
- Advanced psychological effect systems

## Files

- `ursina_backrooms.py` - Main game implementation with mouse/keyboard controls
- `generate_backroom.py` - Advanced room generation script
- `backroom_generator.py` - Original room generation script
- `generated_world.json` - Generated world data file

## Psycho Elements

The game includes various psychological effects:
- **Slow Zones**: Reduce player movement speed
- **Fast Zones**: Increase player movement speed
- **Glitch Zones**: Cause visual distortions and disorientation
- **Panic Zones**: Reduce sanity and cause visual/audio distortions
- **Dream Messages**: Random text that appears to unnerve the player

## World Generation

The backrooms world is procedurally generated using:
- Hash-based algorithm for consistent room types
- Chunk-based generation for performance
- Multiple room types (hallways, junctions, corners, open spaces)
- Dream zones with special effects scattered throughout
- Advanced features like hazards and entities

Enjoy exploring the endless backrooms, but remember... reality is fragile in here.
