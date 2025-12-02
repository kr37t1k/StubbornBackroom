# Advanced Raycasting System

## Overview
The advanced raycasting system provides two different rendering implementations:
1. **Pygame Implementation** - Enhanced version of the original system with improved visuals
2. **Pyglet OpenGL Implementation** - Advanced 3D rendering using OpenGL for better performance and effects

## Features

### Enhanced Pygame Renderer
- **Better perspective correction**: More accurate wall height calculations
- **Gradient ceiling and floor**: Smoother transitions in vertical directions
- **Improved anti-aliasing**: Cleaner wall rendering with single-pixel width lines
- **Enhanced lighting effects**: Dynamic fog and color blending
- **Dream effects**: Wave patterns and flickering for atmospheric feel

### Pyglet OpenGL Renderer
- **True 3D rendering**: Direct OpenGL calls for maximum performance
- **Hardware acceleration**: Uses GPU for rendering
- **Advanced texturing capabilities**: Ready for future texture implementation
- **Better performance**: More efficient rendering pipeline
- **Cross-platform compatibility**: Works on multiple operating systems

## Implementation Details

### Advanced Raycaster Class
- Enhanced ray casting with coordinate tracking
- Improved distance calculations with perspective correction
- More detailed color palette with dream-like colors
- Dynamic effects (wave patterns, flickering)

### PygameRaycastRenderer
- Optimized rendering pipeline for pygame
- Gradient backgrounds for ceiling and floor
- Perspective-corrected wall rendering
- Enhanced lighting and fog effects

### OpenGLRaycastRenderer
- Direct OpenGL rendering for maximum performance
- Vertex-based wall rendering
- Normalized coordinate system
- Ready for advanced effects and texturing

## Usage

### Running the Game
The main game (`game.py`) now uses the advanced pygame renderer by default. You can switch to the OpenGL version by modifying the import and renderer usage.

### Running Advanced Features
To use the Pyglet OpenGL implementation, run:
```python
from advanced_raycast import run_advanced_game
run_advanced_game()
```

This will prompt you to choose between Pygame and Pyglet OpenGL implementations.

## Key Improvements

1. **Better Performance**: Optimized rendering algorithms
2. **Enhanced Visuals**: More realistic lighting and perspective
3. **Modular Design**: Separate renderer classes for easy switching
4. **Future-Ready**: Architecture ready for texture mapping and advanced effects
5. **Robust Error Handling**: Graceful fallbacks for headless environments

## Files

- `advanced_raycast.py`: Main implementation with both rendering methods
- `game.py`: Updated to use advanced pygame renderer
- `test_advanced_raycast.py`: Test script to verify functionality

## Future Enhancements

- Texture mapping for walls
- Sprite rendering for objects
- Dynamic lighting effects
- Performance optimizations
- Advanced shader support in OpenGL version