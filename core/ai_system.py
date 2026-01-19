"""
Advanced AI System for Enemies
Implements state machines, pathfinding, and tactical behaviors
"""

from .engine import Component, GameObject
import math
import random
from enum import Enum
from ursina import Vec3, raycast
import numpy as np


class AIState(Enum):
    IDLE = "idle"
    PATROL = "patrol"
    CHASE = "chase"
    ATTACK = "attack"
    FLEE = "flee"
    SEARCH = "search"


class AIBehavior(Enum):
    AGGRESSIVE = "aggressive"
    CAUTIOUS = "cautious"
    AMBUSH = "ambush"
    PATROL = "patrol"


class EnemyAI(Component):
    """Advanced enemy AI with state machine and tactical behaviors"""
    def __init__(self, ai_behavior=AIBehavior.AGGRESSIVE, detection_range=15.0, attack_range=3.0):
        super().__init__()
        self.ai_behavior = ai_behavior
        self.detection_range = detection_range
        self.attack_range = attack_range
        self.state = AIState.IDLE
        self.target = None  # Reference to player or other target
        self.health = 100
        self.max_health = 100
        self.damage = 25
        self.speed = self._get_speed_for_behavior(ai_behavior)
        self.field_of_view = 90  # Degrees
        
        # Patrol state variables
        self.patrol_points = []
        self.current_patrol_index = 0
        self.return_to_patrol = True
        
        # Chase state variables
        self.last_known_player_pos = None
        self.chase_timer = 0
        self.search_duration = 10  # seconds to search before giving up
        
        # Attack state variables
        self.attack_cooldown = 0
        self.attack_delay = 1.0  # seconds between attacks
        
        # Flee state variables
        self.flee_threshold = 0.3  # health percentage below which enemy flees
    
    def _get_speed_for_behavior(self, behavior):
        """Get speed based on AI behavior type"""
        speeds = {
            AIBehavior.AGGRESSIVE: 3.0,
            AIBehavior.CAUTIOUS: 1.5,
            AIBehavior.AMBUSH: 2.0,
            AIBehavior.PATROL: 2.0
        }
        return speeds.get(behavior, 2.0)
    
    def update(self, dt):
        """Main AI update loop"""
        # Update cooldowns
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        
        # Update chase timer
        if self.state == AIState.CHASE:
            self.chase_timer += dt
        
        # Update state based on conditions
        self._update_state()
        
        # Execute behavior based on current state
        self._execute_state(dt)
    
    def _update_state(self):
        """Determine and transition to appropriate state"""
        player_pos = self._get_player_position()
        if player_pos is None:
            # No player detected, maybe return to patrol
            if self.return_to_patrol and self.patrol_points:
                self.state = AIState.PATROL
            else:
                self.state = AIState.IDLE
            return
        
        # Calculate distance to player
        distance_to_player = self._distance_to(player_pos)
        
        # Check if we can see the player
        can_see_player = self._can_see_player(player_pos)
        
        # State transition logic
        if self.health / self.max_health < self.flee_threshold:
            self.state = AIState.FLEE
        elif distance_to_player <= self.attack_range and can_see_player:
            self.state = AIState.ATTACK
        elif distance_to_player <= self.detection_range and can_see_player:
            self.state = AIState.CHASE
            self.last_known_player_pos = player_pos
            self.chase_timer = 0
        elif self.state == AIState.CHASE and self.chase_timer > self.search_duration:
            # Player lost, search for a bit then return to patrol
            self.state = AIState.SEARCH
        elif self.state == AIState.SEARCH:
            # Continue searching for a bit more
            self.chase_timer += 1  # We reuse chase_timer for search tracking
            if self.chase_timer > self.search_duration + 5:  # Search for 5 more seconds
                if self.return_to_patrol and self.patrol_points:
                    self.state = AIState.PATROL
                else:
                    self.state = AIState.IDLE
        elif self.state == AIState.FLEE and self.health / self.max_health > 0.5:
            # If health recovered enough, stop fleeing
            if self.return_to_patrol and self.patrol_points:
                self.state = AIState.PATROL
            else:
                self.state = AIState.IDLE
    
    def _execute_state(self, dt):
        """Execute behavior based on current state"""
        if self.state == AIState.IDLE:
            self._idle_behavior(dt)
        elif self.state == AIState.PATROL:
            self._patrol_behavior(dt)
        elif self.state == AIState.CHASE:
            self._chase_behavior(dt)
        elif self.state == AIState.ATTACK:
            self._attack_behavior(dt)
        elif self.state == AIState.FLEE:
            self._flee_behavior(dt)
        elif self.state == AIState.SEARCH:
            self._search_behavior(dt)
    
    def _idle_behavior(self, dt):
        """Behavior when in idle state"""
        # Just stand in place, maybe look around occasionally
        if random.random() < 0.01:  # Small chance to look around
            self._look_at(Vec3(
                self.owner.transform.position.x + random.uniform(-5, 5),
                self.owner.transform.position.y,
                self.owner.transform.position.z + random.uniform(-5, 5)
            ))
    
    def _patrol_behavior(self, dt):
        """Behavior when patrolling"""
        if not self.patrol_points:
            return
        
        # Get current patrol target
        target_point = self.patrol_points[self.current_patrol_index]
        
        # Move towards target
        direction = target_point - self.owner.transform.position
        distance = direction.length()
        
        if distance < 1.0:  # Close enough to target
            # Move to next patrol point
            self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)
        else:
            # Move towards target
            direction.normalize()
            self.owner.transform.position += direction * self.speed * dt
            self._look_at(target_point)
    
    def _chase_behavior(self, dt):
        """Behavior when chasing player"""
        player_pos = self._get_player_position()
        if player_pos is None:
            return
        
        direction = player_pos - self.owner.transform.position
        direction.y = 0  # Keep movement on horizontal plane
        distance = direction.length()
        
        if distance > 0:
            direction.normalize()
            self.owner.transform.position += direction * self.speed * dt
            self._look_at(player_pos)
    
    def _attack_behavior(self, dt):
        """Behavior when attacking player"""
        if self.attack_cooldown <= 0:
            self._perform_attack()
            self.attack_cooldown = self.attack_delay
    
    def _flee_behavior(self, dt):
        """Behavior when fleeing from danger"""
        player_pos = self._get_player_position()
        if player_pos is None:
            return
        
        # Move away from player
        direction = self.owner.transform.position - player_pos
        direction.y = 0
        if direction.length() > 0:
            direction.normalize()
            self.owner.transform.position += direction * self.speed * dt
            self._look_away_from(player_pos)
    
    def _search_behavior(self, dt):
        """Behavior when searching for lost target"""
        # Wander around the last known position
        if self.last_known_player_pos:
            # Move in a random direction near the last known position
            offset = Vec3(
                random.uniform(-3, 3),
                0,
                random.uniform(-3, 3)
            )
            target = self.last_known_player_pos + offset
            
            direction = target - self.owner.transform.position
            distance = direction.length()
            
            if distance > 0.5:  # Not at target yet
                direction.normalize()
                self.owner.transform.position += direction * self.speed * 0.5 * dt
                self._look_at(target)
    
    def _perform_attack(self):
        """Perform attack action"""
        # This could be shooting, melee, or other attack
        player = self._get_player_reference()
        if player:
            # Apply damage to player
            if hasattr(player, 'take_damage'):
                player.take_damage(self.damage)
            else:
                # Alternative way to apply damage if no take_damage method
                if hasattr(player, 'health'):
                    player.health -= self.damage
    
    def _can_see_player(self, player_pos):
        """Check if enemy can see the player"""
        if not player_pos:
            return False
        
        # Check if player is within field of view
        direction_to_player = player_pos - self.owner.transform.position
        distance_to_player = direction_to_player.length()
        
        if distance_to_player > self.detection_range:
            return False
        
        # Calculate angle between enemy forward direction and player
        forward = self.owner.transform.get_forward_vector()
        direction_to_player.y = 0  # Ignore vertical difference
        forward.y = 0
        
        if forward.length() > 0 and direction_to_player.length() > 0:
            forward.normalize()
            direction_to_player.normalize()
            
            dot_product = forward.dot(direction_to_player)
            angle = math.degrees(math.acos(max(-1, min(1, dot_product))))
            
            if angle > self.field_of_view / 2:
                return False
        
        # Raycast to check for obstacles
        hit_info = raycast(
            self.owner.transform.position + Vec3(0, 1, 0),  # Eye level
            direction_to_player,
            distance=distance_to_player,
            exclude_entities=[self.owner]
        )
        
        # If we hit the player specifically, we can see them
        return hit_info and hit_info.entity and self._is_player_entity(hit_info.entity)
    
    def _distance_to(self, other_pos):
        """Calculate distance to another position"""
        diff = self.owner.transform.position - other_pos
        diff.y = 0  # Only consider horizontal distance
        return diff.length()
    
    def _get_player_position(self):
        """Get the player's current position"""
        player = self._get_player_reference()
        if player and hasattr(player, 'transform'):
            return player.transform.position
        return None
    
    def _get_player_reference(self):
        """Get reference to player object"""
        # This would depend on how you store player reference
        # For now, assuming it's stored in a global variable or accessible somehow
        # In a real implementation, this might be passed through the game manager
        if hasattr(self.owner, 'game_manager') and hasattr(self.owner.game_manager, 'player'):
            return self.owner.game_manager.player
        return None
    
    def _is_player_entity(self, entity):
        """Check if an entity is the player"""
        # This depends on how you identify player entities
        # Could check by name, tag, or component
        if hasattr(entity, 'is_player'):
            return entity.is_player
        if hasattr(entity, 'name') and 'player' in entity.name.lower():
            return True
        return False
    
    def _look_at(self, target_pos):
        """Make the enemy look at a target position"""
        direction = target_pos - self.owner.transform.position
        direction.y = 0  # Keep rotation on horizontal plane
        
        if direction.length() > 0:
            direction.normalize()
            # Calculate yaw based on direction
            yaw = math.degrees(math.atan2(-direction.x, -direction.z))
            self.owner.transform.rotation = Vec3(0, yaw, 0)
    
    def _look_away_from(self, target_pos):
        """Make the enemy look away from a target position"""
        direction = self.owner.transform.position - target_pos
        direction.y = 0
        
        if direction.length() > 0:
            direction.normalize()
            # Calculate yaw based on opposite direction
            yaw = math.degrees(math.atan2(-direction.x, -direction.z))
            self.owner.transform.rotation = Vec3(0, yaw, 0)
    
    def take_damage(self, amount):
        """Apply damage to the enemy"""
        self.health -= amount
        if self.health <= 0:
            self.die()
    
    def die(self):
        """Handle enemy death"""
        print(f"{self.owner.name} died!")
        # In a real game, this might trigger death animation, drop loot, etc.
        if self.owner:
            self.owner.active = False  # Deactivate the game object


