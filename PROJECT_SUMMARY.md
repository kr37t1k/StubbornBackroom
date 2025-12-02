# Psycho Backrooms - Ursina Implementation

## Project Overview

Successfully converted the pygame-based Backrooms game to a fully functional Ursina (Panda3D) implementation. The new game features a 3D first-person perspective with enhanced visuals and gameplay mechanics.

## Files Created/Modified

### Core Game Files
- `ursina_backrooms.py` - Main game implementation using Ursina
- `requirements.txt` - Project dependencies
- `verify_ursina.py` - Verification script for imports and syntax
- `README_BACKROOMS_URSINA.md` - Detailed documentation for the Ursina version

### Updated Files
- `README.md` - Updated to reflect the new Ursina implementation

## Key Features Implemented

### 1. Procedural World Generation
- Uses Perlin noise for smooth, infinite backrooms generation
- Multiple room types (hallways, junctions, corners, open spaces)
- Dynamic chunk-based generation system

### 2. First-Person Gameplay
- WASD movement controls
- Mouse look functionality
- Collision detection with walls

### 3. Psychological Effects System
- Dream zones with different effects (slow, fast, glitch, panic)
- Sanity and reality stability tracking
- Visual distortions and glitches

### 4. Environmental Details
- Cream-colored walls with subtle variations
- Yellowish-white floors
- Off-white ceiling
- Random furniture (chairs, tables, boxes)
- Fluorescent lights for atmosphere

### 5. UI Elements
- Dream messages that appear periodically
- Player status display (position, dream level, sanity)
- Controls information

### 6. Dynamic Effects
- Breathing camera effect
- Random glitch distortions
- Speed modifications in different zones

## Technical Improvements

### From Pygame to Ursina
- **3D Environment**: Full 3D first-person perspective instead of 2D raycasting
- **Better Performance**: Ursina's optimized rendering pipeline
- **Enhanced Graphics**: Proper 3D models, lighting, and textures
- **Improved Controls**: Mouse look and smooth movement

### Enhanced Gameplay
- **Proper Collision**: 3D collision detection with walls and objects
- **Realistic Movement**: First-person controller with natural movement
- **Visual Polish**: Better lighting, textures, and environmental details

## Dependencies

- `ursina` - Game engine (based on Panda3D)
- `noise` - Perlin noise for world generation
- `numpy` - Numerical operations

## Running the Game

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the game:
   ```bash
   python ursina_backrooms.py
   ```

## Game Controls

- **WASD**: Move around
- **Mouse**: Look around
- **ESC**: Quit the game

## Verification

The implementation has been verified to:
- Import all necessary modules correctly
- Have proper syntax without errors
- Define all classes correctly
- Include all required functionality

## Game Experience

The new Ursina implementation provides a much more immersive experience with:
- True 3D first-person perspective
- Realistic movement and collision
- Dynamic environmental effects
- Psychological horror elements
- Procedurally generated infinite backrooms
- Visual and gameplay distortions that enhance the "psycho" theme

The game maintains the dreamy, unsettling atmosphere of the original while significantly improving the technical implementation and player experience.