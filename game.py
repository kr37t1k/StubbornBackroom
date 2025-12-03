# main.py - FIXED: Working movement and rendering
import pygame
import math
import random
import sys
from raycast import Raycaster
from advanced_raycast import AdvancedRaycaster, PygameRaycastRenderer
from world import BackroomsWorld
from player import DreamPlayer
from audio import BackgroundMusic

# There must be stable main game script

# Initialize pygame
pygame.init()
WIDTH, HEIGHT = 1024, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("StubbornBackroom: Psycho Dream")
clock = pygame.time.Clock()

# Create game objects
raycaster = AdvancedRaycaster(WIDTH, HEIGHT)  # Use advanced raycaster
pygame_renderer = PygameRaycastRenderer(WIDTH, HEIGHT)  # Advanced pygame renderer
world = BackroomsWorld(seed=42)

# Run background music
music = BackgroundMusic()
music.play_audio()

# ✅ FIXED: Start player in open space (not inside wall)
player = DreamPlayer(x=5.5, y=5.5, angle=0)  # Start in open area

# Font for UI
font = pygame.font.SysFont('Arial', 24)
small_font = pygame.font.SysFont('Arial', 16)

# Dream state messages
dream_messages = [
    "you are safe here...",
    "the walls breathe softly...",
    "listen to the hum...",
    "time flows like honey...",
    "reality is gentle...",
    "you belong here...",
    "the dream protects you...",
    "soft edges, soft mind...",
]

current_message = random.choice(dream_messages)
message_timer = 0


def render_3d_view(rays):
    """Enhanced 3D rendering using the advanced renderer"""
    pygame_renderer.render_3d_view(rays, screen, player.x, player.y, player.angle)


def render_ui():
    """Render user interface"""
    global current_message, message_timer
    message_timer += 1
    if message_timer > 300:
        current_message = random.choice(dream_messages)
        message_timer = 0

    # Dream message (larger and more visible)
    message_surface = font.render(f"💭 {current_message}", True, (255, 230, 200))
    screen.blit(message_surface, (20, 20))

    # Player status (more readable)
    status_lines = [
        f"POS: {player.x:.1f}, {player.y:.1f}",
        f"DREAM: {player.dream_level:.1f}",
        f"SANITY: {player.sanity:.0f}%"
    ]

    for i, line in enumerate(status_lines):
        text = small_font.render(line, True, (240, 220, 200))
        screen.blit(text, (20, HEIGHT - 80 + i * 25))

    # Controls (more visible)
    controls = small_font.render(
        "WASD: Move | ESC: Quit | Arrows: Turn",
        True, (230, 210, 190)
    )
    screen.blit(controls, (WIDTH - controls.get_width() - 20, HEIGHT - 30))


def main():
    print("Soft Backrooms: Cute Psycho Dream")
    print("WASD to move, ARROW KEYS to turn, ESC to quit")

    running = True
    keys_pressed = set()

    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_w:
                    keys_pressed.add('w')
                elif event.key == pygame.K_s:
                    keys_pressed.add('s')
                elif event.key == pygame.K_a:
                    keys_pressed.add('a')
                elif event.key == pygame.K_d:
                    keys_pressed.add('d')
                elif event.key == pygame.K_LEFT:
                    keys_pressed.add('left')
                elif event.key == pygame.K_RIGHT:
                    keys_pressed.add('right')
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    keys_pressed.discard('w')
                elif event.key == pygame.K_s:
                    keys_pressed.discard('s')
                elif event.key == pygame.K_a:
                    keys_pressed.discard('a')
                elif event.key == pygame.K_d:
                    keys_pressed.discard('d')
                elif event.key == pygame.K_LEFT:
                    keys_pressed.discard('left')
                elif event.key == pygame.K_RIGHT:
                    keys_pressed.discard('right')

        # ✅ FIXED: Update player with proper key handling
        dt = clock.get_time() / 16.67
        player.update(keys_pressed, world, dt)

        # Cast rays
        px, py = player.get_render_position()
        rays = raycaster.cast_rays(px, py, player.angle, world, draw_distance=15)

        # Render
        render_3d_view(rays)
        render_ui()

        # Update display
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()