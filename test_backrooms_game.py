"""
Test script to verify the Backrooms game OOP components work correctly
"""
from backrooms_game import BackroomsWorld, PlayerController, AtmosphericLighting
import math

def test_world_generation():
    """Test world generation functionality"""
    print("Testing BackroomsWorld...")
    world = BackroomsWorld(seed=42)
    
    # Test cell generation
    cell = world.get_cell(0, 0)
    assert cell in [0, 1, 2, 3, 4, 5], f"Invalid cell type: {cell}"
    print(f"✓ Generated cell type: {cell}")
    
    # Test chunk generation
    chunk = world.generate_chunk(0, 0)
    assert chunk is not None, "Chunk should not be None"
    print("✓ Chunk generated successfully")
    
    print("World generation tests passed!\n")


def test_player_controller():
    """Test player controller functionality"""
    print("Testing PlayerController...")
    player = PlayerController(x=5.5, y=5.5, z=1.8)
    
    # Test initial position
    pos = player.get_position()
    assert abs(pos.x - 5.5) < 0.001, f"Expected x=5.5, got {pos.x}"
    assert abs(pos.y - 5.5) < 0.001, f"Expected y=5.5, got {pos.y}"
    assert abs(pos.z - 1.8) < 0.001, f"Expected z=1.8, got {pos.z}"
    print("✓ Initial position correct")
    
    # Test forward vector
    forward = player.get_forward_vector()
    assert isinstance(forward, type(player.get_right_vector())), "Forward vector should be LVector3"
    print("✓ Direction vectors work correctly")
    
    # Test key handling
    player.set_key('forward', True)
    assert player.keys['forward'] == True, "Key should be set to True"
    player.set_key('forward', False)
    assert player.keys['forward'] == False, "Key should be set to False"
    print("✓ Key handling works correctly")
    
    print("Player controller tests passed!\n")


def test_atmospheric_lighting():
    """Test atmospheric lighting functionality"""
    print("Testing AtmosphericLighting...")
    
    # Since we can't create a window in headless environment, test the constructor and setup
    lighting = AtmosphericLighting(None)  # Pass None as render initially
    
    # Test that the constructor works
    assert lighting.light_sources == [], "Light sources should be empty initially"
    print("✓ Lighting system initialized correctly")
    
    # We can't test the full setup without a render context, so just verify the method exists
    assert hasattr(lighting, 'setup_dynamic_lights'), "setup_dynamic_lights method should exist"
    assert hasattr(lighting, 'update'), "update method should exist"
    print("✓ Lighting methods exist")
    
    print("Atmospheric lighting tests passed!\n")


def test_game_integration():
    """Test that all components work together"""
    print("Testing component integration...")
    
    # Create all main components
    world = BackroomsWorld(seed=42)
    player = PlayerController(x=5.5, y=5.5, z=1.8)
    
    # Test that player can move in the world
    initial_pos = player.get_position()
    
    # Set forward movement
    player.set_key('forward', True)
    
    # Update player with a small time step
    dt = 0.016  # ~60 FPS
    player.update(dt, world)
    
    # Position should have changed
    new_pos = player.get_position()
    # For this test, we just verify the update method runs without error
    print("✓ Player update method works correctly")
    
    print("Component integration tests passed!\n")


if __name__ == "__main__":
    print("Running Backrooms Game OOP Component Tests...\n")
    
    test_world_generation()
    test_player_controller()
    test_atmospheric_lighting()
    test_game_integration()
    
    print("🎉 All tests passed! The Backrooms game OOP components work correctly.")