class TacticalAI(EnemyAI):
    """More advanced AI with tactical awareness and team coordination"""
    def __init__(self, ai_behavior=AIBehavior.AGGRESSIVE, detection_range=15.0, attack_range=3.0):
        super().__init__(ai_behavior, detection_range, attack_range)
        self.team_id = None
        self.teammates = []
        self.tactical_position = None
        self.cover_points = []
        self.has_flanked = False
    
    def update(self, dt):
        """Tactical AI update with team awareness"""
        # Consider teammate positions and tactical objectives
        self._consider_tactical_positions()
        super().update(dt)
    
    def _consider_tactical_positions(self):
        """Consider better positions based on team tactics"""
        # This would implement flanking, covering teammates, etc.
        pass


class AITeamManager:
    """Manages groups of AI enemies working together"""
    def __init__(self):
        self.teams = {}
        self.all_enemies = []
    
    def add_enemy_to_team(self, enemy_ai, team_id):
        """Add an enemy to a team"""
        enemy_ai.team_id = team_id
        
        if team_id not in self.teams:
            self.teams[team_id] = []
        
        self.teams[team_id].append(enemy_ai)
        self.all_enemies.append(enemy_ai)
        
        # Update teammate references
        for other_enemy in self.teams[team_id]:
            if other_enemy != enemy_ai:
                if enemy_ai not in other_enemy.teammates:
                    other_enemy.teammates.append(enemy_ai)
                if other_enemy not in enemy_ai.teammates:
                    enemy_ai.teammates.append(other_enemy)
    
    def update_all(self, dt):
        """Update all enemies in all teams"""
        for enemy in self.all_enemies:
            if enemy.active:
                enemy.update(dt)