import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

distance = ctrl.Antecedent(np.arange(0, 800, 1), "distance")
speed = ctrl.Antecedent(np.arange(5, 21, 0.1), "speed")
obs_height = ctrl.Antecedent(np.arange(0, 100, 1), "obs_height")
ptero_offset = ctrl.Antecedent(np.arange(0, 150, 1), "ptero_offset")

strength = ctrl.Consequent(np.arange(0, 1.01, 0.01), "strength")
duck_duration = ctrl.Consequent(np.arange(0, 61, 1), "duck_duration")

obs_height["short"] = fuzz.trimf(obs_height.universe, [0, 20, 45])
obs_height["tall"] = fuzz.trapmf(obs_height.universe, [40, 65, 100, 100])

ptero_offset["low"] = fuzz.trimf(ptero_offset.universe, [0, 30, 45])
ptero_offset["medium"] = fuzz.trimf(ptero_offset.universe, [45, 60, 90])
ptero_offset["high"] = fuzz.trapmf(ptero_offset.universe, [90, 120, 150, 150])

distance["close"] = fuzz.trapmf(distance.universe, [0, 0, 80, 150])
distance["medium"] = fuzz.trimf(distance.universe, [120, 220, 350])
distance["far"] = fuzz.trapmf(distance.universe, [150, 220, 800, 800])

speed["slow"] = fuzz.trapmf(speed.universe, [5, 5, 8, 12])
speed["moderate"] = fuzz.trimf(speed.universe, [9, 13, 17])
speed["fast"] = fuzz.trapmf(speed.universe, [14, 18, 20, 21])

strength["low_power"] = fuzz.trimf(strength.universe, [0, 0.7, 0.75])
strength["high_power"] = fuzz.trimf(strength.universe, [0.8, 1.0, 1.0])

duck_duration["short_hold"] = fuzz.trimf(duck_duration.universe, [0, 8, 18])
duck_duration["med_hold"] = fuzz.trimf(duck_duration.universe, [12, 25, 38])
duck_duration["long_hold"] = fuzz.trapmf(duck_duration.universe, [30, 45, 60, 60])

rules = [
    ctrl.Rule(
        obs_height["short"] & distance["close"] & ptero_offset["low"],
        [strength["low_power"], duck_duration["short_hold"]],
    ),
    ctrl.Rule(
        obs_height["tall"] & distance["medium"] & ptero_offset["low"],
        [strength["high_power"], duck_duration["short_hold"]],
    ),
    ctrl.Rule(
        ptero_offset["medium"] & distance["close"] & speed["slow"],
        [strength["low_power"], duck_duration["long_hold"]],
    ),
    ctrl.Rule(
        ptero_offset["medium"] & distance["close"] & speed["moderate"],
        [strength["low_power"], duck_duration["med_hold"]],
    ),
    ctrl.Rule(
        ptero_offset["medium"] & distance["close"] & speed["fast"],
        [strength["low_power"], duck_duration["short_hold"]],
    ),
    ctrl.Rule(distance["far"], [strength["low_power"], duck_duration["short_hold"]]),
]

simulation = ctrl.ControlSystemSimulation(ctrl.ControlSystem(rules))


def process(player_x, closest_enemy, current_speed) -> tuple[float, float]:
    crisp_dist = closest_enemy.x - player_x

    if closest_enemy.color == (128, 128, 128):  # ptero
        offset_value = (
            (GROUND_LEVEL + PLAYER_SIZE) - closest_enemy.height - closest_enemy.y
        )
    else:
        offset_value = 0

    simulation.input["distance"] = max(0, crisp_dist)
    simulation.input["speed"] = current_speed
    simulation.input["obs_height"] = closest_enemy.height
    simulation.input["ptero_offset"] = offset_value

    simulation.compute()
    # print(simulation.output["strength"], simulation.output["duck_duration"])

    try:
        return simulation.output["strength"], simulation.output["duck_duration"]
    except Exception:
        print("Exception")
        return 0.0, 0.0
