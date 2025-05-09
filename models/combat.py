from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Set
import numpy as np
from .unit import Unit, UnitType
from .probabilities import ProbabilitySystem, TargetState, DamageType, TankDamageType

class UnitState(Enum):
    ALIVE = "Alive"
    M_KILL = "M-kill"  # Mobility kill
    F_KILL = "F-kill"  # Firepower kill
    K_KILL = "K-kill"  # Complete kill

class Action(Enum):
    MANEUVER = "Maneuver"
    FIRE = "Fire"
    STOP = "Stop"

@dataclass
class CombatUnit:
    unit: Unit
    state: UnitState = UnitState.ALIVE
    action: Action = Action.STOP
    target_list: Set[Unit] = None
    eligible_target_list: Set[Unit] = None
    is_moving: bool = False
    is_defilade: bool = False
    
    def __post_init__(self):
        if self.target_list is None:
            self.target_list = set()
        if self.eligible_target_list is None:
            self.eligible_target_list = set()
    
    def get_target_state(self) -> TargetState:
        """Get the current target state based on movement and defilade status"""
        if self.is_defilade:
            return TargetState.DS if not self.is_moving else TargetState.DM
        return TargetState.ES if not self.is_moving else TargetState.EM

class CombatSystem:
    def __init__(self, probability_system: ProbabilitySystem = None):
        self.fel = []  # Future Event List
        self.world = None  # Will be set by GameState
        self.prob_system = probability_system or ProbabilitySystem()
        self.distance_rescale = 1.0
    
    def set_distance_rescale(self, scale: float):
        self.distance_rescale = scale
    
    def los(self, coordinates: Tuple[float, float]) -> bool:
        """Line of Sight analysis for given coordinates"""
        # TODO: Implement terrain-based LOS calculation
        return True
    
    def detect(self, unit: CombatUnit, enemy_units: List[CombatUnit]):
        """Detect enemy units based on LOS and detection rules"""
        unit.target_list.clear()
        for enemy in enemy_units:
            if self.los(enemy.unit.position):
                # Add detection probability logic here
                unit.target_list.add(enemy.unit)
    
    def available_target(self, unit: CombatUnit):
        """Determine eligible targets based on weapon characteristics"""
        unit.eligible_target_list.clear()
        for target in unit.target_list:
            if self._is_valid_target(unit.unit, target):
                unit.eligible_target_list.add(target)
    
    def _is_valid_target(self, attacker: Unit, target: Unit) -> bool:
        """Check if target is valid for the attacker's weapon system"""
        if attacker.unit_type == UnitType.ANTI_TANK:
            return target.unit_type in [UnitType.TANK, UnitType.INFANTRY]
        return True
    
    def finding_target(self, unit: CombatUnit):
        """Target selection logic"""
        if unit.state in [UnitState.ALIVE, UnitState.M_KILL] and unit.action == Action.STOP:
            if unit.eligible_target_list:
                unit.action = Action.FIRE
                target = self._select_target(unit)
                if target:
                    self._schedule_fire(unit, target)
    
    def _select_target(self, unit: CombatUnit) -> Unit:
        """Select target based on unit type and priority"""
        if not unit.eligible_target_list:
            return None
            
        if unit.unit.unit_type == UnitType.ARTILLERY:
            # Artillery target selection based on fire priority
            return self._select_artillery_target(unit)
        else:
            # Direct fire weapons select closest target
            return self._select_direct_fire_target(unit)
    
    def _select_artillery_target(self, unit: CombatUnit) -> Unit:
        """Select target for artillery based on fire priority"""
        # TODO: Implement fire priority and friendly fire consideration
        return next(iter(unit.eligible_target_list))
    
    def _select_direct_fire_target(self, unit: CombatUnit) -> Unit:
        """Select closest target for direct fire weapons"""
        if not unit.eligible_target_list:
            return None
        return min(unit.eligible_target_list, 
                  key=lambda t: self._calculate_distance(unit.unit.position, t.position))
    
    def _calculate_distance(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between two positions in background.png pixel coordinates"""
        d = np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
        return d * self.distance_rescale
    
    def _schedule_fire(self, unit: CombatUnit, target: Unit):
        """Schedule fire event in FEL"""
        # TODO: Implement fire scheduling with timing
        pass
    
    def fire(self, unit: CombatUnit, target: Unit):
        """Execute fire event"""
        if target not in unit.eligible_target_list:
            return
            
        if unit.unit.unit_type == UnitType.ARTILLERY:
            self._artillery_fire(unit, target)
        else:
            self._direct_fire(unit, target)
            
        unit.action = Action.STOP
    
    def _artillery_fire(self, unit: CombatUnit, target: Unit):
        """Execute artillery fire"""
        # TODO: Implement artillery fire mechanics
        pass
    
    def _direct_fire(self, unit: CombatUnit, target: Unit):
        """Execute direct fire"""
        distance = self._calculate_distance(unit.unit.position, target.position)
        
        # Get hit probability
        weapon_type = "rifle" if unit.unit.unit_type == UnitType.INFANTRY else "tank"
        hit_prob = self.prob_system.get_hit_probability(
            weapon_type, 
            distance, 
            target.get_target_state()
        )
        
        # Check if hit
        if np.random.random() <= hit_prob:
            if weapon_type == "rifle":
                self._process_rifle_damage(unit, target, distance)
            else:
                self._process_tank_damage(unit, target)
    
    def _process_rifle_damage(self, unit: CombatUnit, target: Unit, distance: float):
        """Process rifle damage"""
        damage_type = self.prob_system.determine_rifle_damage(
            distance,
            target.get_target_state()
        )
        
        # Apply damage based on type
        if damage_type == DamageType.FATAL:
            target.state = UnitState.K_KILL
        elif damage_type == DamageType.CRITICAL:
            target.state = UnitState.F_KILL
        elif damage_type == DamageType.SERIOUS:
            target.state = UnitState.M_KILL
    
    def _process_tank_damage(self, unit: CombatUnit, target: Unit):
        """Process tank damage"""
        damage_type = self.prob_system.determine_tank_damage(
            target.get_target_state()
        )
        
        # Apply damage based on type
        if damage_type == TankDamageType.COMPLETE:
            target.state = UnitState.K_KILL
        elif damage_type == TankDamageType.FIREPOWER:
            target.state = UnitState.F_KILL
        elif damage_type == TankDamageType.MOBILITY:
            target.state = UnitState.M_KILL
    
    def is_in_range(self, unit: CombatUnit, target: CombatUnit) -> bool:
        """Check if target is within weapon range"""
        distance = self._calculate_distance(unit.unit.position, target.unit.position)
        
        # Define weapon ranges
        weapon_ranges = {
            UnitType.INFANTRY: 500,  # meters
            UnitType.TANK: 2000,     # meters
            UnitType.ANTI_TANK: 1500,# meters
            UnitType.ARTILLERY: 5000, # meters
            UnitType.DRONE: 1000,    # meters
            UnitType.COMMAND_POST: 100# meters
        }
        
        return distance <= weapon_ranges[unit.unit.unit_type]
    
    def calculate_hit_probability(self, unit: CombatUnit, target: CombatUnit) -> float:
        """Calculate hit probability based on weapon type, distance, and target state"""
        distance = self._calculate_distance(unit.unit.position, target.unit.position)
        target_state = target.get_target_state()
        
        # Get weapon type
        weapon_type = "rifle" if unit.unit.unit_type == UnitType.INFANTRY else "tank"
        
        return self.prob_system.get_hit_probability(weapon_type, distance, target_state)
        
    def process_damage(self, unit: CombatUnit, target: CombatUnit) -> float:
        """Calculate and process damage"""
        distance = self._calculate_distance(unit.unit.position, target.unit.position)
        target_state = target.get_target_state()
        
        if unit.unit.unit_type == UnitType.INFANTRY:
            damage_type = self.prob_system.determine_rifle_damage(distance, target_state)
            # Convert damage type to numeric value
            damage_values = {
                DamageType.MINOR: 10,
                DamageType.SERIOUS: 30,
                DamageType.CRITICAL: 60,
                DamageType.FATAL: 100
            }
            return damage_values[damage_type]
        else:
            damage_type = self.prob_system.determine_tank_damage(target_state)
            # Convert damage type to numeric value
            damage_values = {
                TankDamageType.MOBILITY: 30,
                TankDamageType.FIREPOWER: 50,
                TankDamageType.TURRET: 70,
                TankDamageType.COMPLETE: 100
            }
            return damage_values[damage_type] 