# Psycho Backrooms - Ursina Version

This is a 3D horror exploration game inspired by the Backrooms phenomenon, implemented using Ursina (Panda3D) instead of pygame. The game features psychological elements, procedural generation, and dream-like effects.

## Features

- **Procedural Backrooms Generation**: Infinite, maze-like rooms generated using hash-based algorithm
- **Psychological Effects**: Dream zones with different effects (slow, fast, glitch, panic)
- **First-Person Exploration**: Navigate through the endless backrooms
- **Dynamic Environment**: Walls, floors, ceilings, and random objects
- **Dream Messages**: Random psychological messages appear during gameplay
- **Player Stats**: Track dream level, sanity, and reality stability

## Game Mechanics

- **Movement**: WASD keys to move, mouse to look around
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
python ursina_backrooms.py
```

## Controls

- **WASD**: Move around
- **Mouse**: Look around
- **ESC**: Quit the game

## Game Elements

- **Walls**: Cream-colored walls that form the maze structure
- **Floors**: Subtle variations of yellowish-white floors
- **Ceiling**: Off-white ceiling for the backrooms
- **Furniture**: Random chairs, tables, and boxes scattered throughout
- **Lights**: Fluorescent lights that create atmosphere

## Technical Details

The game uses:
- Ursina engine (built on Panda3D) for 3D rendering
- Hash-based algorithm for procedural world generation
- First-person controller for movement
- Custom world generation system
- Dynamic UI elements

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

Enjoy exploring the endless backrooms, but remember... reality is fragile in here.
