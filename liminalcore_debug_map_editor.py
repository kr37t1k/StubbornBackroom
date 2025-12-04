#!/usr/bin/env python3
"""
Debug Map Editor for Liminalcore Backrooms Game
Advanced debugging and map editing tool with visualization capabilities
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import json
import os
from typing import List, Tuple, Dict, Any
import random


class DebugMapEditor:
    """Advanced debug map editor with visualization and debugging features"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Liminalcore Debug Map Editor")
        self.root.geometry("1400x900")
        
        # Map data
        self.grid = []
        self.entities = []
        self.width = 50
        self.height = 50
        self.start_pos = (1, 1)
        self.end_pos = (self.width-2, self.height-2)
        self.current_tool = "wall"  # wall, path, start, end, door, entity, special
        self.current_entity_type = "chair"
        self.cell_size = 15
        self.grid_snap = True
        self.show_grid = True
        self.show_entities = True
        self.show_debug_info = True
        
        # Debug settings
        self.debug_settings = {
            'show_connections': True,
            'show_room_types': True,
            'show_reality_state': False,
            'highlight_path': False,
            'show_performance': True
        }
        
        # Create UI
        self.create_widgets()
        
        # Create initial empty map
        self.create_empty_map()
    
    def create_widgets(self):
        """Create the UI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top toolbar
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
            ("Special", "special"),
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
        entity_types = ["chair", "table", "plant", "light", "door", "monitor", "strange_object", "bookshelf", "painting"]
        self.entity_combo = ttk.Combobox(
            self.entity_frame,
            textvariable=self.entity_type_var,
            values=entity_types,
            state="readonly",
            width=12
        )
        self.entity_combo.pack(side=tk.LEFT, padx=(5, 0))
        self.entity_combo.bind("<<ComboboxSelected>>", self.on_entity_type_change)
        
        # File operations
        ttk.Button(toolbar, text="New", command=self.new_map).pack(side=tk.LEFT, padx=(20, 5))
        ttk.Button(toolbar, text="Open", command=self.open_map).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Save", command=self.save_map).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Save As", command=self.save_map_as).pack(side=tk.LEFT, padx=5)
        
        # Debug controls
        ttk.Button(toolbar, text="Debug View", command=self.toggle_debug_view).pack(side=tk.LEFT, padx=(20, 5))
        ttk.Button(toolbar, text="Generate", command=self.open_generator_dialog).pack(side=tk.LEFT, padx=5)
        
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
        self.canvas.bind("<Button-3>", self.on_canvas_right_click)  # Right-click for context menu
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, pady=(10, 0))
        
        # Debug info panel
        self.debug_panel = ttk.Frame(main_frame)
        self.debug_panel.pack(fill=tk.X, pady=(5, 0))
        
        # Debug toggles
        self.debug_vars = {}
        for setting, default in self.debug_settings.items():
            var = tk.BooleanVar(value=default)
            self.debug_vars[setting] = var
            chk = ttk.Checkbutton(self.debug_panel, text=setting.replace('_', ' ').title(), variable=var)
            chk.pack(side=tk.LEFT, padx=5)
        
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
        new_width = simpledialog.askinteger("New Map", "Enter map width:", initialvalue=50, minvalue=10, maxvalue=200)
        if new_width is None:
            return
            
        new_height = simpledialog.askinteger("New Map", "Enter map height:", initialvalue=50, minvalue=10, maxvalue=200)
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
            "entities": self.entities,
            "debug_info": self.debug_settings
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
        
        # Draw grid background
        if self.show_grid:
            for x in range(0, canvas_width, self.cell_size):
                self.canvas.create_line(x, 0, x, canvas_height, fill="#e0e0e0", tags="grid")
            for y in range(0, canvas_height, self.cell_size):
                self.canvas.create_line(0, y, canvas_width, y, fill="#e0e0e0", tags="grid")
        
        # Draw map cells
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
                    outline = "black"
                elif (x, y) == self.end_pos:
                    color = "red"
                    text = "E"
                    outline = "black"
                elif self.grid[y][x] == 1:  # Wall
                    color = "gray"
                    text = ""
                    outline = "black"
                elif self.grid[y][x] == 2:  # Door
                    color = "brown"
                    text = "D"
                    outline = "black"
                elif self.grid[y][x] == 3:  # Special
                    color = "orange"
                    text = "O"
                    outline = "black"
                elif self.grid[y][x] == 4:  # Liminal
                    color = "purple"
                    text = "L"
                    outline = "black"
                else:  # Path
                    color = "white"
                    text = ""
                    outline = "#cccccc"
                
                # Draw cell
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=outline, width=1)
                
                # Add text for start/end
                if text:
                    self.canvas.create_text(
                        x1 + self.cell_size//2, 
                        y1 + self.cell_size//2, 
                        text=text, 
                        font=("Arial", 8, "bold")
                    )
        
        # Draw entities if enabled
        if self.show_entities:
            for entity in self.entities:
                x, y = int(entity["x"]), int(entity["z"])
                if 0 <= x < self.width and 0 <= y < self.height:
                    x1 = x * self.cell_size + 3
                    y1 = y * self.cell_size + 3
                    x2 = x1 + self.cell_size - 6
                    y2 = y1 + self.cell_size - 6
                    
                    # Different colors for different entity types
                    colors = {
                        "chair": "blue",
                        "table": "saddlebrown", 
                        "plant": "green",
                        "light": "yellow",
                        "door": "brown",
                        "monitor": "lightblue",
                        "strange_object": "magenta",
                        "bookshelf": "sienna",
                        "painting": "olive"
                    }
                    color = colors.get(entity["type"], "pink")
                    
                    self.canvas.create_oval(x1, y1, x2, y2, fill=color, outline="black")
                    self.canvas.create_text(
                        x1 + (x2-x1)//2, 
                        y1 + (y2-y1)//2, 
                        text=entity["type"][0].upper(), 
                        font=("Arial", 6, "bold")
                    )
        
        # Draw debug information if enabled
        if self.show_debug_info:
            self.draw_debug_info()
    
    def draw_debug_info(self):
        """Draw debug information on the map"""
        # Draw connections between cells (simplified)
        if self.debug_settings['show_connections']:
            for y in range(self.height):
                for x in range(self.width):
                    if self.grid[y][x] in [0, 2]:  # Path or door
                        # Draw small circles for connected neighbors
                        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < self.width and 0 <= ny < self.height:
                                if self.grid[ny][nx] in [0, 2]:  # Connected path or door
                                    cx = (x + nx) * self.cell_size / 2
                                    cy = (y + ny) * self.cell_size / 2
                                    self.canvas.create_oval(
                                        cx-2, cy-2, cx+2, cy+2, 
                                        fill="lightgreen", outline="darkgreen"
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
    
    def on_canvas_right_click(self, event):
        """Handle right mouse click for context menu"""
        x = event.x // self.cell_size
        y = event.y // self.cell_size
        
        if 0 <= x < self.width and 0 <= y < self.height:
            # Create context menu
            context_menu = tk.Menu(self.root, tearoff=0)
            context_menu.add_command(label="Set as Start", command=lambda: self.set_start_pos(x, y))
            context_menu.add_command(label="Set as End", command=lambda: self.set_end_pos(x, y))
            context_menu.add_command(label="Clear Cell", command=lambda: self.clear_cell(x, y))
            context_menu.add_separator()
            context_menu.add_command(label="Get Cell Info", command=lambda: self.get_cell_info(x, y))
            
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
    
    def set_start_pos(self, x, y):
        """Set the start position"""
        # Remove previous start
        sx, sy = self.start_pos
        if 0 <= sx < self.width and 0 <= sy < self.height:
            if self.grid[sy][sx] not in [1, 2, 3, 4]:  # Not a wall or special type
                self.grid[sy][sx] = 0  # Reset to path
        # Set new start
        self.start_pos = (x, y)
        self.grid[y][x] = 0  # Make sure it's a path
        self.draw_map()
    
    def set_end_pos(self, x, y):
        """Set the end position"""
        # Remove previous end
        ex, ey = self.end_pos
        if 0 <= ex < self.width and 0 <= ey < self.height:
            if self.grid[ey][ex] not in [1, 2, 3, 4]:  # Not a wall or special type
                self.grid[ey][ex] = 0  # Reset to path
        # Set new end
        self.end_pos = (x, y)
        self.grid[y][x] = 0  # Make sure it's a path
        self.draw_map()
    
    def clear_cell(self, x, y):
        """Clear the cell (set to path)"""
        self.grid[y][x] = 0
        # Remove any entity at this position
        self.entities = [e for e in self.entities if not (int(e["x"]) == x and int(e["z"]) == y)]
        self.draw_map()
    
    def get_cell_info(self, x, y):
        """Get information about a cell"""
        cell_type = self.grid[y][x]
        cell_info = {
            0: "Path",
            1: "Wall", 
            2: "Door",
            3: "Special Room",
            4: "Liminal Space"
        }
        
        # Check for entities
        cell_entities = [e for e in self.entities if int(e["x"]) == x and int(e["z"]) == y]
        
        info = f"Cell ({x}, {y}):\n"
        info += f"Type: {cell_info.get(cell_type, 'Unknown')}\n"
        info += f"Entities: {len(cell_entities)}\n"
        
        for i, entity in enumerate(cell_entities):
            info += f"  {i+1}. {entity['type']}\n"
        
        messagebox.showinfo("Cell Info", info)
    
    def modify_cell(self, x, y):
        """Modify a cell based on the current tool"""
        if self.current_tool == "wall":
            self.grid[y][x] = 1
        elif self.current_tool == "path":
            self.grid[y][x] = 0
        elif self.current_tool == "start":
            self.set_start_pos(x, y)
        elif self.current_tool == "end":
            self.set_end_pos(x, y)
        elif self.current_tool == "door":
            self.grid[y][x] = 2
        elif self.current_tool == "special":
            self.grid[y][x] = 3
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
                    "z": float(y),
                    "id": len(self.entities)  # Add unique ID
                })
    
    def toggle_debug_view(self):
        """Toggle debug view settings"""
        # Update debug settings from UI
        for setting, var in self.debug_vars.items():
            self.debug_settings[setting] = var.get()
        
        # Redraw map with new settings
        self.draw_map()
    
    def open_generator_dialog(self):
        """Open the map generator dialog"""
        generator_window = tk.Toplevel(self.root)
        generator_window.title("Map Generator")
        generator_window.geometry("400x500")
        
        # Generator settings
        ttk.Label(generator_window, text="Map Generator Settings", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Width and height
        ttk.Label(generator_window, text="Width:").pack()
        width_var = tk.IntVar(value=self.width)
        width_spin = tk.Spinbox(generator_window, from_=10, to=200, textvariable=width_var)
        width_spin.pack(pady=5)
        
        ttk.Label(generator_window, text="Height:").pack()
        height_var = tk.IntVar(value=self.height)
        height_spin = tk.Spinbox(generator_window, from_=10, to=200, textvariable=height_var)
        height_spin.pack(pady=5)
        
        # Complexity
        ttk.Label(generator_window, text="Complexity (0.0-1.0):").pack()
        complexity_var = tk.DoubleVar(value=0.5)
        complexity_scale = tk.Scale(generator_window, from_=0.0, to=1.0, resolution=0.1, 
                                   orient=tk.HORIZONTAL, variable=complexity_var)
        complexity_scale.pack(pady=5)
        
        # Style selection
        ttk.Label(generator_window, text="Map Style:").pack()
        style_var = tk.StringVar(value="maze")
        style_combo = ttk.Combobox(generator_window, textvariable=style_var, 
                                  values=["maze", "open_space", "room_based", "liminal", "chaotic"],
                                  state="readonly")
        style_combo.pack(pady=5)
        
        # Buttons
        button_frame = ttk.Frame(generator_window)
        button_frame.pack(pady=20)
        
        def generate_map():
            # Get values
            width = width_var.get()
            height = height_var.get()
            complexity = complexity_var.get()
            style = style_var.get()
            
            # Create temporary generator to apply settings
            self.width = width
            self.height = height
            self.create_empty_map()
            
            # Apply some basic generation based on style
            self._generate_basic_map(style, complexity)
            
            # Update the main map
            self.draw_map()
            generator_window.destroy()
        
        ttk.Button(button_frame, text="Generate", command=generate_map).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=generator_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def _generate_basic_map(self, style, complexity):
        """Generate a basic map based on style and complexity"""
        # Initialize with walls
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] = 1  # Wall
        
        if style == "maze":
            self._generate_simple_maze(complexity)
        elif style == "open_space":
            self._generate_simple_open_space(complexity)
        elif style == "room_based":
            self._generate_simple_room_based(complexity)
        elif style == "liminal":
            self._generate_simple_liminal(complexity)
        elif style == "chaotic":
            self._generate_simple_chaotic(complexity)
        
        # Ensure start and end are clear
        self.grid[1][1] = 0  # Start
        self.grid[self.height-2][self.width-2] = 0  # End
        self.start_pos = (1, 1)
        self.end_pos = (self.width-2, self.width-2)
    
    def _generate_simple_maze(self, complexity):
        """Generate a simple maze"""
        # Create a basic maze pattern
        for y in range(1, self.height-1):
            for x in range(1, self.width-1):
                if x % 2 == 0 and y % 2 == 0:
                    self.grid[y][x] = 0  # Path
                elif x % 2 == 1 and y % 2 == 1:
                    # Randomly make some walls into paths based on complexity
                    if random.random() < complexity:
                        self.grid[y][x] = 0
        
        # Add some random paths to make it more complex
        for _ in range(int(self.width * self.height * 0.1 * complexity)):
            x = random.randint(2, self.width - 3)
            y = random.randint(2, self.height - 3)
            if self.grid[y][x] == 1:
                self.grid[y][x] = 0
    
    def _generate_simple_open_space(self, complexity):
        """Generate a simple open space"""
        wall_density = 0.15 * (1.0 - complexity)
        for y in range(1, self.height-1):
            for x in range(1, self.width-1):
                if random.random() < wall_density:
                    self.grid[y][x] = 1  # Wall
                else:
                    self.grid[y][x] = 0  # Path
    
    def _generate_simple_room_based(self, complexity):
        """Generate a simple room-based map"""
        # Create rooms
        room_count = max(5, int((self.width * self.height) * 0.01 * (1.0 + complexity)))
        min_room_size = 3
        max_room_size = 6 + int(complexity * 4)
        
        rooms = []
        for _ in range(room_count):
            room_width = random.randint(min_room_size, max_room_size)
            room_height = random.randint(min_room_size, max_room_size)
            x = random.randint(1, self.width - room_width - 1)
            y = random.randint(1, self.height - room_height - 1)
            
            # Check for overlap
            overlaps = False
            for rx, ry, rw, rh in rooms:
                if (x < rx + rw + 1 and x + room_width + 1 > rx and
                    y < ry + rh + 1 and y + room_height + 1 > ry):
                    overlaps = True
                    break
            
            if not overlaps:
                rooms.append((x, y, room_width, room_height))
                
                # Carve out the room
                for ry in range(y, y + room_height):
                    for rx in range(x, x + room_width):
                        if 0 <= ry < self.height and 0 <= rx < self.width:
                            self.grid[ry][rx] = 0
        
        # Connect rooms
        for i in range(len(rooms) - 1):
            room1 = rooms[i]
            room2 = rooms[i + 1]
            
            x1, y1 = room1[0] + room1[2] // 2, room1[1] + room1[3] // 2
            x2, y2 = room2[0] + room2[2] // 2, room2[1] + room2[3] // 2
            
            # Horizontal corridor
            start_x, end_x = min(x1, x2), max(x1, x2)
            for x in range(start_x, end_x + 1):
                if 0 <= x < self.width and 0 <= y1 < self.height:
                    self.grid[y1][x] = 0
            
            # Vertical corridor
            start_y, end_y = min(y1, y2), max(y1, y2)
            for y in range(start_y, end_y + 1):
                if 0 <= x2 < self.width and 0 <= y < self.height:
                    self.grid[y][x2] = 0
    
    def _generate_simple_liminal(self, complexity):
        """Generate a simple liminal map"""
        for y in range(1, self.height-1):
            for x in range(1, self.width-1):
                if random.random() < 0.1 * (1.0 - complexity):
                    self.grid[y][x] = 1  # Wall
                else:
                    self.grid[y][x] = 0  # Path
        
        # Add some special liminal areas
        special_count = int(self.width * self.height * 0.01 * complexity)
        for _ in range(special_count):
            x = random.randint(2, self.width - 3)
            y = random.randint(2, self.height - 3)
            self.grid[y][x] = 4  # Liminal space
    
    def _generate_simple_chaotic(self, complexity):
        """Generate a simple chaotic map"""
        chaos_factor = 0.45 + (complexity * 0.1)
        for y in range(1, self.height-1):
            for x in range(1, self.width-1):
                if random.random() < chaos_factor:
                    self.grid[y][x] = 1  # Wall
                else:
                    self.grid[y][x] = 0  # Path


def main():
    """Main function to run the debug map editor"""
    root = tk.Tk()
    app = DebugMapEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()