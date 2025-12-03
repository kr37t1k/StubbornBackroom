#!/usr/bin/env python
"""
Launcher script for the new Backrooms Game
"""
import sys
import os
import argparse

def main():
    print("Backrooms Game - Panda3D Edition")
    print("Loading game with FPS controls...")
    
    parser = argparse.ArgumentParser(description='Backrooms Game')
    parser.add_argument('--level', type=str, help='Path to level file to load')
    args = parser.parse_args()
    
    # Check if level file exists
    level_file = None
    if args.level:
        if os.path.exists(args.level):
            level_file = args.level
            print(f"Loading level from: {level_file}")
        else:
            print(f"Level file not found: {args.level}")
            sys.exit(1)
    
    # Import and run the main game
    try:
        from backrooms_game import BackroomsGame
        game = BackroomsGame(level_file=level_file)
        game.run()
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