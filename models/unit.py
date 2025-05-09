from enum import Enum
from dataclasses import dataclass

class UnitType(Enum):
    DRONE = "드론"
    TANK = "전차"
    ANTI_TANK = "대전차"
    INFANTRY = "개인화기"
    COMMAND_POST = "전방지휘소"
    ARTILLERY = "곡사화기"

@dataclass
class Unit:
    unit_type: UnitType
    team: str  # "RED" or "BLUE"
    position: tuple[float, float]
    health: float = 100.0
    combat_power: float = 100.0
    
    def is_alive(self) -> bool:
        return self.health > 0
    
    def take_damage(self, damage: float):
        self.health = max(0, self.health - damage)
        self.combat_power = self.health  # Simplified: combat power equals health
    
    def get_combat_power_percentage(self) -> float:
        return (self.combat_power / 100.0) * 100 