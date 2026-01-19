"""
Game Engine Framework for 3D FPS Games
Provides core systems for rendering, input handling, physics, and game objects
"""

from abc import ABC, abstractmethod
import time
from enum import Enum
from typing import Dict, List, Any, Optional
import math


class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"


class Component(ABC):
    """Base class for all components"""
    def __init__(self, owner=None):
        self.owner = owner
        self.active = True
    
    @abstractmethod
    def update(self, dt: float):
        pass


class GameObject:
    """Base game object that can hold multiple components"""
    def __init__(self, name: str = "GameObject"):
        self.name = name
        self.components: List[Component] = []
        self.transform = Transform()
        self.active = True
        self.children: List['GameObject'] = []
        self.parent: Optional['GameObject'] = None
    
    def add_component(self, component: Component):
        component.owner = self
        self.components.append(component)
    
    def get_component(self, component_type):
        for comp in self.components:
            if isinstance(comp, component_type):
                return comp
        return None
    
    def remove_component(self, component_type):
        for i, comp in enumerate(self.components):
            if isinstance(comp, component_type):
                del self.components[i]
                return True
        return False
    
    def add_child(self, child: 'GameObject'):
        child.parent = self
        self.children.append(child)
    
    def update(self, dt: float):
        if not self.active:
            return
        
        for component in self.components:
            if component.active:
                component.update(dt)
        
        for child in self.children:
            child.update(dt)


class Transform:
    """Transform component for position, rotation, scale"""
    def __init__(self, position=None, rotation=None, scale=None):
        from ursina import Vec3
        self.position = position or Vec3(0, 0, 0)
        self.rotation = rotation or Vec3(0, 0, 0)  # pitch, yaw, roll
        self.scale = scale or Vec3(1, 1, 1)
    
    def translate(self, offset):
        """Translate by offset vector"""
        from ursina import Vec3
        if isinstance(offset, tuple):
            offset = Vec3(*offset)
        self.position += offset
    
    def rotate(self, rotation_offset):
        """Rotate by offset"""
        from ursina import Vec3
        if isinstance(rotation_offset, tuple):
            rotation_offset = Vec3(*rotation_offset)
        self.rotation += rotation_offset
    
    def get_forward_vector(self):
        """Get forward direction vector based on rotation"""
        from ursina import Vec3
        # Simple forward calculation based on yaw
        yaw_rad = math.radians(self.rotation.y)
        forward_x = -math.sin(yaw_rad)
        forward_z = -math.cos(yaw_rad)
        return Vec3(forward_x, 0, forward_z)


class GameSystem(ABC):
    """Base class for game systems (managers)"""
    def __init__(self, engine):
        self.engine = engine
        self.active = True
    
    @abstractmethod
    def update(self, dt: float):
        pass


class EntityManager:
    """Manages all game objects in the scene"""
    def __init__(self):
        self.game_objects: List[GameObject] = []
        self.object_map: Dict[str, GameObject] = {}
    
    def register_object(self, obj: GameObject):
        self.game_objects.append(obj)
        if obj.name in self.object_map:
            # Handle duplicate names
            counter = 1
            original_name = obj.name
            while f"{original_name}_{counter}" in self.object_map:
                counter += 1
            obj.name = f"{original_name}_{counter}"
        self.object_map[obj.name] = obj
    
    def unregister_object(self, obj: GameObject):
        if obj in self.game_objects:
            self.game_objects.remove(obj)
        if obj.name in self.object_map:
            del self.object_map[obj.name]
    
    def get_object_by_name(self, name: str) -> Optional[GameObject]:
        return self.object_map.get(name)
    
    def update_all(self, dt: float):
        for obj in self.game_objects[:]:  # Copy list to avoid modification during iteration
            if obj.active:
                obj.update(dt)
    
    def destroy_object(self, obj: GameObject):
        """Destroy and remove a game object"""
        obj.active = False
        self.unregister_object(obj)


class InputManager:
    """Handles input from keyboard, mouse, and controllers"""
    def __init__(self):
        self.keys_pressed = {}
        self.mouse_pos = (0, 0)
        self.mouse_buttons = {'left': False, 'right': False, 'middle': False}
        self.key_states = {}
        self.mouse_delta = (0, 0)
        self.last_mouse_pos = (0, 0)
    
    def update(self):
        # This would be updated with actual input from the framework
        pass
    
    def is_key_down(self, key: str) -> bool:
        return self.key_states.get(key, False)
    
    def is_key_pressed(self, key: str) -> bool:
        return self.keys_pressed.get(key, False)
    
    def is_mouse_button_down(self, button: str) -> bool:
        return self.mouse_buttons.get(button, False)


class PhysicsSystem(GameSystem):
    """Handles collision detection and physics simulation"""
    def __init__(self, engine):
        super().__init__(engine)
        self.gravity = 9.81
    
    def update(self, dt: float):
        # Update physics for all objects with rigidbody components
        pass


class Renderer:
    """Abstract renderer interface"""
    def __init__(self):
        self.camera_transform = Transform()
        self.render_queue = []
    
    def render(self, game_objects: List[GameObject]):
        # Render all game objects
        pass


class GameEngine:
    """Main game engine that orchestrates all systems"""
    def __init__(self):
        self.entity_manager = EntityManager()
        self.input_manager = InputManager()
        self.physics_system = PhysicsSystem(self)
        self.renderer = Renderer()
        
        self.systems: List[GameSystem] = [
            self.physics_system
        ]
        
        self.game_state = GameState.MENU
        self.running = False
        self.last_update_time = time.time()
        self.frame_count = 0
        self.fps = 0
        
        # Timing
        self.target_fps = 60
        self.fixed_timestep = 1.0 / 60.0
        self.accumulator = 0.0
    
    def initialize(self):
        """Initialize the game engine"""
        pass
    
    def run(self):
        """Main game loop"""
        self.running = True
        self.last_update_time = time.time()
        
        while self.running:
            current_time = time.time()
            dt = current_time - self.last_update_time
            self.last_update_time = current_time
            
            self.accumulator += dt
            
            # Process fixed timestep updates
            while self.accumulator >= self.fixed_timestep:
                self.fixed_update(self.fixed_timestep)
                self.accumulator -= self.fixed_timestep
            
            # Variable timestep updates
            self.update(dt)
            self.render()
            
            self.frame_count += 1
            if self.frame_count % 60 == 0:
                self.fps = 1.0 / dt if dt > 0 else 0
    
    def fixed_update(self, dt: float):
        """Fixed timestep update for physics and other time-sensitive systems"""
        self.physics_system.update(dt)
    
    def update(self, dt: float):
        """Variable timestep update for gameplay logic"""
        self.input_manager.update()
        
        # Update all game systems
        for system in self.systems:
            if system.active:
                system.update(dt)
        
        # Update all game objects
        self.entity_manager.update_all(dt)
    
    def render(self):
        """Render the scene"""
        game_objects = self.entity_manager.game_objects
        self.renderer.render(game_objects)
    
    def quit(self):
        """Quit the game"""
        self.running = False
    
    def change_state(self, new_state: GameState):
        """Change the game state"""
        old_state = self.game_state
        self.game_state = new_state
        print(f"Game state changed from {old_state.value} to {new_state.value}")