#!/usr/bin/env python3
"""
Standalone 3D Map Editor for Liminalcore Backrooms Game
Visual editor for creating and modifying backrooms maps in 3D space
"""

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import json
import os
from enum import Enum


class EditorMode(Enum):
    BUILD = 0
    EDIT = 1
    PAINT = 2
    ENTITY = 3


class MapEditor3D:
    def __init__(self):
        # Initialize Ursina app
        self.app = Ursina()
        
        # Editor state
        self.mode = EditorMode.BUILD
        self.current_tool = "wall"  # wall, floor, ceiling, door, entity
        self.current_entity_type = "chair"
        self.is_running = True
        
        # Map data
        self.map_data = {
            "width": 20,
            "height": 20,
            "seed": 42,
            "start_pos": [1, 1],
            "end_pos": [18, 18],
            "map": [],
            "entities": []
        }
        self.grid_entities = []
        self.entity_objects = []
        self.room_size = 5
        self.wall_height = 4
        
        # Create initial empty map
        self.create_empty_map()
        
        # Create UI
        self.create_ui()
        
        # Set up scene
        self.setup_scene()
        
        # Bind input
        self.bind_input()
    
    def create_empty_map(self):
        """Create an empty map grid"""
        self.map_data["map"] = [[0 for _ in range(self.map_data["width"])] for _ in range(self.map_data["height"])]
        
        # Create border walls
        for x in range(self.map_data["width"]):
            self.map_data["map"][0][x] = 1  # Top border
            self.map_data["map"][self.map_data["height"]-1][x] = 1  # Bottom border
        for y in range(self.map_data["height"]):
            self.map_data["map"][y][0] = 1  # Left border
            self.map_data["map"][y][self.map_data["width"]-1] = 1  # Right border
        
        # Clear existing entities
        for entity in self.grid_entities:
            destroy(entity)
        for entity in self.entity_objects:
            destroy(entity)
        
        self.grid_entities = []
        self.entity_objects = []
        
        # Generate the visual map
        self.generate_visual_map()
    
    def generate_visual_map(self):
        """Generate the visual representation of the map"""
        # Clear existing grid entities
        for entity in self.grid_entities:
            destroy(entity)
        self.grid_entities = []
        
        # Create grid representation
        for y in range(self.map_data["height"]):
            for x in range(self.map_data["width"]):
                cell_type = self.map_data["map"][y][x]
                
                # Create floor
                floor_y = 0
                if cell_type == 1:  # Wall
                    floor_color = color.gray
                elif cell_type == 2:  # Door
                    floor_color = color.brown
                elif cell_type == 3:  # Special
                    floor_color = color.orange
                else:  # Path
                    floor_color = color.white
                
                floor = Entity(
                    model='plane',
                    scale=(self.room_size, 1, self.room_size),
                    position=Vec3(x * self.room_size, floor_y, y * self.room_size),
                    color=floor_color,
                    collider='box',
                    parent=scene
                )
                self.grid_entities.append(floor)
                
                # Create walls where needed
                if cell_type == 1:  # Wall
                    wall = Entity(
                        model='cube',
                        scale=(self.room_size, self.wall_height, 0.5),
                        position=Vec3(x * self.room_size, self.wall_height/2, y * self.room_size + self.room_size/2),
                        color=color.gray,
                        collider='box',
                        parent=scene
                    )
                    self.grid_entities.append(wall)
                
                # Create door where needed
                elif cell_type == 2:  # Door
                    door = Entity(
                        model='cube',
                        scale=(self.room_size*0.8, self.wall_height*0.8, 0.3),
                        position=Vec3(x * self.room_size, self.wall_height/2, y * self.room_size),
                        color=color.brown,
                        collider='box',
                        parent=scene
                    )
                    self.grid_entities.append(door)
        
        # Create entities
        self.create_entity_objects()
    
    def create_entity_objects(self):
        """Create visual representations of entities"""
        for entity in self.entity_objects:
            destroy(entity)
        self.entity_objects = []
        
        for entity_data in self.map_data["entities"]:
            x = entity_data["x"]
            z = entity_data["z"]
            y = entity_data.get("y", 0)
            entity_type = entity_data["type"]
            
            if entity_type == "chair":
                entity_obj = Entity(
                    model='cube',
                    scale=(0.8, 0.8, 0.8),
                    position=Vec3(x * self.room_size, y + 0.4, z * self.room_size),
                    color=color.blue,
                    collider='box',
                    parent=scene
                )
            elif entity_type == "table":
                entity_obj = Entity(
                    model='cube',
                    scale=(1.2, 0.2, 1.0),
                    position=Vec3(x * self.room_size, y + 0.1, z * self.room_size),
                    color=color.brown,
                    collider='box',
                    parent=scene
                )
            elif entity_type == "plant":
                entity_obj = Entity(
                    model='cube',
                    scale=(0.5, 1.0, 0.5),
                    position=Vec3(x * self.room_size, y + 0.5, z * self.room_size),
                    color=color.green,
                    collider='box',
                    parent=scene
                )
            elif entity_type == "light":
                entity_obj = Entity(
                    model='cube',
                    scale=(0.3, 0.1, 0.3),
                    position=Vec3(x * self.room_size, y + 2.0, z * self.room_size),
                    color=color.yellow,
                    unlit=True,
                    collider='box',
                    parent=scene
                )
            elif entity_type == "door":
                entity_obj = Entity(
                    model='cube',
                    scale=(0.8, self.wall_height*0.9, 0.3),
                    position=Vec3(x * self.room_size, y + self.wall_height/2, z * self.room_size),
                    color=color.orange,
                    collider='box',
                    parent=scene
                )
            else:
                # Default entity
                entity_obj = Entity(
                    model='cube',
                    scale=(0.6, 0.6, 0.6),
                    position=Vec3(x * self.room_size, y + 0.3, z * self.room_size),
                    color=color.red,
                    collider='box',
                    parent=scene
                )
            
            self.entity_objects.append(entity_obj)
    
    def setup_scene(self):
        """Set up the 3D scene"""
        # Lighting
        DirectionalLight(parent=scene, y=15, z=3, rotation_x=30, shadows=True)
        
        # Sky
        Sky()
        
        # Create a first-person controller for navigation
        self.editor_camera = FirstPersonController(
            position=(self.map_data["width"] * self.room_size / 2, 10, self.map_data["height"] * self.room_size / 2 - 20),
            speed=10
        )
        
        # Set background color
        scene.background_color = color.gray
    
    def create_ui(self):
        """Create the editor UI"""
        # Mode selection buttons
        self.mode_buttons = []
        
        # Build mode button
        build_btn = Button(
            text='Build Mode',
            position=window.top_left + Vec2(0.1, -0.05),
            scale=(0.15, 0.05),
            color=color.blue
        )
        build_btn.on_click = lambda: self.set_mode(EditorMode.BUILD)
        self.mode_buttons.append(build_btn)
        
        # Edit mode button
        edit_btn = Button(
            text='Edit Mode',
            position=window.top_left + Vec2(0.1, -0.12),
            scale=(0.15, 0.05),
            color=color.green
        )
        edit_btn.on_click = lambda: self.set_mode(EditorMode.EDIT)
        self.mode_buttons.append(edit_btn)
        
        # Entity mode button
        entity_btn = Button(
            text='Entity Mode',
            position=window.top_left + Vec2(0.1, -0.19),
            scale=(0.15, 0.05),
            color=color.orange
        )
        entity_btn.on_click = lambda: self.set_mode(EditorMode.ENTITY)
        self.mode_buttons.append(entity_btn)
        
        # Tool selection based on mode
        self.tool_label = Text(
            text='Current Tool: Wall',
            position=window.top_left + Vec2(0.3, -0.05),
            scale=1.5,
            color=color.white
        )
        
        # File operations
        save_btn = Button(
            text='Save Map',
            position=window.top_right + Vec2(-0.15, -0.05),
            scale=(0.12, 0.05),
            color=color.green
        )
        save_btn.on_click = self.save_map
        
        load_btn = Button(
            text='Load Map',
            position=window.top_right + Vec2(-0.15, -0.12),
            scale=(0.12, 0.05),
            color=color.blue
        )
        load_btn.on_click = self.load_map
        
        new_btn = Button(
            text='New Map',
            position=window.top_right + Vec2(-0.15, -0.19),
            scale=(0.12, 0.05),
            color=color.red
        )
        new_btn.on_click = self.create_empty_map
        
        # Entity type selector (visible only in entity mode)
        self.entity_selector = Slider(
            min=0,
            max=4,
            default=0,
            position=window.top_left + Vec2(0.3, -0.12),
            scale=(0.2, 0.02),
            dynamic=True
        )
        self.entity_selector.on_value_changed = self.on_entity_type_change
        
        self.entity_type_text = Text(
            text='Entity: Chair',
            position=window.top_left + Vec2(0.3, -0.15),
            scale=1.2,
            color=color.white
        )
        
        # Update UI visibility
        self.update_ui_visibility()
    
    def update_ui_visibility(self):
        """Update UI element visibility based on current mode"""
        if self.mode == EditorMode.ENTITY:
            self.entity_selector.enabled = True
            self.entity_type_text.enabled = True
        else:
            self.entity_selector.enabled = False
            self.entity_type_text.enabled = False
    
    def set_mode(self, mode):
        """Set the current editor mode"""
        self.mode = mode
        
        # Update UI
        mode_names = {
            EditorMode.BUILD: "Build",
            EditorMode.EDIT: "Edit", 
            EditorMode.PAINT: "Paint",
            EditorMode.ENTITY: "Entity"
        }
        self.tool_label.text = f'Editor Mode: {mode_names[mode]}'
        
        self.update_ui_visibility()
    
    def on_entity_type_change(self):
        """Handle entity type change"""
        entity_types = ["chair", "table", "plant", "light", "door"]
        idx = int(self.entity_selector.value)
        if 0 <= idx < len(entity_types):
            self.current_entity_type = entity_types[idx]
            self.entity_type_text.text = f'Entity: {self.current_entity_type.capitalize()}'
    
    def bind_input(self):
        """Bind input events"""
        # Raycast for object placement
        def input_handler(key):
            if key == 'left mouse down':
                self.handle_mouse_click()
            elif key == 'right mouse down':
                self.handle_right_click()
            elif key == 'escape':
                self.app.quit()
            elif key == 'f1':
                # Toggle between build modes
                modes = list(EditorMode)
                current_idx = modes.index(self.mode)
                next_idx = (current_idx + 1) % len(modes)
                self.set_mode(modes[next_idx])
        
        self.app.input_handler = input_handler
    
    def handle_mouse_click(self):
        """Handle left mouse click for placing objects"""
        # Raycast from camera
        hit_info = raycast(self.editor_camera.position, self.editor_camera.forward, distance=100)
        
        if hit_info.entity:
            # Find the grid position
            grid_x = round(hit_info.entity.x / self.room_size)
            grid_z = round(hit_info.entity.z / self.room_size)
            
            if self.mode == EditorMode.BUILD:
                # Toggle wall/floor based on current tool
                if 0 <= grid_x < self.map_data["width"] and 0 <= grid_z < self.map_data["height"]:
                    if self.current_tool == "wall":
                        self.map_data["map"][grid_z][grid_x] = 1
                    elif self.current_tool == "door":
                        self.map_data["map"][grid_z][grid_x] = 2
                    elif self.current_tool == "special":
                        self.map_data["map"][grid_z][grid_x] = 3
                    else:  # path/floor
                        self.map_data["map"][grid_z][grid_x] = 0
                    
                    # Regenerate visual map
                    self.generate_visual_map()
            
            elif self.mode == EditorMode.ENTITY:
                # Add entity at this position
                if 0 <= grid_x < self.map_data["width"] and 0 <= grid_z < self.map_data["height"]:
                    # Check if there's already an entity at this position
                    existing = None
                    for i, entity in enumerate(self.map_data["entities"]):
                        if int(entity["x"]) == grid_x and int(entity["z"]) == grid_z:
                            existing = i
                            break
                    
                    if existing is not None:
                        # Remove existing entity
                        del self.map_data["entities"][existing]
                    else:
                        # Add new entity
                        self.map_data["entities"].append({
                            "type": self.current_entity_type,
                            "x": float(grid_x),
                            "y": 0.0,
                            "z": float(grid_z)
                        })
                    
                    # Regenerate entity objects
                    self.create_entity_objects()
    
    def handle_right_click(self):
        """Handle right mouse click for removing objects"""
        # Raycast from camera
        hit_info = raycast(self.editor_camera.position, self.editor_camera.forward, distance=100)
        
        if hit_info.entity:
            # Find the grid position
            grid_x = round(hit_info.entity.x / self.room_size)
            grid_z = round(hit_info.entity.z / self.room_size)
            
            if 0 <= grid_x < self.map_data["width"] and 0 <= grid_z < self.map_data["height"]:
                # Set to path/floor
                self.map_data["map"][grid_z][grid_x] = 0
                
                # Regenerate visual map
                self.generate_visual_map()
    
    def save_map(self):
        """Save the current map to a file"""
        # Create maps directory if it doesn't exist
        if not os.path.exists("maps"):
            os.makedirs("maps")
        
        # Default filename
        filename = f"maps/custom_map_{self.map_data['width']}x{self.map_data['height']}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.map_data, f, indent=2)
            print(f"Map saved to {filename}")
        except Exception as e:
            print(f"Error saving map: {e}")
    
    def load_map(self):
        """Load a map from a file"""
        # For simplicity, we'll load a default map
        # In a full implementation, this would open a file dialog
        filename = "maps/first.json"  # Default map file
        
        try:
            with open(filename, 'r') as f:
                loaded_data = json.load(f)
            
            # Update map data
            self.map_data = loaded_data
            self.map_data.setdefault("entities", [])  # Add entities if missing
            
            # Regenerate visual map
            self.generate_visual_map()
            print(f"Map loaded from {filename}")
        except FileNotFoundError:
            print(f"Map file {filename} not found, creating empty map")
            self.create_empty_map()
        except Exception as e:
            print(f"Error loading map: {e}")
            self.create_empty_map()
    
    def run(self):
        """Run the editor"""
        print("3D Map Editor Started!")
        print("Controls:")
        print("- WASD: Move")
        print("- Mouse: Look around")
        print("- Left Click: Place object/entity")
        print("- Right Click: Remove object")
        print("- F1: Cycle through editor modes")
        print("- ESC: Quit")
        print()
        print("Editor Modes:")
        print("- Build: Place/remove walls, doors, etc.")
        print("- Edit: Modify existing structures")
        print("- Entity: Place/remove entities")
        
        self.app.run()


if __name__ == "__main__":
    editor = MapEditor3D()
    editor.run()