# Panda3D Backrooms Game - Psycho Horror Experience

This is a complete conversion of the Pygame raycasting Backrooms game to Panda3D, featuring a 3D implementation with proper lighting, movement, and psycho horror elements.

## Features(WILL BE ADDED LATER)

- **3D Backrooms Environment**: Procedurally generated rooms using Perlin noise
- **Player Movement**: WASD for movement, mouse look for aiming
- **Psycho Horror Elements**: Dream zones with special effects (slow, fast, float, glitch)
- **Atmospheric Lighting**: Flickering fluorescent lighting effect
- **Dynamic UI**: Dream messages and player status display
- **Collision Detection**: Proper wall collision system

## Requirements

- Python 3.6+ (recommended: 3.11)
- Panda3D 1.10+
- You need to read the Panda3D docs for 'less error' and 'better performance' in game code

## Installation

```bash
pip install panda3d
```

## How to Run

```bash
python game.py
```

## Controls

- **WASD**: Move around
- **Mouse**: Look around (first person view)
- **ESC**: Quit the game

## Game Elements

### Movement System
- The player moves in a 3D grid-based world
- Collision detection prevents walking through walls
- Movement speed adjusts based on dream zones

### Dream Zones
- **Slow**: Reduces movement speed
- **Fast**: Increases movement speed
- **Float**: Affects vertical position
- **Glitch**: Randomly distorts player direction

### Visual Atmosphere
- Cream-colored walls reminiscent of the Backrooms
- Subtle lighting flicker for unease
- Dynamic color variations for texture
- Warm fog effect for depth

### Psycho Horror Elements
- Random dream messages appear periodically
- Glitch effects that distort reality
- Floating effect that changes vertical position
- Sanity and dream level tracking

## Assets

The game uses simple geometric shapes (planes and boxes) created programmatically, so no external asset files are required. The environment is generated procedurally using Perlin noise.
**But i will add some textures and models soon.**

## Technical Implementation (Future)

- Uses Panda3D's built-in 3D rendering pipeline
- Procedural generation for infinity-like environments
- Dream zone effects with particle systems
- Proper lighting with ambient and directional lights
- First-person camera system with mouse look
- Collision detection system
- Dynamic UI elements

## Customization

You can easily modify:
- Wall colors and textures
- World generation parameters
- Player movement speed
- Dream zone effects
- Lighting properties
- UI elements and messages

#### INFINITE STUBBORN BACKROOM GAME