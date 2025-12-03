# advanced_raycast.py - Advanced Raycasting with both Pygame and Pyglet OpenGL implementations
import math
import random
import numpy as np
import pygame
from raycast import Raycaster
# Import OpenGL and Pyglet only when needed

# PyGame and OpenGL.

class AdvancedRaycaster:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.fov = math.pi / 3  # 60 degrees
        self.ray_angle_step = self.fov / width
        
        # Enhanced color palette
        self.colors = {
            'walls': [
                (240, 220, 180),  # Cream walls
                (230, 210, 170),  # Slightly darker
                (220, 200, 160),  # Even darker
                (255, 245, 220),  # Light cream
                (200, 190, 160),  # Darker cream
            ],
            'floors': [
                (250, 240, 210),  # Pale yellow floor
                (255, 250, 230),  # Lighter
                (240, 230, 200),  # Slightly darker
            ],
            'ceilings': [
                (255, 255, 245),  # Almost white ceiling
                (250, 250, 240),  # Slightly warm
                (245, 245, 235),  # Even warmer
            ],
            'fog': (200, 180, 150)  # Warm fog
        }
        
        self.wave_offset = 0
        self.flicker_intensity = 0.0
        
        # Initialize pygame surface for pygame rendering
        self.pygame_surface = pygame.Surface((width, height))
        
        # For OpenGL rendering
        self.opengl_initialized = False

    def cast_rays(self, player_x, player_y, player_angle, world, draw_distance=10):
        """Enhanced ray casting with more detailed information"""
        rays = []
        half_fov = self.fov / 2

        for x in range(self.width):
            # Calculate ray angle
            ray_angle = player_angle + (x / self.width - 0.5) * self.fov

            # Cast ray
            distance, wall_type, side, hit_x, hit_y = self._cast_single_ray_with_coords(
                player_x, player_y, ray_angle, world, draw_distance
            )

            # Apply fog
            fog_factor = min(1.0, distance / draw_distance)

            # Apply dream effects
            wave_effect = math.sin(self.wave_offset + x * 0.01) * 0.3
            distance *= (1.0 + wave_effect * 0.05)

            rays.append({
                'x': x,
                'distance': distance,
                'wall_type': wall_type,
                'side': side,  # 'x' or 'y' for texture correction
                'fog_factor': fog_factor,
                'hit_x': hit_x,
                'hit_y': hit_y
            })

        self.wave_offset += 0.03
        self.flicker_intensity = math.sin(self.wave_offset * 2) * 0.1

        return rays

    def _cast_single_ray_with_coords(self, start_x, start_y, angle, world, max_distance):
        """Enhanced ray casting that returns hit coordinates"""
        # Ray direction
        ray_dir_x = math.cos(angle)
        ray_dir_y = math.sin(angle)

        # Player position in map grid
        map_x = int(start_x)
        map_y = int(start_y)

        # Delta distance (how far to next grid line)
        delta_dist_x = abs(1.0 / ray_dir_x) if ray_dir_x != 0 else float('inf')
        delta_dist_y = abs(1.0 / ray_dir_y) if ray_dir_y != 0 else float('inf')

        # Step direction
        step_x = 1 if ray_dir_x > 0 else -1
        step_y = 1 if ray_dir_y > 0 else -1

        # Initial side distance
        if ray_dir_x < 0:
            side_dist_x = (start_x - map_x) * delta_dist_x
        else:
            side_dist_x = (map_x + 1.0 - start_x) * delta_dist_x

        if ray_dir_y < 0:
            side_dist_y = (start_y - map_y) * delta_dist_y
        else:
            side_dist_y = (map_y + 1.0 - start_y) * delta_dist_y

        # DDA loop
        distance = 0.0
        hit = False
        side = 'x'  # which side was hit
        hit_x, hit_y = start_x, start_y

        while not hit and distance < max_distance:
            # Jump to next map square
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 'x'
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 'y'

            # Check for wall hit
            try:
                if abs(map_x) < 1000 and abs(map_y) < 1000:
                    wall_type = world.get_cell(map_x, map_y)
                    if wall_type > 0:
                        hit = True
                        # Calculate exact hit coordinates
                        if side == 'x':
                            distance = abs((map_x - start_x + (0 if step_x > 0 else 1)) / ray_dir_x)
                            hit_x = map_x + (0 if step_x < 0 else 1)
                            hit_y = start_y + distance * ray_dir_y
                        else:
                            distance = abs((map_y - start_y + (0 if step_y > 0 else 1)) / ray_dir_y)
                            hit_x = start_x + distance * ray_dir_x
                            hit_y = map_y + (0 if step_y < 0 else 1)
                else:
                    wall_type = 0
            except:
                wall_type = 0

            if abs(map_x) > 2000 or abs(map_y) > 2000:
                distance = max_distance
                wall_type = 0
                break

        if not hit:
            distance = max_distance
            wall_type = 0
            hit_x, hit_y = start_x + ray_dir_x * max_distance, start_y + ray_dir_y * max_distance

        return distance, wall_type, side, hit_x, hit_y

    def get_wall_color(self, wall_type, ray_data):
        """Enhanced wall color with dream effects"""
        if wall_type == 0:
            return (0, 0, 0)  # Transparent (shouldn't be drawn)

        # Select base color
        color_idx = (wall_type - 1) % len(self.colors['walls'])
        base_color = list(self.colors['walls'][color_idx])

        # Add flicker effect
        flicker = 1.0 + self.flicker_intensity * random.uniform(-0.1, 0.1)
        base_color[0] = min(255, int(base_color[0] * flicker))
        base_color[1] = min(255, int(base_color[1] * flicker))
        base_color[2] = min(255, int(base_color[2] * flicker))

        # Add fog
        fog = self.colors['fog']
        fog_factor = ray_data['fog_factor']
        final_color = [
            int(base_color[0] * (1 - fog_factor * 0.5) + fog[0] * fog_factor * 0.5),
            int(base_color[1] * (1 - fog_factor * 0.5) + fog[1] * fog_factor * 0.5),
            int(base_color[2] * (1 - fog_factor * 0.5) + fog[2] * fog_factor * 0.5)
        ]

        return tuple(final_color)


