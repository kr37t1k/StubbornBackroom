# Ursina Development Guide for 3D Backrooms

## Overview

This guide explains how to develop and extend the 3D Backrooms game using the Ursina engine. Ursina is a Python game engine built on top of Panda3D that provides an easier API for creating 3D games.

## Ursina Basics

### Core Concepts
- **Entity**: The basic building block for all objects in Ursina
- **Ursina**: The main application class
- **update()**: Called every frame for game logic
- **input()**: Handles input events
- **Collider**: Enables collision detection

### Common Components
- `Vec3`: 3D vector for positions and rotations
- `color`: For coloring entities
- `Texture`: For applying textures to models
- `FirstPersonController`: Built-in first-person controller

## Game Architecture

### Main Components
1. **BackroomsGame**: Main game class inheriting from Ursina
2. **Map**: Handles maze generation and storage
3. **Config**: Game configuration settings

### Scene Setup
- `setup_scene()`: Initializes the 3D environment
- `create_floor()`: Creates the floor plane
- `create_walls_from_map()`: Builds walls based on the map data
- `create_ceiling()`: Creates the ceiling plane

## Extending the Game

### Adding New Features
```python
# Example: Adding a new entity
new_entity = Entity(
    model='cube',
    texture='textures/my_texture.png',
    position=Vec3(0, 0, 0),
    collider='box'
)
```

### Custom Controllers
Instead of using the built-in FirstPersonController, you can create custom movement:
```python
class CustomPlayer(Entity):
    def update(self):
        # Custom movement logic
        if held_keys['w']:
            self.position += Vec3(0, 0, time.dt * self.speed)
```

### Adding Effects
```python
# Visual effects
def apply_visual_distortion(self):
    # Change lighting
    self.directional_light.color = color.red
    
    # Add visual overlays or shader effects
    # (Would require custom shaders in a full implementation)
```

## Performance Considerations

### Optimization Tips
- Use `combine_parent()` to combine multiple static meshes
- Reduce texture sizes where possible
- Use `destroy()` to remove unused entities
- Limit the number of active entities

### Memory Management
- Load textures once and reuse them
- Use object pooling for frequently created/destroyed objects
- Consider using instanced rendering for repeated objects

## Troubleshooting

### Common Issues
1. **No window appears**: Ensure a display is available
2. **Controls not working**: Check that input() method is properly defined
3. **Collisions not working**: Verify colliders are properly set
4. **Performance issues**: Reduce scene complexity or optimize draw calls

### Debugging Tips
- Use `print()` statements to trace execution
- Enable FPS counter with `window.fps_counter.enabled = True`
- Use `Entity.debug = True` for collision debugging

## Advanced Features

### Shader Effects
Ursina supports custom shaders for advanced visual effects:
```python
my_shader = Shader(vertex_shader=vertex_shader_code, fragment_shader=fragment_shader_code)
my_entity.shader = my_shader
```

### Audio System
- Use `Audio()` for sound effects
- Use pygame.mixer for background music (as implemented in the game)

### Animation
- Use `lerp()` for smooth transitions
- Create custom animations with `Sequence` and `Func`

## Best Practices

1. **Keep update() efficient**: Avoid heavy calculations in update()
2. **Use proper parenting**: Group related entities under parent objects
3. **Manage resources**: Load assets once and reuse them
4. **Separate logic**: Keep game logic separate from rendering code
5. **Error handling**: Wrap potentially failing operations in try/except blocks

## Useful Resources

- [Ursina Official Documentation](https://www.ursinaengine.org/)
- [Ursina GitHub Repository](https://github.com/pokepetter/ursina)
- [Python Game Development Tutorials](https://www.ursinaengine.org/cheat_sheet.html)

## Migration Notes

This game was converted from a Panda3D implementation. Key differences:
- Entity-based system instead of NodePath hierarchy
- Built-in FirstPersonController instead of manual camera control
- Simpler texture and model loading
- Integrated input handling