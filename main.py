from models.game_state import GameState
from models.unit import UnitType
from models.combat import UnitState

def main():
    # Initialize game state
    game_state = GameState()
    
    # Simulation loop
    turn = 1
    while True:
        print(f"\n=== Turn {turn} ===")
        print(f"Current Phase: {game_state.command_system.red_command.phase.name}")
        
        # Update target lists
        game_state.update_target_lists()
        
        # Process combat
        game_state.process_combat()
        
        # Display team status
        print("\nRed Team Status:")
        for unit_type in UnitType:
            count = sum(1 for unit in game_state.red_team 
                       if unit.unit.unit_type == unit_type and unit.unit.is_alive())
            print(f"{unit_type.value}: {count} units")
        
        print("\nBlue Team Status:")
        for unit_type in UnitType:
            count = sum(1 for unit in game_state.blue_team 
                       if unit.unit.unit_type == unit_type and unit.unit.is_alive())
            print(f"{unit_type.value}: {count} units")
        
        # Check for phase transition
        game_state.check_phase_transition()
        
        # Check for game end conditions
        red_power = game_state.get_team_combat_power("RED")
        blue_power = game_state.get_team_combat_power("BLUE")
        
        if red_power <= 0:
            print("\nBlue Team Wins!")
            break
        if blue_power <= 0:
            print("\nRed Team Wins!")
            break
        
        turn += 1
        
        # For demonstration, we'll end after 10 turns
        if turn > 10:
            print("\nSimulation ended after 10 turns")
            break

if __name__ == "__main__":
    main() 