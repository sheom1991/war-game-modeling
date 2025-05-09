import rasterio
import numpy as np
from typing import Tuple, Optional
from dataclasses import dataclass

@dataclass
class TerrainEffects:
    movement_speed: float  # Movement speed multiplier
    detection_prob: float  # Detection probability multiplier
    kill_prob: float      # Kill probability multiplier

class TerrainSystem:
    def __init__(self, dem_file: str = "database/36710.img"):
        # Load DEM data
        with rasterio.open(dem_file) as src:
            self.dem_data = src.read(1)
            self.transform = src.transform
            self.crs = src.crs
        
        # Terrain thresholds
        self.mountain_threshold = 50.0  # meters
        self.water_threshold = 40.0     # meters
        
        # Terrain effect weights
        self.decay_weight_mount = 0.5   # Mountain effect weight
        self.decay_weight_water = 0.3   # Water effect weight
        
        # Unit type specific effects
        self.unit_terrain_effects = {
            "DRONE": TerrainEffects(1.0, 1.0, 1.0),      # Drones unaffected by terrain
            "TANK": TerrainEffects(0.7, 0.8, 1.0),       # Tanks affected by terrain
            "ANTI_TANK": TerrainEffects(0.8, 0.9, 1.0),  # Anti-tank units
            "INFANTRY": TerrainEffects(0.9, 0.9, 1.0),   # Infantry
            "COMMAND_POST": TerrainEffects(0.8, 0.8, 1.0), # Command post
            "ARTILLERY": TerrainEffects(0.7, 0.8, 1.0)   # Artillery
        }
    
    def get_elevation(self, x: int, y: int) -> float:
        """Get elevation at given coordinates"""
        if 0 <= y < self.dem_data.shape[0] and 0 <= x < self.dem_data.shape[1]:
            return self.dem_data[y, x]
        return 0.0
    
    def get_terrain_effects(self, x: int, y: int, unit_type: str) -> TerrainEffects:
        """Get terrain effects for a unit at given coordinates"""
        elevation = self.get_elevation(x, y)
        base_effects = self.unit_terrain_effects[unit_type]
        
        # Calculate terrain modifiers
        if elevation > self.mountain_threshold:
            mountain_modifier = (elevation - self.mountain_threshold) * self.decay_weight_mount
            return TerrainEffects(
                movement_speed=base_effects.movement_speed * (1 - mountain_modifier),
                detection_prob=base_effects.detection_prob * (1 - mountain_modifier),
                kill_prob=base_effects.kill_prob * (1 - mountain_modifier)
            )
        elif elevation < self.water_threshold:
            water_modifier = (self.water_threshold - elevation) * self.decay_weight_water
            return TerrainEffects(
                movement_speed=base_effects.movement_speed * (1 - water_modifier),
                detection_prob=base_effects.detection_prob * (1 - water_modifier),
                kill_prob=base_effects.kill_prob * (1 - water_modifier)
            )
        
        return base_effects
    
    def check_line_of_sight(self, start: Tuple[int, int], end: Tuple[int, int]) -> bool:
        """Check if there is line of sight between two points"""
        x1, y1 = start
        x2, y2 = end
        
        # Bresenham's line algorithm to check points between start and end
        points = self._get_line_points(x1, y1, x2, y2)
        
        # Get elevation at start and end points
        start_elev = self.get_elevation(x1, y1)
        end_elev = self.get_elevation(x2, y2)
        
        # Check if any point along the line is higher than both endpoints
        for x, y in points:
            if x == x1 and y == y1 or x == x2 and y == y2:
                continue
                
            point_elev = self.get_elevation(x, y)
            if point_elev > max(start_elev, end_elev):
                return False
        
        return True
    
    def _get_line_points(self, x1: int, y1: int, x2: int, y2: int) -> list:
        """Get all points along a line using Bresenham's algorithm"""
        points = []
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        x, y = x1, y1
        n = 1 + dx + dy
        x_inc = 1 if x2 > x1 else -1
        y_inc = 1 if y2 > y1 else -1
        error = dx - dy
        dx *= 2
        dy *= 2

        for _ in range(n):
            points.append((x, y))
            if error > 0:
                x += x_inc
                error -= dy
            else:
                y += y_inc
                error += dx

        return points
    
    def get_initial_positions(self) -> dict:
        """Get initial positions for both teams"""
        # Define initial positions for each team
        # These are example positions - adjust based on your requirements
        return {
            "RED": {
                "DRONE": [(10, 10), (15, 10)],
                "TANK": [(20, 20), (25, 20), (30, 20), (35, 20)],
                "ANTI_TANK": [(40, 30), (45, 30), (50, 30), (55, 30), (60, 30), (65, 30)],
                "INFANTRY": [(70, 40) + (i, i) for i in range(24)],
                "COMMAND_POST": [(100, 50)],
                "ARTILLERY": [(120, 60), (125, 60), (130, 60), (135, 60), (140, 60), (145, 60)]
            },
            "BLUE": {
                "DRONE": [(150, 300), (155, 300)],
                "TANK": [(140, 290), (145, 290), (150, 290), (155, 290)],
                "ANTI_TANK": [(130, 280), (135, 280), (140, 280), (145, 280), (150, 280), (155, 280)],
                "INFANTRY": [(120, 270) + (i, i) for i in range(24)],
                "COMMAND_POST": [(100, 260)],
                "ARTILLERY": [(80, 250), (85, 250), (90, 250), (95, 250), (100, 250), (105, 250)]
            }
        } 