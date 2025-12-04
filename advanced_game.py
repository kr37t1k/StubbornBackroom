#!/usr/bin/env python3
# Backrooms Horror Escape Game
# A terrifying 3D Backrooms experience with escape objectives

import random
import sys
import time
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
import json
import os


app = Ursina()

# Seed for reproducible randomization
random.seed(0)
Entity.default_shader = lit_with_shadows_shader

# Backrooms-specific variables
backrooms_timer = 0
sanity = 100
sanity_decrease_rate = 0.1
escape_objectives = []
current_objective = 0
game_over = False
vignette = None

# Load map data
def load_map(map_path):
    """Load map from JSON file with walls, floor, and other entities"""
    if os.path.exists(map_path):
        with open(map_path, 'r') as f:
            return json.load(f)
    else:
        print(f"Map file not found: {map_path}")
        # Return a default Backrooms map
        return {
            "width": 20,
            "height": 20,
            "map": [[1 if (x == 0 or x == 19 or y == 0 or y == 19) else 0 for x in range(20)] for y in range(20)],
            "start_pos": [1, 1],
            "end_pos": [18, 18],
            "objectives": [{"type": "exit", "x": 18, "z": 18, "description": "Find the exit"}]
        }

# Load the map
map_data = load_map("./maps/first.json")

# Create floor based on map dimensions
map_width = map_data["width"]
map_height = map_data["height"]
floor = Entity(
    model='plane', 
    collider='box', 
    scale=max(map_width, map_height) * 2, 
    texture='textures/backrooms_floor.jpg', 
    texture_scale=(4, 4),
    rotation_x=90,
    y=0,
    color=color.rgb(200, 190, 150)  # Yellowish tone for Backrooms
)

# Create walls from map data
for y in range(map_height):
    for x in range(map_width):
        if map_data["map"][y][x] == 1:  # Wall
            wall = Entity(
                model='cube',
                texture='textures/backrooms_wall.jpg',
                texture_scale=(2, 1),
                scale=(1, 3, 1),
                x=x,
                y=1.5,
                z=y,
                color=color.rgb(200, 190, 150),  # Yellowish tone for Backrooms
                collider='box'
            )

# Create ceiling
ceiling = Entity(
    model='plane',
    texture='textures/backrooms_ceiling.jpg',
    texture_scale=(4, 4),
    scale=max(map_width, map_height) * 2,
    rotation_x=-90,
    y=3,
    color=color.rgb(200, 190, 150)  # Yellowish tone for Backrooms
)

# Add flickering fluorescent lights to ceiling
for y in range(0, map_height, 3):
    for x in range(0, map_width, 3):
        if random.random() > 0.7:  # Only place lights in some spots
            light_panel = Entity(
                model='cube',
                texture='textures/fluorescent_light.png',
                scale=(1, 0.1, 1),
                x=x,
                y=2.95,
                z=y,
                color=color.rgb(255, 255, 200),
                parent=ceiling
            )
            # Make some lights flicker
            if random.random() > 0.5:
                light_panel.original_color = light_panel.color
                light_panel.flicker_state = True
                light_panel.flicker_timer = 0

# Editor camera for debugging
editor_camera = EditorCamera(enabled=False, ignore_paused=True)

# Create player with FirstPersonController
start_pos = map_data["start_pos"]
player = FirstPersonController(model='cube', x=start_pos[0], z=start_pos[1], y=1.5, color=color.rgb(100, 100, 100), origin_y=-.5, speed=5, collider='box')  # Slower movement for tension
player.collider = BoxCollider(player, Vec3(0,1,0), Vec3(1,2,1))

# Create flashlight for the player
flashlight = Entity(model='point_light', parent=camera, position=(0,0,0), color=color.rgb(255, 255, 200), intensity=1.5)

# Create a parent entity for interactive objects
interactive_parent = Entity()
mouse.traverse_target = interactive_parent

# Add Backrooms-style environmental props
for i in range(10):
    x = random.uniform(2, map_width-2)
    z = random.uniform(2, map_height-2)
    # Make sure the position is not a wall
    map_x, map_z = int(x), int(z)
    if 0 <= map_x < map_width and 0 <= map_z < map_height and map_data["map"][map_z][map_x] == 0:
        prop_type = random.choice(['chair', 'table', 'box'])
        if prop_type == 'chair':
            chair = Entity(
                model='cube', 
                origin_y=-.5, 
                scale=(0.8, 1.2, 0.8), 
                texture='textures/chair_texture.jpg', 
                x=x,
                z=z,
                y=0.6,
                collider='box',
                color=color.rgb(180, 170, 140)
            )
        elif prop_type == 'table':
            table = Entity(
                model='cube', 
                origin_y=-.5, 
                scale=(1.5, 0.8, 1), 
                texture='textures/table_texture.jpg', 
                x=x,
                z=z,
                y=0.4,
                collider='box',
                color=color.rgb(190, 180, 150)
            )
        else:  # box
            box = Entity(
                model='cube', 
                origin_y=-.5, 
                scale=(1, 1, 1), 
                texture='textures/cardboard_box.jpg', 
                x=x,
                z=z,
                y=0.5,
                collider='box',
                color=color.rgb(200, 190, 160)
            )

