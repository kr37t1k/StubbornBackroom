# raycaster.py - COMPLETELY FIXED: Working 3D raycasting
import math
import random


class Raycaster:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.fov = math.pi / 3  # 60 degrees
        self.ray_angle_step = self.fov / width

        # Color palette (soft, dreamy colors)
        self.colors = {
            'walls': [
                (240, 220, 180),  # Cream walls
                (230, 210, 170),  # Slightly darker
                (220, 200, 160),  # Even darker
                (255, 245, 220),  # Light cream
            ],
            'floors': [
                (250, 240, 210),  # Pale yellow floor
                (255, 250, 230),  # Lighter
            ],
            'ceilings': [
                (255, 255, 245),  # Almost white ceiling
                (250, 250, 240),  # Slightly warm
            ],
            'fog': (200, 180, 150)  # Warm fog
        }

        self.wave_offset = 0
        self.flicker_intensity = 0.0

    def cast_rays(self, player_x, player_y, player_angle, world, draw_distance=10):
        """Cast rays and return render data"""
        rays = []
        half_fov = self.fov / 2

        for x in range(self.width):
            # Calculate ray angle - ✅ FIXED: Correct angle calculation
            ray_angle = player_angle + (x / self.width - 0.5) * self.fov

            # Cast ray - ✅ FIXED: Correct ray casting
            distance, wall_type, side = self._cast_single_ray(
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
                'fog_factor': fog_factor
            })

        self.wave_offset += 0.03
        self.flicker_intensity = math.sin(self.wave_offset * 2) * 0.1

        return rays

    def _cast_single_ray(self, start_x, start_y, angle, world, max_distance):
        """✅ COMPLETELY REWRITTEN: Working DDA raycaster"""
        # Ray direction - ✅ FIXED: cos for x, sin for y
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
                # ✅ FIXED: Use world.get_cell() with proper bounds
                if abs(map_x) < 1000 and abs(map_y) < 1000:
                    wall_type = world.get_cell(map_x, map_y)
                    if wall_type > 0:
                        hit = True
                        # Calculate exact distance
                        if side == 'x':
                            distance = abs((map_x - start_x + (0 if step_x > 0 else 1)) / ray_dir_x)
                        else:
                            distance = abs((map_y - start_y + (0 if step_y > 0 else 1)) / ray_dir_y)
                else:
                    # Too far away - treat as open space
                    wall_type = 0
            except:
                wall_type = 0

            # Safety break
            if abs(map_x) > 2000 or abs(map_y) > 2000:
                distance = max_distance
                wall_type = 0
                break

        if not hit:
            distance = max_distance
            wall_type = 0

        return distance, wall_type, side

    def get_wall_color(self, wall_type, ray_data):
        """Get wall color with dream effects"""
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