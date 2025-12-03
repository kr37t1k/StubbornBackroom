import pygame
import math
import random
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

class Player:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.rotation_x = 0.0  # Vertical rotation (looking up/down)
        self.rotation_y = 0.0  # Horizontal rotation (looking left/right)
        self.speed = 0.1
        self.sensitivity = 0.2

class Enemy:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.active = True

class Simple3DGame:
    def __init__(self):
        pygame.init()
        self.width, self.height = 800, 600
        self.display = (self.width, self.height)
        pygame.display.set_mode(self.display, DOUBLEBUF | OPENGL)
        pygame.display.set_caption("Simple 3D Game - WASD to move, Mouse to aim")
        
        # Initialize GLUT for drawing shapes (must be done after pygame display init)
        glutInit()
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
        
        # Enable depth testing
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glLightfv(GL_LIGHT0, GL_POSITION, (5, 5, 5, 1))
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # Set up perspective
        gluPerspective(45, (self.display[0] / self.display[1]), 0.1, 50.0)
        glTranslatef(0.0, 0.0, -5)
        
        self.player = Player()
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Create some enemies
        self.enemies = []
        for _ in range(10):
            x = random.uniform(-10, 10)
            z = random.uniform(-10, 10)
            # Make sure enemies aren't too close to player
            while math.sqrt(x**2 + z**2) < 3:
                x = random.uniform(-10, 10)
                z = random.uniform(-10, 10)
            self.enemies.append(Enemy(x, 0, z))
        
        # Hide and grab mouse cursor
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        
        # Movement keys state
        self.keys = {
            K_w: False,
            K_s: False,
            K_a: False,
            K_d: False,
            K_UP: False,
            K_DOWN: False,
            K_LEFT: False,
            K_RIGHT: False
        }
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key in self.keys:
                    self.keys[event.key] = True
                elif event.key == K_ESCAPE:
                    self.running = False
            
            elif event.type == pygame.KEYUP:
                if event.key in self.keys:
                    self.keys[event.key] = False
            
            elif event.type == pygame.MOUSEMOTION:
                # Update player rotation based on mouse movement
                dx, dy = event.rel
                self.player.rotation_y += dx * self.player.sensitivity
                self.player.rotation_x += dy * self.player.sensitivity
                
                # Limit vertical look to avoid flipping
                self.player.rotation_x = max(-90, min(90, self.player.rotation_x))
    
    def update_player(self):
        # Calculate movement direction based on rotation
        rad_y = math.radians(self.player.rotation_y)
        forward_x = math.sin(rad_y)
        forward_z = math.cos(rad_y)
        
        right_x = math.cos(rad_y)
        right_z = -math.sin(rad_y)
        
        move_x = 0
        move_z = 0
        
        # 8-direction movement
        if self.keys[K_w]:  # Forward
            move_x += forward_x
            move_z += forward_z
        if self.keys[K_s]:  # Backward
            move_x -= forward_x
            move_z -= forward_z
        if self.keys[K_a]:  # Strafe left
            move_x -= right_x
            move_z -= right_z
        if self.keys[K_d]:  # Strafe right
            move_x += right_x
            move_z += right_z
        if self.keys[K_q]:  # Move left (alternative)
            move_x -= right_x
            move_z -= right_z
        if self.keys[K_e]:  # Move right (alternative)
            move_x += right_x
            move_z += right_z
        if self.keys[K_UP]:  # Forward (arrow key)
            move_x += forward_x
            move_z += forward_z
        if self.keys[K_DOWN]:  # Backward (arrow key)
            move_x -= forward_x
            move_z -= forward_z
        
        # Normalize diagonal movement
        if move_x != 0 and move_z != 0:
            length = math.sqrt(move_x**2 + move_z**2)
            move_x /= length
            move_z /= length
        
        # Apply movement
        self.player.x += move_x * self.player.speed
        self.player.z += move_z * self.player.speed
    
    def draw_player(self):
        glPushMatrix()
        glTranslatef(self.player.x, self.player.y, self.player.z)
        glColor3f(0.0, 1.0, 0.0)  # Green for player
        glutSolidCube(0.5)
        glPopMatrix()
    
    def draw_enemies(self):
        for enemy in self.enemies:
            if enemy.active:
                glPushMatrix()
                glTranslatef(enemy.x, enemy.y, enemy.z)
                glColor3f(1.0, 0.0, 0.0)  # Red for enemies
                glutSolidSphere(0.3, 10, 10)
                glPopMatrix()
    
    def draw_world(self):
        # Draw ground
        glBegin(GL_QUADS)
        glColor3f(0.3, 0.6, 0.3)  # Green ground
        glVertex3f(-20, -1, -20)
        glVertex3f(-20, -1, 20)
        glVertex3f(20, -1, 20)
        glVertex3f(20, -1, -20)
        glEnd()
        
        # Draw some simple walls/obstacles
        glColor3f(0.5, 0.5, 0.5)  # Gray walls
        self.draw_cube(-8, 0, 0, 0.5, 2, 4)  # Wall 1
        self.draw_cube(8, 0, 0, 0.5, 2, 4)   # Wall 2
        self.draw_cube(0, 0, -8, 4, 2, 0.5)  # Wall 3
        self.draw_cube(0, 0, 8, 4, 2, 0.5)   # Wall 4
    
    def draw_cube(self, x, y, z, width, height, depth):
        half_w, half_h, half_d = width/2, height/2, depth/2
        glPushMatrix()
        glTranslatef(x, y, z)
        glBegin(GL_QUADS)
        # Front face
        glVertex3f(-half_w, -half_h, half_d)
        glVertex3f(half_w, -half_h, half_d)
        glVertex3f(half_w, half_h, half_d)
        glVertex3f(-half_w, half_h, half_d)
        # Back face
        glVertex3f(-half_w, -half_h, -half_d)
        glVertex3f(-half_w, half_h, -half_d)
        glVertex3f(half_w, half_h, -half_d)
        glVertex3f(half_w, -half_h, -half_d)
        # Top face
        glVertex3f(-half_w, half_h, -half_d)
        glVertex3f(-half_w, half_h, half_d)
        glVertex3f(half_w, half_h, half_d)
        glVertex3f(half_w, half_h, -half_d)
        # Bottom face
        glVertex3f(-half_w, -half_h, -half_d)
        glVertex3f(half_w, -half_h, -half_d)
        glVertex3f(half_w, -half_h, half_d)
        glVertex3f(-half_w, -half_h, half_d)
        # Right face
        glVertex3f(half_w, -half_h, -half_d)
        glVertex3f(half_w, half_h, -half_d)
        glVertex3f(half_w, half_h, half_d)
        glVertex3f(half_w, -half_h, half_d)
        # Left face
        glVertex3f(-half_w, -half_h, -half_d)
        glVertex3f(-half_w, -half_h, half_d)
        glVertex3f(-half_w, half_h, half_d)
        glVertex3f(-half_w, half_h, -half_d)
        glEnd()
        glPopMatrix()
    
    def setup_camera(self):
        # Reset matrix
        glLoadIdentity()
        # Apply camera transformation
        glRotatef(-self.player.rotation_x, 1, 0, 0)  # Look up/down
        glRotatef(-self.player.rotation_y, 0, 1, 0)  # Look left/right
        glTranslatef(-self.player.x, -self.player.y, -self.player.z)  # Move camera
    
    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        self.setup_camera()
        self.draw_world()
        self.draw_enemies()
        self.draw_player()
        
        pygame.display.flip()
    
    def run(self):
        print("Controls:")
        print("- WASD or Arrow Keys: 8-direction movement")
        print("- Mouse: Look around")
        print("- ESC: Quit game")
        print("Collect the red spheres by moving over them!")
        
        while self.running:
            self.handle_events()
            self.update_player()
            
            # Simple collision detection with enemies
            for enemy in self.enemies:
                if enemy.active:
                    distance = math.sqrt(
                        (self.player.x - enemy.x)**2 + 
                        (self.player.z - enemy.z)**2
                    )
                    if distance < 0.5:  # Collision threshold
                        enemy.active = False
                        print(f"Enemy collected! {sum(1 for e in self.enemies if e.active)} left.")
            
            self.render()
            self.clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    game = Simple3DGame()
    game.run()