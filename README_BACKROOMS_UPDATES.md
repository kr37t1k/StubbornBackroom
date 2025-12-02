# Ursina Backrooms Game - Updates and Improvements

## Overview
This document details the improvements made to the Ursina Backrooms game to fix the issues with white screen, mouse, and keyboard controls.

## Issues Fixed

### 1. White Screen Issue
- **Problem**: Game appeared all white when starting
- **Solution**: 
  - Added proper lighting with `DirectionalLight`
  - Improved room generation with better color contrast
  - Ensured proper texture and color application to entities

### 2. Mouse Controls
- **Problem**: No mouse look functionality
- **Solution**:
  - Added `mouse.locked = True` for FPS-style controls
  - Implemented proper mouse look in the update method
  - Added sensitivity controls for smooth camera rotation
  - Added ability to toggle mouse lock with Escape key

### 3. Keyboard Controls
- **Problem**: No movement controls
- **Solution**:
  - Enhanced movement system with WASD keys
  - Added arrow key support as alternative
  - Implemented proper physics with gravity and jumping
  - Added velocity-based movement for smoother gameplay

## New Features Added

### 1. Movement System
- WASD or arrow keys for movement (forward, backward, strafe left/right)
- Spacebar for jumping
- Gravity system for realistic jumping/falling
- Speed modifiers based on room effects

### 2. Mouse Look System
- Mouse locked to center of screen for FPS controls
- Smooth camera rotation with sensitivity controls
- Vertical look clamped to prevent over-rotation
- Escape key to toggle mouse lock

### 3. Additional Controls
- Escape key to toggle mouse lock/unlock
- Support for both WASD and arrow keys

### 4. Advanced Room Generation
- Created `generate_backroom.py` with advanced features:
  - Hazard generation (water puddles, broken glass, etc.)
  - Entity spawning (shadow figures, stray people)
  - Environmental features (humidity, temperature, etc.)

## File Structure

- `ursina_backrooms.py` - Main game file with all improvements
- `generate_backroom.py` - Enhanced room generation script
- `generated_world.json` - Generated world data (created by the generator)

## How to Run

1. Install requirements: `pip install -r requirements.txt`
2. Generate the world: `python generate_backroom.py`
3. Run the game: `python ursina_backrooms.py`

## Controls

- **WASD** or **Arrow Keys**: Move character
- **Mouse**: Look around (when locked)
- **Space**: Jump
- **Escape**: Toggle mouse lock

## Technical Improvements

1. **Physics System**: Added gravity and jumping mechanics
2. **Camera System**: Proper FPS-style camera with mouse look
3. **Movement System**: Smooth movement with proper vector math
4. **Chunk Loading**: Dynamic room loading as player moves
5. **Psychological Effects**: Sanity and reality stability systems
6. **Dream Messages**: Dynamic messages appearing during gameplay

## Game Features

- Procedurally generated backrooms with varying properties
- Dream zones with special effects (slow, fast, glitch, panic)
- Furniture and lighting systems
- Sanity and reality stability tracking
- Dynamic messaging system
- Environmental storytelling elements

The game is now fully playable with proper mouse and keyboard controls in the Ursina 3D engine!