class PygameRaycastRenderer:
    """Pygame implementation of the raycasting renderer"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.raycaster = AdvancedRaycaster(width, height)
        
    def render_3d_view(self, rays, screen, player_x, player_y, player_angle):
        """Enhanced 3D rendering using Pygame"""
        # Clear screen with fog color
        screen.fill((200, 180, 150))

        # Draw gradient ceiling
        for y in range(0, self.height // 2):
            intensity = y / (self.height // 2)
            color = (
                int(255 * (1 - intensity * 0.1)),
                int(255 * (1 - intensity * 0.1)),
                int(245 * (1 - intensity * 0.2))
            )
            pygame.draw.line(screen, color, (0, y), (self.width, y))

        # Draw gradient floor
        for y in range(self.height // 2, self.height):
            intensity = (y - self.height // 2) / (self.height // 2)
            color = (
                int(250 * (1 - intensity * 0.2)),
                int(240 * (1 - intensity * 0.2)),
                int(210 * (1 - intensity * 0.3))
            )
            pygame.draw.line(screen, color, (0, y), (self.width, y))

        # Draw walls
        for ray in rays:
            distance = ray['distance']
            if distance < 15:  # Draw only visible walls
                # Correct wall height calculation with perspective correction
                corrected_distance = distance * math.cos(ray['x'] / self.width * self.raycaster.fov - self.raycaster.fov / 2)
                wall_height = int((self.height * 0.8) / corrected_distance)

                # Center wall vertically
                wall_top = max(0, (self.height - wall_height) // 2)
                wall_bottom = min(self.height, wall_top + wall_height)

                # Get wall color
                color = self.raycaster.get_wall_color(ray['wall_type'], ray)

                # Draw wall strip with better anti-aliasing
                if wall_top < wall_bottom:
                    pygame.draw.line(
                        screen, color,
                        (ray['x'], wall_top),
                        (ray['x'], wall_bottom),
                        1  # Single pixel width for cleaner look
                    )

        # Draw player view center marker
        pygame.draw.circle(screen, (255, 200, 150), (self.width // 2, self.height // 2), 3, 1)


class OpenGLRaycastRenderer:
    """Pyglet OpenGL implementation of the raycasting renderer"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.raycaster = AdvancedRaycaster(width, height)
        self.vertex_buffer = None
        self.color_buffer = None
        self.initialized = False
        
    def init_opengl(self):
        """Initialize OpenGL settings"""
        # Import OpenGL and Pyglet here to avoid issues in headless environments
        from OpenGL.GL import glClearColor, glEnable, glBlendFunc, GL_BLEND, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA
        from OpenGL.GL import glClear, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT
        from pyglet.gl import glBegin, glEnd, glVertex2f, glColor3f, GL_QUADS, GL_LINES
        import pyglet
        
        if not self.initialized:
            glClearColor(0.78, 0.71, 0.59, 1.0)  # Fog color
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            self.initialized = True
    
    def render_3d_view(self, rays, window, player_x, player_y, player_angle):
        """Enhanced 3D rendering using OpenGL"""
        # Import OpenGL and Pyglet here to avoid issues in headless environments
        from OpenGL.GL import glClearColor, glEnable, glBlendFunc, GL_BLEND, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA
        from OpenGL.GL import glClear, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT
        from pyglet.gl import glBegin, glEnd, glVertex2f, glColor3f, GL_QUADS, GL_LINES
        import pyglet
        
        self.init_opengl()
        
        # Clear the screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Draw ceiling
        glBegin(GL_QUADS)
        glColor3f(1.0, 1.0, 0.96)  # Light ceiling color
        glVertex2f(-1.0, 1.0)
        glVertex2f(1.0, 1.0)
        glColor3f(0.98, 0.98, 0.94)  # Gradient ceiling color
        glVertex2f(1.0, 0.0)
        glVertex2f(-1.0, 0.0)
        glEnd()
        
        # Draw floor
        glBegin(GL_QUADS)
        glColor3f(0.98, 0.94, 0.82)  # Light floor color
        glVertex2f(-1.0, 0.0)
        glVertex2f(1.0, 0.0)
        glColor3f(0.96, 0.88, 0.78)  # Gradient floor color
        glVertex2f(1.0, -1.0)
        glVertex2f(-1.0, -1.0)
        glEnd()
        
        # Draw walls using OpenGL quads
        for ray in rays:
            distance = ray['distance']
            if distance < 15:  # Draw only visible walls
                # Convert ray x coordinate to normalized screen coordinate
                x_norm = (ray['x'] / self.width) * 2.0 - 1.0
                
                # Correct wall height calculation with perspective correction
                corrected_distance = distance * math.cos(ray['x'] / self.width * self.raycaster.fov - self.raycaster.fov / 2)
                wall_height = (self.height * 0.8) / corrected_distance
                wall_height_norm = wall_height / self.height
                
                # Calculate wall top and bottom in normalized coordinates
                wall_top = wall_height_norm / 2.0
                wall_bottom = -wall_height_norm / 2.0
                
                # Get wall color
                color = self.raycaster.get_wall_color(ray['wall_type'], ray)
                r, g, b = color[0]/255.0, color[1]/255.0, color[2]/255.0
                
                # Draw wall segment
                glBegin(GL_QUADS)
                glColor3f(r, g, b)
                glVertex2f(x_norm, wall_top)
                glVertex2f(x_norm + 2.0/self.width, wall_top)
                glVertex2f(x_norm + 2.0/self.width, wall_bottom)
                glVertex2f(x_norm, wall_bottom)
                glEnd()
        
        # Draw crosshair
        glColor3f(1.0, 0.8, 0.6)
        glBegin(GL_LINES)
        glVertex2f(-0.01, 0.0)
        glVertex2f(0.01, 0.0)
        glVertex2f(0.0, -0.01)
        glVertex2f(0.0, 0.01)
        glEnd()


