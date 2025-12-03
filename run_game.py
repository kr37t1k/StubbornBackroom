#!/usr/bin/env python
"""
Launcher script for the Panda3D Backrooms Game
"""
import sys
import os

def main():
    print("StubbornBackrooms - Panda3D Edition")
    print("Loading game...")
    
    # Import and run the main game
    try:
        from panda_backrooms_game import main as game_main
        game_main()
    except ImportError as e:
        print(f"Error importing game: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install panda3d noise")
        sys.exit(1)
    except Exception as e:
        print(f"Error running game: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()