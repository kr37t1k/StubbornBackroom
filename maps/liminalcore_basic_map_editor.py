#!/usr/bin/env python3
"""
Map Editor for Backrooms Game
GUI tool to edit maps for the 3D backrooms game
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
from typing import List, Tuple


class MapEditor:
    """GUI Map Editor for the backrooms game"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Backrooms Map Editor")
        self.root.geometry("1000x700")
        
        # Map data
        self.grid = []
        self.width = 20
        self.height = 20
        self.start_pos = (1, 1)
        self.end_pos = (self.width-2, self.height-2)
        self.current_tool = "wall"  # wall, path, start, end
        self.cell_size = 20
        
        # Create UI
        self.create_widgets()
        
        # Create initial empty map
        self.create_empty_map()
    
    def create_widgets(self):
        """Create the UI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Toolbar
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        # Tool selection
        ttk.Label(toolbar, text="Tool:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.tool_var = tk.StringVar(value="wall")
        tools = [("Wall", "wall"), ("Path", "path"), ("Start", "start"), ("End", "end")]
        for text, tool in tools:
            ttk.Radiobutton(toolbar, text=text, variable=self.tool_var, value=tool,
                           command=self.on_tool_change).pack(side=tk.LEFT, padx=(5, 5))
        
        # File operations
        ttk.Button(toolbar, text="New", command=self.new_map).pack(side=tk.LEFT, padx=(20, 5))
        ttk.Button(toolbar, text="Open", command=self.open_map).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Save", command=self.save_map).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Save As", command=self.save_map_as).pack(side=tk.LEFT, padx=5)
        
        # Canvas for map
        self.canvas_frame = ttk.Frame(main_frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollable canvas
        self.canvas = tk.Canvas(self.canvas_frame, bg="white", scrollregion=(0, 0, 800, 600))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout for canvas and scrollbars
        self.canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Bind canvas events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, pady=(10, 0))
    
    def on_tool_change(self):
        """Handle tool change"""
        self.current_tool = self.tool_var.get()
        self.status_var.set(f"Tool: {self.current_tool.capitalize()}")
    
    def create_empty_map(self):
        """Create an empty map"""
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        # Border with walls
        for x in range(self.width):
            self.grid[0][x] = 1
            self.grid[self.height-1][x] = 1
        for y in range(self.height):
            self.grid[y][0] = 1
            self.grid[y][self.width-1] = 1
        
        # Set start and end positions
        self.start_pos = (1, 1)
        self.end_pos = (self.width-2, self.height-2)
        
        self.draw_map()
    
    def new_map(self):
        """Create a new map"""
        # Ask for dimensions
        new_width = tk.simpledialog.askinteger("New Map", "Enter map width:", initialvalue=20, minvalue=10, maxvalue=200)
        if new_width is None:
            return
            
        new_height = tk.simpledialog.askinteger("New Map", "Enter map height:", initialvalue=20, minvalue=10, maxvalue=200)
        if new_height is None:
            return
        
        self.width = new_width
        self.height = new_height
        self.create_empty_map()
        self.status_var.set(f"New map created: {self.width}x{self.height}")
    
    def open_map(self):
        """Open a map from file"""
        filepath = filedialog.askopenfilename(
            title="Open Map",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not filepath:
            return
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.width = data["width"]
            self.height = data["height"]
            self.grid = data["map"]
            self.start_pos = tuple(data["start_pos"])
            self.end_pos = tuple(data["end_pos"])
            
            self.draw_map()
            self.status_var.set(f"Map loaded from {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load map: {str(e)}")
    
    def save_map(self):
        """Save the current map"""
        # For now, use a default path
        if not hasattr(self, 'current_filepath') or not self.current_filepath:
            self.save_map_as()
        else:
            self._save_to_file(self.current_filepath)
    
    def save_map_as(self):
        """Save the current map with a new filename"""
        filepath = filedialog.asksaveasfilename(
            title="Save Map",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not filepath:
            return
        
        self._save_to_file(filepath)
        self.current_filepath = filepath
        self.status_var.set(f"Map saved to {os.path.basename(filepath)}")
    
    def _save_to_file(self, filepath):
        """Save map data to a file"""
        data = {
            "width": self.width,
            "height": self.height,
            "seed": 42,  # Default seed for edited maps
            "start_pos": self.start_pos,
            "end_pos": self.end_pos,
            "map": self.grid
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def draw_map(self):
        """Draw the map on the canvas"""
        self.canvas.delete("all")
        
        # Calculate canvas size
        canvas_width = max(self.width * self.cell_size, 400)
        canvas_height = max(self.height * self.cell_size, 400)
        
        # Update scroll region
        self.canvas.configure(scrollregion=(0, 0, canvas_width, canvas_height))
        
        # Draw grid
        for y in range(self.height):
            for x in range(self.width):
                # Calculate position
                x1 = x * self.cell_size
                y1 = y * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                # Determine color based on cell type
                if (x, y) == self.start_pos:
                    color = "green"
                    text = "S"
                elif (x, y) == self.end_pos:
                    color = "red"
                    text = "E"
                elif self.grid[y][x] == 1:  # Wall
                    color = "gray"
                    text = ""
                else:  # Path
                    color = "white"
                    text = ""
                
                # Draw cell
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
                
                # Add text for start/end
                if text:
                    self.canvas.create_text(x1 + self.cell_size//2, y1 + self.cell_size//2, 
                                          text=text, font=("Arial", 10, "bold"))
    
    def on_canvas_click(self, event):
        """Handle mouse click on canvas"""
        # Convert canvas coordinates to grid coordinates
        x = event.x // self.cell_size
        y = event.y // self.cell_size
        
        if 0 <= x < self.width and 0 <= y < self.height:
            self.modify_cell(x, y)
            self.draw_map()
    
    def on_canvas_drag(self, event):
        """Handle mouse drag on canvas"""
        # Convert canvas coordinates to grid coordinates
        x = event.x // self.cell_size
        y = event.y // self.cell_size
        
        if 0 <= x < self.width and 0 <= y < self.height:
            self.modify_cell(x, y)
            self.draw_map()
    
    def modify_cell(self, x, y):
        """Modify a cell based on the current tool"""
        if self.current_tool == "wall":
            self.grid[y][x] = 1
        elif self.current_tool == "path":
            self.grid[y][x] = 0
        elif self.current_tool == "start":
            # Remove previous start
            sx, sy = self.start_pos
            if 0 <= sx < self.width and 0 <= sy < self.height:
                self.grid[sy][sx] = 0
            # Set new start
            self.start_pos = (x, y)
            self.grid[y][x] = 0  # Make sure it's a path
        elif self.current_tool == "end":
            # Remove previous end
            ex, ey = self.end_pos
            if 0 <= ex < self.width and 0 <= ey < self.height:
                self.grid[ey][ex] = 0
            # Set new end
            self.end_pos = (x, y)
            self.grid[y][x] = 0  # Make sure it's a path


def main():
    """Main function to run the map editor"""
    import tkinter.simpledialog
    
    root = tk.Tk()
    app = MapEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()