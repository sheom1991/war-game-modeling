import numpy as np
import os
import yaml
from models.terrain import TerrainSystem
from models.combat import CombatSystem, CombatUnit
from models.probabilities import ProbabilitySystem
from models.events import EventQueue, SimulationEvent
from models.logging import SimulationLogger, Event, StateSnapshot
from models.visualization import SimulationVisualizer
from models.unit import Unit, UnitType
import time
from matplotlib.image import imread
import json

def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def create_test_units(cfg):
    units = []
    initial_positions = cfg.get('initial_positions', {})

    # 팀별 유닛 사양: (cfg 키, 기본 위치)
    team_specs = {
        'RED': {
            'DRONE': ('num_drone_red',    (100, 100)),
            'TANK': ('num_tank_red',      (120, 120)),
            'ANTI_TANK': ('num_at_red',    (140, 140)),
            'INFANTRY': ('num_infantry_red', (160, 160)),
            'COMMAND_POST': ('num_cp_red', (180, 180)),
            'ARTILLERY': ('num_artillery_red', (200, 200)),
        },
        'BLUE': {
            'DRONE': ('num_drone_blue',    (300, 300)),
            'TANK': ('num_tank_blue',      (320, 320)),
            'ANTI_TANK': ('num_at_blue',    (340, 340)),
            'INFANTRY': ('num_infantry_blue', (360, 360)),
            'COMMAND_POST': ('num_cp_blue', (380, 380)),
            'ARTILLERY': ('num_artillery_blue', (400, 400)),
        },
    }

    # 카운터 초기화
    unit_counters = {
        team: {unit_type: 1 for unit_type in specs}
        for team, specs in team_specs.items()
    }

    def get_positions(team, unit_type, count, default_pos):
        pos_list = initial_positions.get(team, {}).get(unit_type)
        if pos_list and len(pos_list) >= count:
            return [tuple(p) for p in pos_list[:count]]
        return [default_pos] * count

    for team, specs in team_specs.items():
        for unit_type, (cfg_key, default_pos) in specs.items():
            # 드론 옵션 체크
            if unit_type == 'DRONE' and not cfg.get('with_drone', True):
                continue
            count = cfg.get(cfg_key, 0)
            positions = get_positions(team, unit_type, count, default_pos)
            for _ in range(count):
                pos = positions[_]
                unit = Unit(getattr(UnitType, unit_type), team, pos)
                idx = unit_counters[team][unit_type]
                unit.id = f"{team}_{unit_type}_{idx}"
                units.append(CombatUnit(unit))
                unit_counters[team][unit_type] += 1

    return units

