import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import numpy as np
from PIL import Image, ImageTk
import os

class BackroomsLevelEditor:
    """
    Backrooms level editor GUI that allows users to create, edit, and save levels
    that can be loaded into the game.
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("Backrooms Level Editor")
        self.root.geometry("1200x800")
        
        # Tile types
        self.EMPTY = 0
        self.WALL = 1
        self.FLOOR = 2
        self.DOOR = 3
        self.CORRIDOR = 4
        self.ROOM = 5
        self.HAZARD = 6
        
        # Level data
        self.level_map = np.zeros((50, 50), dtype=int)
        self.width = 50
        self.height = 50
        self.tile_size = 12  # Size of each tile in pixels
        self.current_tile = self.FLOOR  # Default tile to place
        
        # Create the GUI
        self.create_widgets()
        self.update_display()
        
    def create_widgets(self):
        """Create all GUI widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Toolbar
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        # Tile selection buttons
        ttk.Label(toolbar, text="Tile Type:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.tile_var = tk.StringVar(value="Floor")
        tile_options = [
            ("Empty", self.EMPTY),
            ("Wall", self.WALL),
            ("Floor", self.FLOOR),
            ("Door", self.DOOR),
            ("Corridor", self.CORRIDOR),
            ("Room", self.ROOM),
            ("Hazard", self.HAZARD)
        ]
        
        for text, value in tile_options:
            ttk.Radiobutton(
                toolbar, 
                text=text, 
                variable=self.tile_var, 
                value=text,
                command=lambda v=value: self.set_current_tile(v)
            ).pack(side=tk.LEFT, padx=5)
        
        # File operations
        file_frame = ttk.Frame(toolbar)
        file_frame.pack(side=tk.RIGHT)
        
        ttk.Button(file_frame, text="New", command=self.new_level).pack(side=tk.LEFT, padx=2)
        ttk.Button(file_frame, text="Load", command=self.load_level).pack(side=tk.LEFT, padx=2)
        ttk.Button(file_frame, text="Save", command=self.save_level).pack(side=tk.LEFT, padx=2)
        ttk.Button(file_frame, text="Generate", command=self.generate_level).pack(side=tk.LEFT, padx=2)
        ttk.Button(file_frame, text="Preview", command=self.preview_level).pack(side=tk.LEFT, padx=2)
        
        # Canvas for level display
        self.canvas = tk.Canvas(
            main_frame, 
            width=self.width * self.tile_size, 
            height=self.height * self.tile_size,
            bg='black',
            highlightthickness=1,
            highlightbackground='gray'
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind mouse events
        self.canvas.bind("<B1-Motion>", self.paint_tile)
        self.canvas.bind("<Button-1>", self.paint_tile)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, pady=(10, 0))
        
    def set_current_tile(self, tile_type):
        """Set the current tile type to place."""
        self.current_tile = tile_type
        self.status_var.set(f"Current tile: {self.get_tile_name(tile_type)}")
    
    def get_tile_name(self, tile_type):
        """Get the name of a tile type."""
        names = {
            self.EMPTY: "Empty",
            self.WALL: "Wall",
            self.FLOOR: "Floor",
            self.DOOR: "Door",
            self.CORRIDOR: "Corridor",
            self.ROOM: "Room",
            self.HAZARD: "Hazard"
        }
        return names.get(tile_type, "Unknown")
    
    def paint_tile(self, event):
        """Paint a tile at the mouse position."""
        x = event.x // self.tile_size
        y = event.y // self.tile_size
        
        if 0 <= x < self.width and 0 <= y < self.height:
            self.level_map[y, x] = self.current_tile
            self.draw_tile(x, y, self.current_tile)
    
    def draw_tile(self, x, y, tile_type):
        """Draw a single tile on the canvas."""
        color_map = {
            self.EMPTY: "#000000",      # Black
            self.WALL: "#646464",       # Gray
            self.FLOOR: "#C8C8C8",      # Light gray
            self.DOOR: "#FFA500",       # Orange
            self.CORRIDOR: "#B4B4B4",   # Lighter gray
            self.ROOM: "#DCDCDC",       # Lighter gray
            self.HAZARD: "#FF0000"      # Red
        }
        
        color = color_map.get(tile_type, "#000000")
        
        self.canvas.create_rectangle(
            x * self.tile_size, y * self.tile_size,
            (x + 1) * self.tile_size, (y + 1) * self.tile_size,
            fill=color,
            outline="#404040",
            width=1
        )
    
    def update_display(self):
        """Update the entire display."""
        self.canvas.delete("all")
        
        for y in range(self.height):
            for x in range(self.width):
                self.draw_tile(x, y, self.level_map[y, x])
    
    def new_level(self):
        """Create a new empty level."""
        self.level_map = np.zeros((self.height, self.width), dtype=int)
        self.update_display()
        self.status_var.set("New level created")
    
    def load_level(self):
        """Load a level from a JSON file."""
        filename = filedialog.askopenfilename(
            title="Load Backrooms Level",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                
                self.width = data['width']
                self.height = data['height']
                self.level_map = np.array(data['map'])
                
                # Resize canvas if needed
                self.canvas.config(
                    width=self.width * self.tile_size,
                    height=self.height * self.tile_size
                )
                
                self.update_display()
                self.status_var.set(f"Level loaded from {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load level: {str(e)}")
    
    def save_level(self):
        """Save the current level to a JSON file."""
        filename = filedialog.asksaveasfilename(
            title="Save Backrooms Level",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                level_data = {
                    'width': self.width,
                    'height': self.height,
                    'seed': 0,  # Not generated, so seed is 0
                    'map': self.level_map.tolist(),
                    'rooms': [],  # Will be calculated from the map
                    'doors': [],  # Will be calculated from the map
                    'corridors': [],  # Will be calculated from the map
                    'hazards': [],  # Will be calculated from the map
                    'metadata': {
                        'generated_by': 'BackroomsLevelEditor',
                        'tile_types': {
                            'empty': self.EMPTY,
                            'wall': self.WALL,
                            'floor': self.FLOOR,
                            'door': self.DOOR,
                            'corridor': self.CORRIDOR,
                            'room': self.ROOM,
                            'hazard': self.HAZARD
                        }
                    }
                }
                
                # Calculate room, door, corridor, and hazard positions
                for y in range(self.height):
                    for x in range(self.width):
                        tile_type = self.level_map[y, x]
                        if tile_type == self.ROOM:
                            level_data['rooms'].append([x, y])
                        elif tile_type == self.DOOR:
                            level_data['doors'].append([x, y])
                        elif tile_type == self.CORRIDOR:
                            level_data['corridors'].append([x, y])
                        elif tile_type == self.HAZARD:
                            level_data['hazards'].append([x, y])
                
                with open(filename, 'w') as f:
                    json.dump(level_data, f, indent=2)
                
                self.status_var.set(f"Level saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save level: {str(e)}")
    
    def generate_level(self):
        """Generate a new level using the level generator."""
        try:
            # Import the level generator
            from backrooms_level_generator import BackroomsLevelGenerator
            
            # Create a new level
            generator = BackroomsLevelGenerator(width=self.width, height=self.height)
            level_data = generator.generate_level()
            
            # Update the editor with the generated level
            self.width = level_data['width']
            self.height = level_data['height']
            self.level_map = np.array(level_data['map'])
            
            # Resize canvas
            self.canvas.config(
                width=self.width * self.tile_size,
                height=self.height * self.tile_size
            )
            
            self.update_display()
            self.status_var.set("Level generated using procedural generator")
        except ImportError:
            messagebox.showerror("Error", "Could not import backrooms_level_generator")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate level: {str(e)}")
    
    def preview_level(self):
        """Preview the level as an image."""
        try:
            # Create a color map for different tile types
            color_map = {
                self.EMPTY: (0, 0, 0),      # Black
                self.WALL: (100, 100, 100), # Gray
                self.FLOOR: (200, 200, 200), # Light gray
                self.DOOR: (255, 165, 0),   # Orange
                self.CORRIDOR: (180, 180, 180), # Lighter gray
                self.ROOM: (220, 220, 220), # Lighter gray
                self.HAZARD: (255, 0, 0)    # Red
            }
            
            # Create image
            img = Image.new('RGB', (self.width, self.height))
            pixels = img.load()
            
            for y in range(self.height):
                for x in range(self.width):
                    tile_type = self.level_map[y, x]
                    pixels[x, y] = color_map.get(tile_type, (0, 0, 0))
            
            # Scale up the image for better visibility
            img = img.resize((self.width * 10, self.height * 10), Image.NEAREST)
            
            # Show the image
            img.show()
            self.status_var.set("Level preview opened")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create preview: {str(e)}")

def main():
    root = tk.Tk()
    app = BackroomsLevelEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()