from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Dict
from .unit import UnitType

class Phase(Enum):
    FIRE_SUPPRESSION = 1  # 적 화력 박멸
    ARMOR_ENGAGEMENT = 2  # 기갑 교전
    CLOSE_COMBAT = 3      # 근접전투

@dataclass
class Command:
    phase: Phase
    team: str  # "RED" or "BLUE"
    tir: Tuple[float, float]  # Drone reconnaissance area
    fire_priority: List[int]  # Fire support priority
    maneuver_objective: Tuple[float, float]  # Phase-specific maneuver objective
    
    @classmethod
    def create_phase_1_command(cls, team: str):
        return cls(
            phase=Phase.FIRE_SUPPRESSION,
            team=team,
            tir=(0, 0),  # TODO: Set actual coordinates
            fire_priority=[1, 2, 3, 4, 5],  # Artillery > Command > Armor > Anti-tank > Infantry
            maneuver_objective=(0, 0)  # TODO: Set actual coordinates
        )
    
    @classmethod
    def create_phase_2_command(cls, team: str):
        return cls(
            phase=Phase.ARMOR_ENGAGEMENT,
            team=team,
            tir=(0, 0),  # TODO: Set actual coordinates
            fire_priority=[3, 2, 1, 4, 5],  # Armor > Command > Artillery > Anti-tank > Infantry
            maneuver_objective=(0, 0)  # TODO: Set actual coordinates
        )
    
    @classmethod
    def create_phase_3_command(cls, team: str):
        return cls(
            phase=Phase.CLOSE_COMBAT,
            team=team,
            tir=(0, 0),  # TODO: Set actual coordinates
            fire_priority=[3, 2, 4, 5, 1],  # Armor > Command > Anti-tank > Infantry > Artillery
            maneuver_objective=(0, 0)  # TODO: Set actual coordinates
        )

class CommandSystem:
    def __init__(self):
        self.red_command: Command = None
        self.blue_command: Command = None
        self.initialize_commands()
    
    def initialize_commands(self):
        self.red_command = Command.create_phase_1_command("RED")
        self.blue_command = Command.create_phase_1_command("BLUE")
    
    def evaluate_dc(self, team: str) -> bool:
        """Evaluate Decision Criteria for phase transition"""
        command = self.red_command if team == "RED" else self.blue_command
        
        if command.phase == Phase.FIRE_SUPPRESSION:
            # DC1: Check if 4 or more enemy artillery units are F-kill or K-kill
            return self._check_dc1(team)
        elif command.phase == Phase.ARMOR_ENGAGEMENT:
            # DC2: Check if 2 or more enemy tanks are F-kill or K-kill
            return self._check_dc2(team)
        return False
    
    def _check_dc1(self, team: str) -> bool:
        """Check Decision Criteria 1: Enemy artillery destruction"""
        # TODO: Implement actual check
        return False
    
    def _check_dc2(self, team: str) -> bool:
        """Check Decision Criteria 2: Enemy tank destruction"""
        # TODO: Implement actual check
        return False
    
    def transition_phase(self, team: str):
        """Transition to next phase"""
        command = self.red_command if team == "RED" else self.blue_command
        
        if command.phase == Phase.FIRE_SUPPRESSION:
            command = Command.create_phase_2_command(team)
        elif command.phase == Phase.ARMOR_ENGAGEMENT:
            command = Command.create_phase_3_command(team)
        
        if team == "RED":
            self.red_command = command
        else:
            self.blue_command = command 