def create_pyglet_opengl_game():
    """Create a Pyglet window with OpenGL raycasting"""
    # Import only when needed to avoid issues in headless environments
    import pyglet
    from pyglet.window import key
    from world import BackroomsWorld
    from player import DreamPlayer
    
    width, height = 1024, 768
    window = pyglet.window.Window(width=width, height=height, caption="Advanced Raycasting - Pyglet OpenGL")
    
    # Initialize game objects
    raycaster = AdvancedRaycaster(width, height)
    opengl_renderer = OpenGLRaycastRenderer(width, height)
    world = BackroomsWorld(seed=42)
    player = DreamPlayer(x=5.5, y=5.5, angle=0)
    
    @window.event
    def on_draw():
        # Cast rays
        px, py = player.get_render_position()
        rays = raycaster.cast_rays(px, py, player.angle, world, draw_distance=15)
        
        # Render with OpenGL
        opengl_renderer.render_3d_view(rays, window, px, py, player.angle)
    
    # Key handling for Pyglet
    keys = pyglet.window.key.KeyStateHandler()
    window.push_handlers(keys)
    
    def update(dt):
        # Handle movement based on pressed keys
        pressed_keys = set()
        if keys[pyglet.window.key.W]:
            pressed_keys.add('w')
        if keys[pyglet.window.key.S]:
            pressed_keys.add('s')
        if keys[pyglet.window.key.A]:
            pressed_keys.add('a')
        if keys[pyglet.window.key.D]:
            pressed_keys.add('d')
        if keys[pyglet.window.key.LEFT]:
            pressed_keys.add('left')
        if keys[pyglet.window.key.RIGHT]:
            pressed_keys.add('right')
            
        # Update player
        player.update(pressed_keys, world, dt * 60)  # dt is in seconds, multiply by 60 for similar behavior
    
    pyglet.clock.schedule_interval(update, 1/60.0)
    
    return window


