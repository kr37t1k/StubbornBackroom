#!/usr/bin/env python3
"""
Advanced Map Editor for Backrooms Game
GUI tool to edit maps with multiple entity types for the 3D backrooms game
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
from typing import List, Tuple


class AdvancedMapEditor:
    """Advanced GUI Map Editor for the backrooms game"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Backrooms Map Editor")
        self.root.geometry("1200x800")
        
        # Map data
        self.grid = []
        self.entities = []  # List of entities in the map
        self.width = 20
        self.height = 20
        self.start_pos = (1, 1)
        self.end_pos = (self.width-2, self.height-2)
        self.current_tool = "wall"  # wall, path, start, end, door, entity
        self.current_entity_type = "chair"  # For entity tool
        self.cell_size = 25
        self.grid_snap = True  # Snap to grid for entity placement
        
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
        tools = [
            ("Wall", "wall"), 
            ("Path", "path"), 
            ("Start", "start"), 
            ("End", "end"),
            ("Door", "door"),
            ("Entity", "entity")
        ]
        for text, tool in tools:
            ttk.Radiobutton(
                toolbar, 
                text=text, 
                variable=self.tool_var, 
                value=tool,
                command=self.on_tool_change
            ).pack(side=tk.LEFT, padx=(5, 5))
        
        # Entity type selection (only visible when entity tool is selected)
        self.entity_frame = ttk.Frame(toolbar)
        self.entity_frame.pack(side=tk.LEFT, padx=(20, 5))
        
        ttk.Label(self.entity_frame, text="Entity:").pack(side=tk.LEFT)
        self.entity_type_var = tk.StringVar(value="chair")
        entity_types = ["chair", "table", "plant", "light", "door"]
        self.entity_combo = ttk.Combobox(
            self.entity_frame, 
            textvariable=self.entity_type_var, 
            values=entity_types,
            state="readonly",
            width=10
        )
        self.entity_combo.pack(side=tk.LEFT, padx=(5, 0))
        self.entity_combo.bind("<<ComboboxSelected>>", self.on_entity_type_change)
        
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
        
        # Update entity frame visibility
        self.update_entity_frame_visibility()
    
    def on_tool_change(self):
        """Handle tool change"""
        self.current_tool = self.tool_var.get()
        self.status_var.set(f"Tool: {self.current_tool.capitalize()}")
        self.update_entity_frame_visibility()
    
    def on_entity_type_change(self, event=None):
        """Handle entity type change"""
        self.current_entity_type = self.entity_type_var.get()
    
    def update_entity_frame_visibility(self):
        """Show/hide entity frame based on current tool"""
        if self.current_tool == "entity":
            self.entity_frame.pack(side=tk.LEFT, padx=(20, 5))
        else:
            self.entity_frame.pack_forget()
    
    def create_empty_map(self):
        """Create an empty map"""
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.entities = []
        
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
            
            # Load entities if they exist
            if "entities" in data:
                self.entities = data["entities"]
            else:
                self.entities = []
            
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
            "map": self.grid,
            "entities": self.entities
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
                elif self.grid[y][x] == 2:  # Door
                    color = "brown"
                    text = "D"
                elif self.grid[y][x] == 3:  # Special
                    color = "orange"
                    text = "O"
                else:  # Path
                    color = "white"
                    text = ""
                
                # Draw cell
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
                
                # Add text for start/end
                if text:
                    self.canvas.create_text(x1 + self.cell_size//2, y1 + self.cell_size//2, 
                                          text=text, font=("Arial", 10, "bold"))
        
        # Draw entities
        for entity in self.entities:
            x, y = int(entity["x"]), int(entity["z"])
            if 0 <= x < self.width and 0 <= y < self.height:
                x1 = x * self.cell_size + 5
                y1 = y * self.cell_size + 5
                x2 = x1 + self.cell_size - 10
                y2 = y1 + self.cell_size - 10
                
                # Different colors for different entity types
                colors = {
                    "chair": "blue",
                    "table": "purple", 
                    "plant": "green",
                    "light": "yellow",
                    "door": "brown"
                }
                color = colors.get(entity["type"], "pink")
                
                self.canvas.create_oval(x1, y1, x2, y2, fill=color, outline="black")
                self.canvas.create_text(
                    x1 + (x2-x1)//2, 
                    y1 + (y2-y1)//2, 
                    text=entity["type"][0].upper(), 
                    font=("Arial", 8, "bold")
                )
    
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
        elif self.current_tool == "door":
            self.grid[y][x] = 2  # Door identifier
        elif self.current_tool == "entity":
            # Check if there's already an entity at this position
            existing_entity = None
            for i, entity in enumerate(self.entities):
                if int(entity["x"]) == x and int(entity["z"]) == y:
                    existing_entity = i
                    break
            
            if existing_entity is not None:
                # Remove existing entity
                del self.entities[existing_entity]
            else:
                # Add new entity
                self.entities.append({
                    "type": self.current_entity_type,
                    "x": float(x),
                    "y": 0.0,
                    "z": float(y)
                })


def main():
    """Main function to run the advanced map editor"""
    import tkinter.simpledialog
    
    root = tk.Tk()
    app = AdvancedMapEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()