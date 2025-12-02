"""
Backroom Generation Script
This script generates the backrooms environment for the Ursina game.
"""
import json
import random


def generate_room(x, z):
    """Generate a single room with all its properties"""
    # Random room properties
    room_type = random.choice(['empty', 'messy', 'clean', 'abandoned'])
    has_furniture = random.random() > 0.3
    has_light = random.random() > 0.2
    dream_zone = random.random() > 0.85  # 15% chance of dream zone

    # Dream zone effects
    dream_effects = []
    if dream_zone:
        effects = ['slow', 'fast', 'glitch', 'panic']
        dream_effects = random.sample(effects, random.randint(1, 2))

    # Furniture generation (if room has furniture)
    furniture = []
    if has_furniture:
        furniture_types = ['chair', 'table', 'lamp', 'plant', 'bookshelf', 'couch']
        num_furniture = random.randint(1, 5)
        for _ in range(num_furniture):
            f_type = random.choice(furniture_types)
            pos_x = random.uniform(-3, 3)
            pos_z = random.uniform(-3, 3)
            rotation = random.randint(0, 3) * 90
            furniture.append({
                'type': f_type,
                'position': [pos_x, 0.5, pos_z],
                'rotation': rotation
            })

    # Light properties (if room has light)
    light_props = None
    if has_light:
        light_props = {
            'type': random.choice(['point', 'ambient', 'directional']),
            'color': [random.randint(200, 255), random.randint(200, 255), random.randint(180, 220)],  # RGB list
            'intensity': random.uniform(0.5, 1.5)
        }

    # Room properties with better color contrast
    return {
        'position': [x, 0, z],
        'type': room_type,
        'has_furniture': has_furniture,
        'furniture': furniture,
        'has_light': has_light,
        'light': light_props,
        'dream_zone': dream_zone,
        'dream_effects': dream_effects,
        'wall_color': [random.randint(220, 240), random.randint(220, 240), random.randint(180, 200)],  # Off-white
        'floor_color': [random.randint(200, 230), random.randint(200, 230), random.randint(160, 190)]  # Slightly yellow
    }


def generate_world_grid(size=8):
    """Generate a grid of rooms and save to JSON"""
    world_data = {}
    for x in range(-size // 2, size // 2):
        for z in range(-size // 2, size // 2):
            room_key = f"{x},{z}"
            world_data[room_key] = generate_room(x, z)

    # Save to file
    with open('generated_world.json', 'w') as f:
        json.dump(world_data, f, indent=2)
    print(f"Generated and saved {len(world_data)} rooms to generated_world.json")
    return world_data


def generate_advanced_room(x, z):
    """Generate an advanced room with more features"""
    room = generate_room(x, z)
    
    # Add more advanced features
    room['hazards'] = []
    if random.random() > 0.9:  # 10% chance of hazards
        hazards = ['water_puddle', 'broken_glass', 'strange_sound', 'flickering_light']
        num_hazards = random.randint(1, 2)
        room['hazards'] = random.sample(hazards, num_hazards)
    
    # Add entities
    room['entities'] = []
    if random.random() > 0.85:  # 15% chance of entities
        entities = ['shadow_figure', 'stray_person', 'unknown_object']
        num_entities = random.randint(1, 2)
        room['entities'] = random.sample(entities, num_entities)
    
    # Add environmental features
    room['environment'] = {
        'humidity': random.uniform(0.3, 0.9),
        'temperature': random.uniform(15, 25),
        'air_quality': random.uniform(0.1, 0.9),
        'sound_level': random.uniform(0.1, 0.8)
    }
    
    return room


def generate_advanced_world_grid(size=10):
    """Generate an advanced grid of rooms with more features"""
    world_data = {}
    for x in range(-size // 2, size // 2):
        for z in range(-size // 2, size // 2):
            room_key = f"{x},{z}"
            if random.random() > 0.7:  # 30% of rooms are advanced
                world_data[room_key] = generate_advanced_room(x, z)
            else:
                world_data[room_key] = generate_room(x, z)

    # Save to file
    with open('generated_world.json', 'w') as f:
        json.dump(world_data, f, indent=2)
    print(f"Generated and saved {len(world_data)} advanced rooms to generated_world.json")
    return world_data


if __name__ == "__main__":
    print("Generating backrooms...")
    # You can choose to generate either regular or advanced rooms
    generate_world_grid(10)  # Generate 10x10 grid
    # Or use generate_advanced_world_grid(10) for more complex rooms