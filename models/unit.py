from enum import Enum
from dataclasses import dataclass
from typing import Optional, Tuple

class UnitType(Enum):
    DRONE = "드론"
    TANK = "전차"
    ANTI_TANK = "대전차"
    INFANTRY = "개인화기"
    COMMAND_POST = "전방지휘소"
    ARTILLERY = "곡사화기"

class UnitState(Enum):
    ALIVE = "생존"
    K_KILL = "K-kill"
    FIRE = "발사"
    STOP = "정지"
    MOVING = "이동"

@dataclass
class Unit:
    unit_type: UnitType
    team: str  # "RED" or "BLUE"
    position: Tuple[float, float]
    health: float = 100.0
    combat_power: float = 100.0
    state: UnitState = UnitState.ALIVE
    action: UnitState = UnitState.STOP
    id: Optional[str] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = f"{self.team}_{self.unit_type.name}"
    
    def is_alive(self) -> bool:
        return self.health > 0 and self.state != UnitState.K_KILL
    
    def take_damage(self, damage: float):
        self.health = max(0, self.health - damage)
        self.combat_power = self.health  # Simplified: combat power equals health
        if not self.is_alive():
            self.state = UnitState.K_KILL
    
    def get_combat_power_percentage(self) -> float:
        return (self.combat_power / 100.0) * 100
    
    def move_to(self, new_position: Tuple[float, float]):
        self.position = new_position
        self.state = UnitState.MOVING
    
    def fire(self):
        self.state = UnitState.FIRE
        self.action = UnitState.FIRE
    
    def stop(self):
        self.state = UnitState.ALIVE
        self.action = UnitState.STOP
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'type': self.unit_type.name,
            'team': self.team,
            'position': self.position,
            'health': self.health,
            'state': self.state.value,
            'action': self.action.value
        }

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if not isinstance(other, Unit):
            return False
        return self.id == other.id 