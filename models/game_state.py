from enum import Enum
from typing import List, Dict
from .unit import Unit, UnitType
from .combat import CombatUnit, CombatSystem
from .command import CommandSystem, Phase

class GamePhase(Enum):
    ENEMY_FIRE_SUPPRESSION = 1  # 적 화력 박멸
    ARMOR_ENGAGEMENT = 2        # 기갑 교전
    CLOSE_COMBAT = 3           # 근접전투

class GameState:
    def __init__(self):
        self.phase = Phase.FIRE_SUPPRESSION
        self.red_team: List[CombatUnit] = []
        self.blue_team: List[CombatUnit] = []
        self.combat_system = CombatSystem()
        self.command_system = CommandSystem()
        self.initialize_teams()
    
    def initialize_teams(self):
        # Red Team initialization
        self.red_team = [
            CombatUnit(Unit(UnitType.DRONE, "RED", (0, 0))) for _ in range(2)
        ] + [
            CombatUnit(Unit(UnitType.TANK, "RED", (0, 0))) for _ in range(4)
        ] + [
            CombatUnit(Unit(UnitType.ANTI_TANK, "RED", (0, 0))) for _ in range(6)
        ] + [
            CombatUnit(Unit(UnitType.INFANTRY, "RED", (0, 0))) for _ in range(24)
        ] + [
            CombatUnit(Unit(UnitType.COMMAND_POST, "RED", (0, 0)))
        ] + [
            CombatUnit(Unit(UnitType.ARTILLERY, "RED", (0, 0))) for _ in range(6)
        ]
        
        # Blue Team initialization (same structure)
        self.blue_team = [
            CombatUnit(Unit(UnitType.DRONE, "BLUE", (0, 0))) for _ in range(2)
        ] + [
            CombatUnit(Unit(UnitType.TANK, "BLUE", (0, 0))) for _ in range(4)
        ] + [
            CombatUnit(Unit(UnitType.ANTI_TANK, "BLUE", (0, 0))) for _ in range(6)
        ] + [
            CombatUnit(Unit(UnitType.INFANTRY, "BLUE", (0, 0))) for _ in range(24)
        ] + [
            CombatUnit(Unit(UnitType.COMMAND_POST, "BLUE", (0, 0)))
        ] + [
            CombatUnit(Unit(UnitType.ARTILLERY, "BLUE", (0, 0))) for _ in range(6)
        ]
    
    def get_team_combat_power(self, team: str) -> float:
        team_units = self.red_team if team == "RED" else self.blue_team
        return sum(unit.unit.combat_power for unit in team_units if unit.unit.is_alive())
    
    def check_phase_transition(self):
        # Check phase transition for both teams
        if self.command_system.evaluate_dc("RED"):
            self.command_system.transition_phase("RED")
        if self.command_system.evaluate_dc("BLUE"):
            self.command_system.transition_phase("BLUE")
    
    def update_target_lists(self):
        """Update target lists for all units"""
        # Update Red team's target lists
        for unit in self.red_team:
            self.combat_system.detect(unit, self.blue_team)
            self.combat_system.available_target(unit)
        
        # Update Blue team's target lists
        for unit in self.blue_team:
            self.combat_system.detect(unit, self.red_team)
            self.combat_system.available_target(unit)
    
    def process_combat(self):
        """Process combat for all units"""
        # Process Red team's combat
        for unit in self.red_team:
            self.combat_system.finding_target(unit)
        
        # Process Blue team's combat
        for unit in self.blue_team:
            self.combat_system.finding_target(unit)
    
    def get_fire_priority(self) -> List[UnitType]:
        """Get fire priority based on current phase"""
        command = self.command_system.red_command  # Using Red team's command as reference
        if command.phase == Phase.FIRE_SUPPRESSION:
            return [
                UnitType.ARTILLERY,
                UnitType.COMMAND_POST,
                UnitType.TANK,
                UnitType.ANTI_TANK,
                UnitType.INFANTRY
            ]
        elif command.phase == Phase.ARMOR_ENGAGEMENT:
            return [
                UnitType.TANK,
                UnitType.COMMAND_POST,
                UnitType.ARTILLERY,
                UnitType.ANTI_TANK,
                UnitType.INFANTRY
            ]
        else:  # CLOSE_COMBAT
            return [
                UnitType.TANK,
                UnitType.COMMAND_POST,
                UnitType.ANTI_TANK,
                UnitType.INFANTRY,
                UnitType.ARTILLERY
            ] 