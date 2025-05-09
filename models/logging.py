import json
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

@dataclass
class Event:
    timestamp: float
    event_type: str
    actor_id: str
    action: str
    target_id: str = None
    details: Dict = None

@dataclass
class StateSnapshot:
    timestamp: float
    units: List[Dict]
    terrain_state: Dict
    combat_state: Dict

class SimulationLogger:
    def __init__(self, log_file: str = "simulation_log.json"):
        self.log_file = log_file
        self.events: List[Event] = []
        self.state_snapshots: List[StateSnapshot] = []
        
    def log_event(self, event: Event):
        """Log a single event"""
        self.events.append(event)
        
    def log_state(self, snapshot: StateSnapshot):
        """Log a state snapshot"""
        self.state_snapshots.append(snapshot)
        
    def save_logs(self):
        """Save all logs to file"""
        log_data = {
            "events": [asdict(event) for event in self.events],
            "state_snapshots": [asdict(snapshot) for snapshot in self.state_snapshots],
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_events": len(self.events),
                "total_snapshots": len(self.state_snapshots)
            }
        }
        
        with open(self.log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
            
    def get_events_by_type(self, event_type: str) -> List[Event]:
        """Get all events of a specific type"""
        return [event for event in self.events if event.event_type == event_type]
    
    def get_state_at_time(self, timestamp: float) -> StateSnapshot:
        """Get the state snapshot closest to the given timestamp"""
        return min(self.state_snapshots, key=lambda x: abs(x.timestamp - timestamp)) 