# Backrooms update function
def update():
    global backrooms_timer, sanity, game_over
    
    if game_over:
        return
    
    # Update timer
    backrooms_timer += time.dt
    
    # Decrease sanity over time
    sanity = max(0, sanity - sanity_decrease_rate * time.dt)
    
    # Update flickering lights
    for entity in ceiling.children:
        if hasattr(entity, 'flicker_state'):
            entity.flicker_timer += time.dt
            if entity.flicker_timer > 0.1:  # Flicker interval
                entity.flicker_timer = 0
                if entity.flicker_state:
                    entity.color = color.random.color()
                    entity.intensity = random.uniform(0.5, 2.0)
                else:
                    entity.color = entity.original_color
                    entity.intensity = 1.0
                entity.flicker_state = not entity.flicker_state
    
    # Add visual effects based on sanity
    update_sanity_effects()
    
    # Check win condition
    if current_objective >= len(map_data.get("objectives", [])):
        display_message("You escaped the Backrooms!", duration=5)
        application.quit()

def input(key):
    global game_over
    if key == 'escape':
        application.quit()
        sys.exit()
    elif key == 'e' and not game_over:  # Interact key
        interact_with_object()

def interact_with_object():
    """Allow player to interact with objects in the environment"""
    hit_info = raycast(player.position, player.forward, distance=3, ignore=(player,))
    if hit_info.entity:
        if hasattr(hit_info.entity, 'interactable') and hit_info.entity.interactable:
            # Handle interaction based on object type
            if hit_info.entity.object_type == 'objective':
                complete_objective(hit_info.entity.objective_id)
            elif hit_info.entity.object_type == 'document':
                display_document(hit_info.entity.doc_content)

def complete_objective(objective_id):
    """Complete an escape objective"""
    global current_objective
    if objective_id == current_objective:
        current_objective += 1
        display_message(f"Objective completed: {map_data['objectives'][objective_id]['description']}", duration=3)
        
        # Check if all objectives are complete
        if current_objective >= len(map_data.get("objectives", [])):
            display_message("You escaped the Backrooms!", duration=5)
            application.quit()

def display_message(text, duration=3):
    """Display a message to the player"""
    message = Text(text=text, origin=(0,0), scale=2, color=color.red, background=True)
    invoke(destroy, message, delay=duration)

def display_document(content):
    """Display a found document"""
    doc_window = Text(text=content, origin=(0,0), scale=1.5, color=color.white, background=True, line_height=1.5)
    invoke(destroy, doc_window, delay=10)

def update_sanity_effects():
    """Update visual and audio effects based on player sanity"""
    global vignette
    
    # Create or update vignette effect based on sanity
    if sanity < 30:
        if vignette is None:
            vignette = Entity(parent=camera.ui, model='quad', texture='white_cube', 
                             color=color.rgb(50, 0, 0, a=0.2), scale=10, z=1)
        else:
            # Increase red tint as sanity decreases
            vignette.color = color.rgb(50, 0, 0, a=(1 - sanity/30) * 0.4)
    elif vignette:
        destroy(vignette)
        vignette = None
    
    # Add visual distortions when sanity is low
    if sanity < 20:
        camera.rotation_x += random.uniform(-0.5, 0.5)
        camera.rotation_y += random.uniform(-0.5, 0.5)

# Entity classes for Backrooms
class EntityBase(Entity):
    def __init__(self, x=0, z=0, **kwargs):
        super().__init__(
            parent=interactive_parent, 
            model='cube', 
            scale_y=2, 
            origin_y=-.5, 
            color=color.rgb(100, 100, 100), 
            highlight_color=color.red, 
            collider='box',
            x=x,
            z=z,
            y=1,
            **kwargs
        )

class Hinder(EntityBase):
    """A threatening entity in the Backrooms that follows the player"""
    def __init__(self, x=0, z=0, **kwargs):
        super().__init__(
            model='cube',
            scale_y=2.5,
            color=color.rgb(30, 30, 30),  # Dark, menacing color
            x=x,
            z=z,
            y=1.25,
            **kwargs
        )
        self.original_color = self.color
        self.detection_range = 15
        self.chase_speed = 1.5
        self.sanity_drain_rate = 0.2  # Drains player sanity when nearby
        
    def update(self):
        # Only act if player is within detection range
        dist = distance_xz(player.position, self.position)
        if dist > self.detection_range:
            # Slowly move back to original position if player is far
            return

        # Drain player sanity when nearby
        if dist < 5:
            global sanity
            sanity = max(0, sanity - self.sanity_drain_rate * time.dt)
            
            # Visual effect when Hinder is close
            if dist < 3:
                self.color = color.rgb(255, 50, 50)  # Red when close
                # Add visual distortion
                camera.rotation_x += random.uniform(-1, 1)
                camera.rotation_y += random.uniform(-1, 1)
            else:
                self.color = self.original_color
        else:
            self.color = self.original_color

        # Move toward player
        self.look_at_2d(player.position, 'y')
        hit_info = raycast(self.world_position + Vec3(0,1,0), self.forward, 30, ignore=(self,))
        
        if hit_info.entity == player and dist > 1.5:
            self.position += self.forward * time.dt * self.chase_speed

