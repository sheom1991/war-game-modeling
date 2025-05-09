import heapq
from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class SimulationEvent:
    time: float
    actor: Any
    action: str
    target: Optional[Any] = None
    details: Optional[dict] = None
    
    def __lt__(self, other):
        return self.time < other.time

class EventQueue:
    def __init__(self):
        self.events = []
        
    def schedule(self, event: SimulationEvent):
        """Schedule a new event"""
        heapq.heappush(self.events, event)
        
    def get_next_event(self) -> Optional[SimulationEvent]:
        """Get the next event to be processed"""
        if self.events:
            return heapq.heappop(self.events)
        return None
    
    def peek_next_time(self) -> Optional[float]:
        """Get the time of the next event without removing it"""
        if self.events:
            return self.events[0].time
        return None
    
    def clear(self):
        """Clear all events"""
        self.events.clear()
        
    def __len__(self) -> int:
        return len(self.events) 