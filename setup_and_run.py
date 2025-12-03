#!/usr/bin/env python3
"""
Setup and Run Script for Advanced Backrooms Game
This script installs dependencies and runs the game
"""

import subprocess
import sys
import os


def install_dependencies():
    """Install required Python packages"""
    print("Installing dependencies...")
    
    # List of required packages
    packages = [
        "ursina>=7.0.0",
        "pygame>=2.0.0",
        "panda3d>=1.10.0"
    ]
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except subprocess.CalledProcessError:
            print(f"Failed to install {package}")
            return False
    
    print("Dependencies installed successfully!")
    return True


def run_game(game_type="advanced"):
    """Run the specified version of the game"""
    if game_type == "advanced":
        game_file = "advanced_game.py"
        print("Starting Advanced Backrooms Game...")
    elif game_type == "optimized":
        game_file = "optimized_game.py"
        print("Starting Optimized Backrooms Game (for older laptops)...")
    elif game_type == "editor":
        game_file = "maps/advanced_map_editor.py"
        print("Starting Advanced Map Editor...")
    elif game_type == "generator":
        game_file = "maps/advanced_map_generator.py"
        print("Starting Advanced Map Generator...")
    else:
        print("Invalid game type. Use 'advanced', 'optimized', 'editor', or 'generator'")
        return
    
    if not os.path.exists(game_file):
        print(f"Error: {game_file} not found!")
        return
    
    try:
        subprocess.check_call([sys.executable, game_file])
    except subprocess.CalledProcessError as e:
        print(f"Error running {game_file}: {e}")
    except KeyboardInterrupt:
        print("\nGame stopped by user.")


def main():
    """Main function to handle user input and run appropriate action"""
    print("Advanced Backrooms Game - Setup and Run")
    print("======================================")
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "install":
            install_dependencies()
        elif command in ["run", "advanced"]:
            if install_dependencies():
                run_game("advanced")
        elif command == "optimized":
            if install_dependencies():
                run_game("optimized")
        elif command == "editor":
            if install_dependencies():
                run_game("editor")
        elif command == "generator":
            if install_dependencies():
                run_game("generator")
        elif command == "help":
            print("\nUsage:")
            print("  python setup_and_run.py install     - Install dependencies")
            print("  python setup_and_run.py run         - Run advanced game")
            print("  python setup_and_run.py advanced    - Run advanced game")
            print("  python setup_and_run.py optimized   - Run optimized game")
            print("  python setup_and_run.py editor      - Run map editor")
            print("  python setup_and_run.py generator   - Run map generator")
            print("  python setup_and_run.py help        - Show this help")
        else:
            print(f"Unknown command: {command}")
            print("Use 'python setup_and_run.py help' for available commands")
    else:
        print("\nAvailable commands:")
        print("  install     - Install dependencies")
        print("  run         - Run advanced game")
        print("  advanced    - Run advanced game")
        print("  optimized   - Run optimized game")
        print("  editor      - Run map editor")
        print("  generator   - Run map generator")
        print("  help        - Show help")
        
        print("\nExample: python setup_and_run.py run")


if __name__ == "__main__":
    main()