class Objective(EntityBase):
    """An escape objective that player needs to find"""
    def __init__(self, x=0, z=0, objective_id=0, description="", **kwargs):
        super().__init__(
            model='cube',
            color=color.rgb(255, 255, 0),  # Yellow for visibility
            scale=(0.8, 0.8, 0.8),
            x=x,
            z=z,
            y=0.4,
            **kwargs
        )
        self.object_type = 'objective'
        self.objective_id = objective_id
        self.description = description
        self.interactable = True
        # Add a pulsing effect
        self.pulse_direction = 1
        self.pulse_speed = 1

    def update(self):
        # Pulsing effect to make it more noticeable
        current_scale = self.scale_x
        new_scale = current_scale + time.dt * self.pulse_speed * self.pulse_direction
        if new_scale > 1.0 or new_scale < 0.8:
            self.pulse_direction *= -1
            new_scale = current_scale - time.dt * self.pulse_speed * self.pulse_direction
        self.scale = (new_scale, new_scale, new_scale)

class Document(EntityBase):
    """A document the player can find with lore information"""
    def __init__(self, x=0, z=0, content="", **kwargs):
        super().__init__(
            model='cube',
            color=color.rgb(255, 255, 255),  # White for paper
            scale=(0.5, 0.1, 0.7),
            x=x,
            z=z,
            y=0.05,
            texture='textures/paper_doc.png',
            **kwargs
        )
        self.object_type = 'document'
        self.doc_content = content
        self.interactable = True

# Create Hinder entities at random positions on the map
hindering_entities = []
for i in range(3):  # Fewer but more threatening entities
    x = random.uniform(3, map_width-3)
    z = random.uniform(3, map_height-3)
    # Make sure the position is not a wall
    map_x, map_z = int(x), int(z)
    if 0 <= map_x < map_width and 0 <= map_z < map_height and map_data["map"][map_z][map_x] == 0:
        hindering_entities.append(Hinder(x=x, z=z))

# Create objectives based on map data
objectives = []
if "objectives" in map_data:
    for idx, obj_data in enumerate(map_data["objectives"]):
        if obj_data["type"] == "exit":
            exit_obj = Objective(
                x=obj_data["x"], 
                z=obj_data["z"], 
                objective_id=idx, 
                description=obj_data["description"]
            )
            objectives.append(exit_obj)

# Create some documents with Backrooms lore
documents = []
for i in range(5):
    x = random.uniform(2, map_width-2)
    z = random.uniform(2, map_height-2)
    # Make sure the position is not a wall
    map_x, map_z = int(x), int(z)
    if 0 <= map_x < map_width and 0 <= map_z < map_height and map_data["map"][map_z][map_x] == 0:
        # Check it's not too close to player start
        start_dist = distance_xz(Vec3(start_pos[0], 0, start_pos[1]), Vec3(x, 0, z))
        if start_dist > 5:
            doc_content = [
                "ENTRY LOG: Day 1 - I don't know where I am. The walls are yellow, endless. The fluorescent lights buzz overhead.",
                "WARNING: Do not stare at the walls for too long. They seem to... shift when you're not looking directly.",
                "THEY are here. I can hear footsteps in the distance. No matter which direction I go, I always end up in the same place.",
                "THEORY: This place exists outside normal reality. Time moves differently here. My watch stopped working.",
                "EXIT RUMOR: Someone mentioned there's a way out through a maintenance door. Look for signs of civilization."
            ][i % 5]
            document = Document(x=x, z=z, content=doc_content)
            documents.append(document)

# Toggle between editor and game mode
def pause_input(key):
    if key == 'tab':    # press tab to toggle edit/play mode
        editor_camera.enabled = not editor_camera.enabled

        player.visible_self = editor_camera.enabled
        player.cursor.enabled = not editor_camera.enabled
        mouse.locked = not editor_camera.enabled
        editor_camera.position = player.position

        application.paused = editor_camera.enabled

pause_handler = Entity(ignore_paused=True, input=pause_input)

# Backrooms lighting - more atmospheric
ambient_light = AmbientLight(color=color.rgb(80, 80, 40))  # Yellowish ambient light
flicker_light = PointLight(position=(0, 5, 0), color=color.rgb(200, 200, 100), intensity=0.5)

# Create a subtle fog effect
Sky()
sky = Sky()
sky.color = color.rgb(50, 50, 30)  # Dark yellowish sky for the void above

app.run()