def run_simulation(cfg):
    os.makedirs(cfg['output_dir'], exist_ok=True)
    terrain_system = TerrainSystem()
    probability_system = ProbabilitySystem()
    combat_system = CombatSystem(probability_system)
    if 'distance_rescale' in cfg:
        combat_system.set_distance_rescale(cfg['distance_rescale'])
    event_queue = EventQueue()
    logger = SimulationLogger(log_file=os.path.join(cfg['output_dir'], "simulation_log.json"))
    visualizer = SimulationVisualizer(config=cfg)
    units = create_test_units(cfg)
    current_time = 0.0
    time_step = 1.0
    max_time = cfg['max_time']
    print(f"Starting simulation... (with_drone={cfg.get('with_drone', True)}, max_time={max_time}, output_dir={cfg['output_dir']})")
    # Get background image size for bounds
    bg_img = imread(os.path.join("results", "background.png"))
    img_height, img_width = bg_img.shape[0], bg_img.shape[1]
    while current_time < max_time:
        state_snapshot = StateSnapshot(
            timestamp=current_time,
            units=[{
                'id': f"{unit.unit.team}_{unit.unit.unit_type.name}",
                'type': unit.unit.unit_type.name,
                'team': unit.unit.team,
                'position': unit.unit.position,
                'status': unit.state.value,
                'action': unit.action.value,
                'health': unit.unit.health,
                'target_list': [f"{t.team}_{t.unit_type.name}" for t in getattr(unit, 'target_list', [])],
                'eligible_target_list': [f"{t.team}_{t.unit_type.name}" for t in getattr(unit, 'eligible_target_list', [])],
            } for unit in units],
            terrain_state={'timestamp': current_time},
            combat_state={'timestamp': current_time}
        )
        logger.log_state(state_snapshot)
        # 공격 결과 임시 저장
        attack_results = []
        for unit in units:
            if unit.unit.health <= 0:
                continue
            enemies = [u for u in units if u.unit.team != unit.unit.team and u.unit.health > 0]
            if not enemies:
                continue
            # 가장 가까운 적 1명만 공격
            closest_enemy = min(enemies, key=lambda e: combat_system._calculate_distance(unit.unit.position, e.unit.position))
            if combat_system.is_in_range(unit, closest_enemy) and terrain_system.check_line_of_sight(unit.unit.position, closest_enemy.unit.position):
                hit_prob = combat_system.calculate_hit_probability(unit, closest_enemy)
                unit.action = unit.action.FIRE if hasattr(unit.action, 'FIRE') else 'FIRE'  # FIRE 상태로 표시
                if np.random.random() < hit_prob:
                    damage = combat_system.process_damage(unit, closest_enemy)
                    attack_results.append((closest_enemy, damage))
                    combat_event = Event(
                        timestamp=current_time,
                        event_type="COMBAT",
                        actor_id=unit.unit.id,
                        action="FIRE",
                        target_id=closest_enemy.unit.id,
                        details={
                            'hit': True,
                            'damage': damage,
                            'hit_probability': hit_prob
                        }
                    )
                    logger.log_event(combat_event)
                    print(f"Time {current_time:.1f}: {unit.unit.id} HIT {closest_enemy.unit.id} for {damage} damage (p={hit_prob:.2f})")
                else:
                    combat_event = Event(
                        timestamp=current_time,
                        event_type="COMBAT",
                        actor_id=unit.unit.id,
                        action="FIRE",
                        target_id=closest_enemy.unit.id,
                        details={
                            'hit': False,
                            'damage': 0,
                            'hit_probability': hit_prob
                        }
                    )
                    logger.log_event(combat_event)
                    print(f"Time {current_time:.1f}: {unit.unit.id} MISS {closest_enemy.unit.id} (p={hit_prob:.2f})")
        # 공격 결과 health/state 일괄 반영 (다음 턴에서 반영)
        for target, damage in attack_results:
            target.unit.health -= damage
        for unit in units:
            if unit.unit.health <= 0:
                unit.state = unit.state.K_KILL
            elif unit.action == (unit.action.FIRE if hasattr(unit.action, 'FIRE') else 'FIRE'):
                unit.action = unit.action.STOP if hasattr(unit.action, 'STOP') else 'STOP'
        # 이동
        for unit in units:
            if unit.unit.health <= 0:
                continue
            # 지휘소는 이동하지 않음
            if unit.unit.unit_type == UnitType.COMMAND_POST:
                continue
            new_x = unit.unit.position[0] + np.random.randint(-10, 11)
            new_y = unit.unit.position[1] + np.random.randint(-10, 11)
            new_x = max(0, min(new_x, img_width - 1))
            new_y = max(0, min(new_y, img_height - 1))
            unit.unit.position = (new_x, new_y)
            movement_event = Event(
                timestamp=current_time,
                event_type="MOVEMENT",
                actor_id=f"{unit.unit.team}_{unit.unit.unit_type.name}",
                action="MOVE",
                details={
                    'old_position': unit.unit.position,
                    'new_position': (new_x, new_y)
                }
            )
            logger.log_event(movement_event)
        current_time += time_step
    logger.save_logs()
    print("Simulation completed. Generating visualizations...")
    final_units = [{
        'id': f"{unit.unit.team}_{unit.unit.unit_type.name}",
        'type': unit.unit.unit_type.name,
        'team': unit.unit.team,
        'position': unit.unit.position,
        'status': unit.state.value,
        'health': unit.unit.health
    } for unit in units]
    # DEM only visualization
    visualizer.create_map_visualization(final_units, current_time, output_file=os.path.join(cfg['output_dir'], "dem_only.png"))
    # Save background image in the results folder
    bg_path = os.path.join("results", "background.png")
    if not os.path.exists(bg_path):
        visualizer.save_background_image(bg_path)
    # n_frames = int(cfg['fps'] * max(5, max_time / cfg['fps']))
    total_frames = int(max_time * cfg['fps'])   # max_time이 초 단위일 때
    min_frames   = cfg['fps'] * 15              # 최소 15초분 프레임
    n_frames     = max(total_frames, min_frames)
    # Load events for kill log
    with open(os.path.join(cfg['output_dir'], "simulation_log.json"), "r") as f:
        log_data = json.load(f)
    events = log_data.get("events", [])
    visualizer.create_animation(logger.state_snapshots, os.path.join(cfg['output_dir'], "simulation.mp4"), fps=cfg['fps'], n_frames=n_frames, events=events)
    visualizer.plot_metrics(os.path.join(cfg['output_dir'], "simulation_log.json"))
    print("Visualizations generated:")
    print(f"- {cfg['output_dir']}/dem_only.png: DEM only visualization")
    print(f"- {cfg['output_dir']}/simulation.mp4: Animation of the simulation")
    print(f"- {cfg['output_dir']}/simulation_metrics.png: Metrics plots")
    print(f"- {cfg['output_dir']}/simulation_log.json: Detailed simulation logs")

if __name__ == "__main__":
    config = load_config('config.yaml')
    run_simulation(config) 