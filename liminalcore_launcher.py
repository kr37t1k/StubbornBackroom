#!/usr/bin/env python3
"""
Liminalcore Backrooms Game Launcher
Unified launcher for all game components
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog


class LiminalcoreLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Liminalcore Backrooms Game Launcher")
        self.root.geometry("600x500")
        
        self.create_widgets()
    
    def create_widgets(self):
        # Title
        title_label = ttk.Label(
            self.root, 
            text="Liminalcore Backrooms Game", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=20)
        
        subtitle_label = ttk.Label(
            self.root, 
            text="Advanced 3D Backrooms Experience", 
            font=("Arial", 12)
        )
        subtitle_label.pack(pady=5)
        
        # Main buttons frame
        buttons_frame = ttk.Frame(self.root)
        buttons_frame.pack(pady=30, padx=20, fill=tk.X)
        
        # Main game button
        main_game_btn = ttk.Button(
            buttons_frame,
            text="Play Main Game",
            command=self.launch_main_game,
            width=30
        )
        main_game_btn.pack(pady=10)
        
        # Map editors frame
        editors_frame = ttk.LabelFrame(self.root, text="Map Editors", padding=10)
        editors_frame.pack(pady=10, padx=20, fill=tk.X)
        
        ttk.Button(
            editors_frame,
            text="3D Map Editor",
            command=self.launch_3d_editor,
            width=25
        ).pack(pady=5)
        
        ttk.Button(
            editors_frame,
            text="Debug Map Editor",
            command=self.launch_debug_editor,
            width=25
        ).pack(pady=5)
        
        # Map generators frame
        generators_frame = ttk.LabelFrame(self.root, text="Map Generators", padding=10)
        generators_frame.pack(pady=10, padx=20, fill=tk.X)
        
        ttk.Button(
            generators_frame,
            text="Advanced Map Generator",
            command=self.launch_map_generator,
            width=25
        ).pack(pady=5)
        
        ttk.Button(
            generators_frame,
            text="Basic Map Generator",
            command=self.launch_basic_generator,
            width=25
        ).pack(pady=5)
        
        # Utilities frame
        utilities_frame = ttk.LabelFrame(self.root, text="Utilities", padding=10)
        utilities_frame.pack(pady=10, padx=20, fill=tk.X)
        
        ttk.Button(
            utilities_frame,
            text="Open Maps Directory",
            command=self.open_maps_directory,
            width=25
        ).pack(pady=5)
        
        ttk.Button(
            utilities_frame,
            text="View Documentation",
            command=self.show_documentation,
            width=25
        ).pack(pady=5)
        
        # Exit button
        exit_btn = ttk.Button(
            self.root,
            text="Exit",
            command=self.root.quit,
            width=20
        )
        exit_btn.pack(pady=20)
    
    def launch_main_game(self):
        """Launch the main game"""
        try:
            subprocess.Popen([sys.executable, "liminalcore_backrooms_game.py"])
        except FileNotFoundError:
            messagebox.showerror("Error", "Main game file not found!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch game: {str(e)}")
    
    def launch_3d_editor(self):
        """Launch the 3D map editor"""
        try:
            subprocess.Popen([sys.executable, "liminalcore_3d_map_editor.py"])
        except FileNotFoundError:
            messagebox.showerror("Error", "3D Map Editor not found!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch 3D editor: {str(e)}")
    
    def launch_debug_editor(self):
        """Launch the debug map editor"""
        try:
            subprocess.Popen([sys.executable, "liminalcore_debug_map_editor.py"])
        except FileNotFoundError:
            messagebox.showerror("Error", "Debug Map Editor not found!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch debug editor: {str(e)}")
    
    def launch_map_generator(self):
        """Launch the advanced map generator"""
        try:
            subprocess.Popen([sys.executable, "liminalcore_map_generator.py"])
        except FileNotFoundError:
            messagebox.showerror("Error", "Advanced Map Generator not found!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch generator: {str(e)}")
    
    def launch_basic_generator(self):
        """Launch the basic map generator"""
        try:
            subprocess.Popen([sys.executable, "maps/liminalcore_basic_map_generator.py"])
        except FileNotFoundError:
            messagebox.showerror("Error", "Basic Map Generator not found!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch basic generator: {str(e)}")
    
    def open_maps_directory(self):
        """Open the maps directory"""
        try:
            if sys.platform == "win32":
                os.startfile("maps")
            elif sys.platform == "darwin":  # macOS
                subprocess.Popen(["open", "maps"])
            else:  # Linux and other Unix-like
                subprocess.Popen(["xdg-open", "maps"])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open maps directory: {str(e)}")
    
    def show_documentation(self):
        """Show documentation"""
        doc_text = """
Liminalcore Backrooms Game Documentation
========================================

Main Game Features:
- Liminalcore aesthetics with enhanced visuals
- Reality distortion system with 4 states
- Procedural backrooms generation
- Quality settings (Low, Normal, High, Ultra)
- Debugging tools and performance monitoring

Controls:
- WASD: Move
- Mouse: Look around
- Space: Jump
- F1-F4: Quality levels
- F5-F10: Debug toggles
- Tab: Reality distortion view
- M: Switch maps
- E: Open 3D Map Editor
- Esc: Quit

Map Editors:
- 3D Map Editor: Visual 3D map creation
- Debug Map Editor: Advanced debugging tools
- Map Generators: Procedural map creation

Configuration:
- Edit liminalcore_config.json for game settings
- Place custom maps in the maps/ directory
        """
        doc_window = tk.Toplevel(self.root)
        doc_window.title("Documentation")
        doc_window.geometry("700x500")
        
        text_widget = tk.Text(doc_window, wrap=tk.WORD)
        text_widget.insert(tk.END, doc_text)
        text_widget.config(state=tk.DISABLED)
        
        scrollbar = ttk.Scrollbar(doc_window, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def run(self):
        """Run the launcher"""
        self.root.mainloop()


def main():
    launcher = LiminalcoreLauncher()
    launcher.run()


if __name__ == "__main__":
    main()