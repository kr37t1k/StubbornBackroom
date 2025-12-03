# Backrooms Game - Panda3D Implementation

This is a complete Panda3D implementation of the Backrooms game based on the GUIDE_PANDA3D.md with full OOP design, mouse/keyboard controls, and camera movement.

## Features

### Player Controls
- **WASD**: 8-direction movement (forward, backward, strafe left/right)
- **Mouse**: Look around (click to lock/unlock mouse cursor)
- **Space**: Jump
- **ESC**: Quit game

### Game Systems
- **OOP Design**: Fully object-oriented architecture with separate classes for world, player, lighting, and game logic
- **Procedural World Generation**: Uses Perlin noise to generate infinite Backrooms-style environment
- **Custom Level System**: Generate or design your own levels using the level editor
- **Atmospheric Lighting**: Dynamic lighting system with player flashlight and flickering ambient lights
- **Psychological Elements**: Sanity system that affects gameplay and reality stability
- **Physics**: Gravity, collision detection, and movement physics

### Technical Implementation
- **FPS-style Camera**: First-person perspective with mouse look controls
- **3D Environment**: Procedurally generated walls, floors, and ceilings
- **Performance Optimized**: Uses Panda3D's CardMaker for efficient geometry
- **Texture Support**: Loads textures from the textures/ folder if available
- **UI Elements**: Real-time display of player position and sanity

## Architecture

### Classes
- `BackroomsWorld`: Procedural world generation system
- `PlayerController`: Handles movement, input, and psychological state
- `AtmosphericLighting`: Dynamic lighting system
- `BackroomsGame`: Main game class inheriting from ShowBase

### Game Loop
1. Handles mouse input for camera rotation
2. Processes keyboard input for movement
3. Updates player position with physics
4. Updates lighting based on player position
5. Updates camera to follow player
6. Updates UI elements

## Files

- `backrooms_game.py`: Main game implementation
- `launch_game.py`: Launcher script to run the game
- `backrooms_level_generator.py`: Procedural level generator
- `backrooms_level_editor.py`: GUI-based level editor
- `test_level_loading.py`: Test suite for level system
- `textures/`: Folder containing texture files (optional)
- `audio/`: Folder containing audio files (optional)

## Running the Game

```bash
python launch_game.py
```

### Loading Custom Levels

```bash
# Load a specific level file
python launch_game.py --level levels/my_custom_level.json

# Generate a level first, then load it
python backrooms_level_generator.py
python launch_game.py --level levels/generated_level.json
```

## Customization

The game can be easily extended with:
- New world generation algorithms
- Additional psychological effects
- Enemy/hallucination systems
- Inventory and interaction systems
- Sound and music systems
- Save/load functionality

## Dependencies

- Panda3D (1.10.15 or higher)
- noise (1.2.2 or higher)

Install with: `pip install -r requirements.txt`

## Design Philosophy

Based on the GUIDE_PANDA3D.md, this implementation follows:
- Core Panda3D architecture principles
- Horror & loneliness aesthetic implementation
- Schizophrenic reality distortion concepts
- Performance optimization for infinite worlds
- Psychological player controller design