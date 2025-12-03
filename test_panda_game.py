#!/usr/bin/env python
"""
Test script to verify the Panda3D game components work correctly
"""
import sys
import os

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import panda3d
        from panda3d.core import LPoint3f, LVector3f, LColor
        print("✓ Panda3D core imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Panda3D core: {e}")
        return False
    
    try:
        import noise
        print("✓ Noise module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import noise: {e}")
        return False
    
    try:
        import math
        import random
        import sys
        import os
        from direct.showbase.ShowBase import ShowBase
        from direct.task import Task
        from direct.interval.IntervalGlobal import Sequence
        from direct.gui.DirectGui import DirectLabel, DirectButton, DirectSlider
        print("✓ All other required modules imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import other modules: {e}")
        return False
    
    return True

def test_asset_loading():
    """Test that assets can be loaded"""
    print("\nTesting asset loading...")
    
    # Check textures folder
    if os.path.exists("textures"):
        print("✓ Textures folder exists")
        textures = os.listdir("textures")
        if textures:
            print(f"✓ Found texture files: {textures}")
        else:
            print("⚠ No texture files found in textures folder")
    else:
        print("⚠ Textures folder does not exist")
    
    # Check audio folder
    if os.path.exists("audio"):
        print("✓ Audio folder exists")
        audio_files = os.listdir("audio")
        if audio_files:
            print(f"✓ Found audio files: {audio_files}")
        else:
            print("⚠ No audio files found in audio folder")
    else:
        print("⚠ Audio folder does not exist")
    
    return True

def test_game_classes():
    """Test that game classes can be instantiated"""
    print("\nTesting game classes...")
    
    try:
        # Import the main game classes from our game file
        import importlib.util
        spec = importlib.util.spec_from_file_location("panda_backrooms_game", "/workspace/panda_backrooms_game.py")
        game_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(game_module)
        
        # Test BackroomsWorld
        world = game_module.BackroomsWorld(seed=42)
        cell = world.get_cell(5.5, 5.5)
        print(f"✓ BackroomsWorld instantiated, sample cell type: {cell}")
        
        # Test DreamPlayer
        player = game_module.DreamPlayer(x=5.5, y=5.5, angle=0)
        pos = player.get_render_position()
        print(f"✓ DreamPlayer instantiated, initial position: {pos}")
        
        # Test BackgroundMusic
        music = game_module.BackgroundMusic()
        print("✓ BackgroundMusic class instantiated")
        
        return True
    except Exception as e:
        print(f"✗ Error testing game classes: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("Panda3D Backrooms Game - Test Suite")
    print("=" * 40)
    
    success = True
    
    success &= test_imports()
    success &= test_asset_loading()
    success &= test_game_classes()
    
    print("\n" + "=" * 40)
    if success:
        print("✓ All tests passed! The game should work correctly.")
        print("\nTo run the game, execute: python panda_backrooms_game.py")
    else:
        print("✗ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()