def run_advanced_game():
    """Run the advanced game with both implementations"""
    print("Advanced Raycasting Game - Choose Implementation:")
    print("1. Pygame (current implementation)")
    print("2. Pyglet OpenGL (new implementation)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        # Run with pygame
        pygame.init()
        WIDTH, HEIGHT = 1024, 768
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Advanced Raycasting - Pygame")
        clock = pygame.time.Clock()
        
        # Initialize game objects
        raycaster = AdvancedRaycaster(WIDTH, HEIGHT)
        pygame_renderer = PygameRaycastRenderer(WIDTH, HEIGHT)
        world = BackroomsWorld(seed=42)
        player = DreamPlayer(x=5.5, y=5.5, angle=0)
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # Handle key states
            keys_pressed = set()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                keys_pressed.add('w')
            if keys[pygame.K_s]:
                keys_pressed.add('s')
            if keys[pygame.K_a]:
                keys_pressed.add('a')
            if keys[pygame.K_d]:
                keys_pressed.add('d')
            if keys[pygame.K_LEFT]:
                keys_pressed.add('left')
            if keys[pygame.K_RIGHT]:
                keys_pressed.add('right')
            
            # Update player
            dt = clock.get_time() / 16.67
            player.update(keys_pressed, world, dt)
            
            # Cast rays
            px, py = player.get_render_position()
            rays = raycaster.cast_rays(px, py, player.angle, world, draw_distance=15)
            
            # Render
            pygame_renderer.render_3d_view(rays, screen, px, py, player.angle)
            
            # Update display
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
    
    elif choice == "2":
        # Run with Pyglet OpenGL
        window = create_pyglet_opengl_game()
        pyglet.app.run()
    
    else:
        print("Invalid choice. Running default Pygame version...")
        pygame.init()
        WIDTH, HEIGHT = 1024, 768
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Advanced Raycasting - Pygame")
        clock = pygame.time.Clock()
        
        # Initialize game objects
        raycaster = AdvancedRaycaster(WIDTH, HEIGHT)
        pygame_renderer = PygameRaycastRenderer(WIDTH, HEIGHT)
        world = BackroomsWorld(seed=42)
        player = DreamPlayer(x=5.5, y=5.5, angle=0)
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # Handle key states
            keys_pressed = set()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                keys_pressed.add('w')
            if keys[pygame.K_s]:
                keys_pressed.add('s')
            if keys[pygame.K_a]:
                keys_pressed.add('a')
            if keys[pygame.K_d]:
                keys_pressed.add('d')
            if keys[pygame.K_LEFT]:
                keys_pressed.add('left')
            if keys[pygame.K_RIGHT]:
                keys_pressed.add('right')
            
            # Update player
            dt = clock.get_time() / 16.67
            player.update(keys_pressed, world, dt)
            
            # Cast rays
            px, py = player.get_render_position()
            rays = raycaster.cast_rays(px, py, player.angle, world, draw_distance=15)
            
            # Render
            pygame_renderer.render_3d_view(rays, screen, px, py, player.angle)
            
            # Update display
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()


if __name__ == "__main__":
    run_advanced_game()