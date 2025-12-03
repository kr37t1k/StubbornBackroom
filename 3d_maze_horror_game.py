import pygame
import math
import random
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

class Player:
    def __init__(self):
        self.x = 1.5
        self.y = 1.5
        self.z = 1.8
        self.angle = 0
        self.vertical_angle = 0
        self.speed = 0.05
        self.vertical_speed = 0.05
        self.fov = 70
        self.near = 0.1
        self.far = 100.0

class Enemy:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.active = True
        self.animation_offset = random.uniform(0, 2 * math.pi)

class MazeGame:
    def __init__(self):
        pygame.init()
        self.width, self.height = 800, 600
        self.display = (self.width, self.height)
        pygame.display.set_mode(self.display, DOUBLEBUF | OPENGL)
        pygame.display.set_caption("3D Horror Maze")
        self.clock = pygame.time.Clock()
        
        # Initialize OpenGL settings
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glShadeModel(GL_SMOOTH)
        
        # Set up lighting
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, (5, 5, 5, 1))
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.8, 0.8, 0.8, 1.0))
        glLightfv(GL_LIGHT0, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
        
        # Material properties
        glMaterialfv(GL_FRONT, GL_AMBIENT, (0.1, 0.1, 0.1, 1.0))
        glMaterialfv(GL_FRONT, GL_DIFFUSE, (0.7, 0.7, 0.7, 1.0))
        glMaterialfv(GL_FRONT, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
        glMaterialf(GL_FRONT, GL_SHININESS, 50.0)
        
        # Initialize player
        self.player = Player()
        
        # Create maze layout (1 = wall, 0 = path)
        self.maze = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 0, 1, 1, 1, 0, 1],
            [1, 0, 1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 0, 1, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 1, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1, 0, 1],
            [1, 0, 1, 1, 1, 1, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        ]
        
        # Create enemies
        self.enemies = []
        for i in range(10):  # 10 enemies scattered in the maze
            while True:
                x = random.uniform(1.5, 8.5)
                y = random.uniform(1.5, 8.5)
                if self.maze[int(y)][int(x)] == 0:  # Only place on paths
                    self.enemies.append(Enemy(x, y, 0.5))
                    break
        
        # Game state
        self.score = 0
        self.game_over = False
        self.horror_mode = True
        
        # Hide cursor for aiming
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

    def draw_maze(self):
        """Draw the 3D maze"""
        for y in range(len(self.maze)):
            for x in range(len(self.maze[y])):
                if self.maze[y][x] == 1:
                    # Draw wall
                    glPushMatrix()
                    glTranslatef(x, y, 0)
                    self.draw_cube(0.5, 0.9, 0.5, (0.2, 0.2, 0.2))  # Dark gray walls
                    glPopMatrix()

    def draw_floor(self):
        """Draw the floor"""
        glBegin(GL_QUADS)
        glColor3f(0.1, 0.1, 0.1)  # Dark gray floor
        glVertex3f(0, 0, 0)
        glVertex3f(10, 0, 0)
        glVertex3f(10, 10, 0)
        glVertex3f(0, 10, 0)
        glEnd()

    def draw_ceiling(self):
        """Draw the ceiling"""
        glBegin(GL_QUADS)
        glColor3f(0.05, 0.05, 0.05)  # Very dark ceiling
        glVertex3f(0, 0, 1.8)
        glVertex3f(10, 0, 1.8)
        glVertex3f(10, 10, 1.8)
        glVertex3f(0, 10, 1.8)
        glEnd()

    def draw_cube(self, width, height, depth, color):
        """Draw a colored cube"""
        glColor3f(*color)
        
        # Front face
        glBegin(GL_QUADS)
        glVertex3f(-width, -height, -depth)
        glVertex3f(width, -height, -depth)
        glVertex3f(width, height, -depth)
        glVertex3f(-width, height, -depth)
        
        # Back face
        glVertex3f(-width, -height, depth)
        glVertex3f(-width, height, depth)
        glVertex3f(width, height, depth)
        glVertex3f(width, -height, depth)
        
        # Top face
        glVertex3f(-width, height, -depth)
        glVertex3f(width, height, -depth)
        glVertex3f(width, height, depth)
        glVertex3f(-width, height, depth)
        
        # Bottom face
        glVertex3f(-width, -height, -depth)
        glVertex3f(-width, -height, depth)
        glVertex3f(width, -height, depth)
        glVertex3f(width, -height, -depth)
        
        # Right face
        glVertex3f(width, -height, -depth)
        glVertex3f(width, height, -depth)
        glVertex3f(width, height, depth)
        glVertex3f(width, -height, depth)
        
        # Left face
        glVertex3f(-width, -height, -depth)
        glVertex3f(-width, -height, depth)
        glVertex3f(-width, height, depth)
        glVertex3f(-width, height, -depth)
        glEnd()

    def draw_enemies(self):
        """Draw all enemies in the maze"""
        for enemy in self.enemies:
            if enemy.active:
                glPushMatrix()
                # Add a subtle animation to make it more eerie
                float_offset = math.sin(pygame.time.get_ticks() / 500 + enemy.animation_offset) * 0.1
                glTranslatef(enemy.x, enemy.y, enemy.z + float_offset)
                # Draw enemy as a small red cube to look like a hazard
                self.draw_cube(0.2, 0.2, 0.2, (0.8, 0.1, 0.1))  # Red for danger
                glPopMatrix()

    def draw_player(self):
        """Draw the player (for debugging)"""
        glPushMatrix()
        glTranslatef(self.player.x, self.player.y, self.player.z)
        glColor3f(0, 0, 1)  # Blue sphere for player
        # Draw a simple sphere for the player
        quad = gluNewQuadric()
        gluSphere(quad, 0.2, 10, 10)
        gluDeleteQuadric(quad)
        glPopMatrix()

    def check_collision(self, new_x, new_y):
        """Check if the new position collides with a wall"""
        grid_x = int(new_x)
        grid_y = int(new_y)
        
        # Check if we're within bounds
        if grid_x < 0 or grid_x >= len(self.maze[0]) or grid_y < 0 or grid_y >= len(self.maze):
            return True
            
        # Check if the grid cell is a wall
        if self.maze[grid_y][grid_x] == 1:
            return True
            
        return False

    def update_player(self):
        """Update player position based on input"""
        if self.game_over:
            return
            
        keys = pygame.key.get_pressed()
        
        # Calculate movement direction based on current angle
        dx = math.sin(math.radians(self.player.angle))
        dy = math.cos(math.radians(self.player.angle))
        
        # Forward movement
        if keys[K_w]:
            new_x = self.player.x + dx * self.player.speed
            new_y = self.player.y + dy * self.player.speed
            if not self.check_collision(new_x, new_y):
                self.player.x = new_x
                self.player.y = new_y
        
        # Backward movement
        if keys[K_s]:
            new_x = self.player.x - dx * self.player.speed
            new_y = self.player.y - dy * self.player.speed
            if not self.check_collision(new_x, new_y):
                self.player.x = new_x
                self.player.y = new_y
        
        # Strafe left
        if keys[K_a]:
            strafe_angle = self.player.angle + 90
            dx_strafe = math.sin(math.radians(strafe_angle))
            dy_strafe = math.cos(math.radians(strafe_angle))
            new_x = self.player.x + dx_strafe * self.player.speed
            new_y = self.player.y + dy_strafe * self.player.speed
            if not self.check_collision(new_x, new_y):
                self.player.x = new_x
                self.player.y = new_y
        
        # Strafe right
        if keys[K_d]:
            strafe_angle = self.player.angle - 90
            dx_strafe = math.sin(math.radians(strafe_angle))
            dy_strafe = math.cos(math.radians(strafe_angle))
            new_x = self.player.x + dx_strafe * self.player.speed
            new_y = self.player.y + dy_strafe * self.player.speed
            if not self.check_collision(new_x, new_y):
                self.player.x = new_x
                self.player.y = new_y
        
        # Vertical movement (for debugging)
        if keys[K_SPACE]:
            self.player.z += self.player.vertical_speed
        if keys[K_LSHIFT]:
            self.player.z -= self.player.vertical_speed
        
        # Keep player above ground and below ceiling
        self.player.z = max(1.5, min(self.player.z, 1.8))

    def check_enemy_collisions(self):
        """Check for collisions with enemies"""
        for enemy in self.enemies:
            if enemy.active:
                distance = math.sqrt((self.player.x - enemy.x)**2 + (self.player.y - enemy.y)**2)
                if distance < 0.5:  # Collision threshold
                    enemy.active = False
                    self.score += 1

    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False  # Exit on ESC
                    
                if event.key == pygame.K_r and self.game_over:
                    # Restart game
                    self.__init__()
            
            if event.type == pygame.MOUSEMOTION and not self.game_over:
                # Mouse movement for looking around
                rel_x, rel_y = event.rel
                self.player.angle += rel_x * 0.1
                self.player.vertical_angle = max(-90, min(90, self.player.vertical_angle - rel_y * 0.1))
        
        return True

    def setup_camera(self):
        """Set up the camera perspective"""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.player.fov, (self.width / self.height), self.player.near, self.player.far)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Calculate camera direction
        dx = math.sin(math.radians(self.player.angle))
        dz = math.cos(math.radians(self.player.angle))
        dy = math.sin(math.radians(self.player.vertical_angle))
        
        # Set camera position and look direction
        gluLookAt(
            self.player.x, self.player.y, self.player.z,
            self.player.x + dx, self.player.y + dz, self.player.z + dy,
            0, 0, 1
        )

    def render_hud(self):
        """Render heads-up display"""
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, self.height, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Render score
        font = pygame.font.SysFont('Arial', 24)
        score_text = font.render(f'Score: {self.score}', True, (255, 255, 255))
        # Convert pygame surface to OpenGL texture and render would be needed for full implementation
        # For now, just print to console
        if self.score % 5 == 0 and self.score > 0:
            print(f"Score: {self.score}")
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def render(self):
        """Main rendering function"""
        # Set background color (dark for horror atmosphere)
        glClearColor(0.05, 0.0, 0.05, 1.0)  # Dark purple/black
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        self.setup_camera()
        
        # Draw the maze environment
        self.draw_floor()
        self.draw_ceiling()
        self.draw_maze()
        self.draw_enemies()
        
        # Draw HUD
        self.render_hud()
        
        pygame.display.flip()

    def run(self):
        """Main game loop"""
        running = True
        while running:
            running = self.handle_events()
            
            if not self.game_over:
                self.update_player()
                self.check_enemy_collisions()
                
                # Check win condition
                active_enemies = sum(1 for enemy in self.enemies if enemy.active)
                if active_enemies == 0:
                    self.game_over = True
                    print("You've collected all enemies! You win!")
            
            self.render()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()

if __name__ == "__main__":
    game = MazeGame()
    game.run()