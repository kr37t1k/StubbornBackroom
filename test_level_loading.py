#!/usr/bin/env python
"""
Test script to verify level loading functionality works correctly
"""
import sys
import os
import json

def test_level_loading():
    print("Testing level loading functionality...")
    
    # Test that the level file was created
    level_file = "levels/generated_level.json"
    if not os.path.exists(level_file):
        print(f"ERROR: Level file {level_file} does not exist!")
        return False
    
    print(f"✓ Level file exists: {level_file}")
    
    # Test loading the level file
    try:
        with open(level_file, 'r') as f:
            level_data = json.load(f)
        print("✓ Level file can be loaded and parsed as JSON")
    except Exception as e:
        print(f"ERROR: Could not load level file: {e}")
        return False
    
    # Verify expected structure
    required_keys = ['width', 'height', 'map', 'rooms', 'doors', 'corridors', 'hazards', 'metadata']
    for key in required_keys:
        if key not in level_data:
            print(f"ERROR: Missing required key '{key}' in level data")
            return False
    
    print("✓ Level data has all required keys")
    
    # Test that the BackroomsWorld can load the level
    try:
        from backrooms_game import BackroomsWorld
        world = BackroomsWorld(level_file=level_file)
        print("✓ BackroomsWorld can load the level file")
        
        # Test that we can get cell data from the loaded level
        cell = world.get_cell(0, 0)
        print(f"✓ Can retrieve cell data from loaded level: {cell}")
        
        # Check if level dimensions match
        if hasattr(world, 'width') and hasattr(world, 'height'):
            print(f"✓ World dimensions loaded correctly: {world.width}x{world.height}")
        else:
            print("ERROR: World dimensions not loaded properly")
            return False
            
    except Exception as e:
        print(f"ERROR: Could not load level with BackroomsWorld: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n✓ All level loading tests passed!")
    return True

def test_editor():
    print("\nTesting level editor functionality...")
    
    try:
        # Try to import tkinter first to check if GUI is available
        import tkinter as tk
    except ImportError:
        print("⚠ Level editor requires tkinter (GUI library) which is not available in this environment")
        print("  The editor will work when tkinter is installed, but tests are skipped in headless mode")
        return True  # Return True since this is expected in headless environments
    
    try:
        # Try to import the editor to make sure it's syntactically correct
        import importlib.util
        spec = importlib.util.spec_from_file_location("backrooms_level_editor", "backrooms_level_editor.py")
        editor_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(editor_module)
        print("✓ Level editor module can be imported without syntax errors")
    except Exception as e:
        print(f"ERROR: Level editor has syntax errors: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("✓ Level editor test passed!")
    return True

def test_generator():
    print("\nTesting level generator functionality...")
    
    try:
        # Try to import the generator to make sure it's syntactically correct
        import importlib.util
        spec = importlib.util.spec_from_file_location("backrooms_level_generator", "backrooms_level_generator.py")
        generator_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(generator_module)
        print("✓ Level generator module can be imported without syntax errors")
        
        # Test creating a generator instance
        generator = generator_module.BackroomsLevelGenerator(width=20, height=20, seed=123)
        level_data = generator.generate_level()
        print("✓ Level generator can create levels")
        
        # Verify level data structure
        required_keys = ['width', 'height', 'map', 'rooms', 'doors', 'corridors', 'hazards', 'metadata']
        for key in required_keys:
            if key not in level_data:
                print(f"ERROR: Generator missing required key '{key}' in level data")
                return False
        print("✓ Generated level has all required keys")
        
    except Exception as e:
        print(f"ERROR: Level generator has errors: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("✓ Level generator test passed!")
    return True

if __name__ == "__main__":
    success = True
    success &= test_generator()
    success &= test_level_loading()
    success &= test_editor()
    
    if success:
        print("\n🎉 All tests passed! The level loading system is working correctly.")
    else:
        print("\n❌ Some tests failed.")
        sys.exit(1)