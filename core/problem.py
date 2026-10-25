"""
Module: core/problem.py
Mo ta: Mo hinh hoa bai toan Sokoban gom khong gian trang thai, tap hanh dong hop le, ham chuyen trang thai va kiem tra trang thai dich.
"""

from typing import Tuple, List, FrozenSet
from core.state import State, ACTIONS


class SokobanProblem:
    def __init__(self, initial_state: State, walls: FrozenSet[Tuple[int, int]], goals: FrozenSet[Tuple[int, int]]):
        self.initial_state = initial_state
        self.walls = walls
        self.goals = goals

    def is_goal(self, state: State) -> bool:
        # Kiem tra tat ca cac o dich da duoc lap day boi hop
        if not self.goals:
            return False
        return self.goals.issubset(state.boxes_pos)

    def get_actions(self, state: State) -> List[str]:
        # Tra ve danh sach hanh dong hop le tu vi tri hien tai
        valid_actions = []
        ar, ac = state.player_pos

        for action_name, (dr, dc) in ACTIONS.items():
            new_ar, new_ac = ar + dr, ac + dc
            target_pos = (new_ar, new_ac)

            # Khong di vao tuong
            if target_pos in self.walls:
                continue

            # Neu gap hop, kiem tra o sau lung hop de day
            if target_pos in state.boxes_pos:
                behind_box_pos = (new_ar + dr, new_ac + dc)
                if behind_box_pos in self.walls or behind_box_pos in state.boxes_pos:
                    continue
                valid_actions.append(action_name)
            else:
                # O trong hop le de di chuyen
                valid_actions.append(action_name)

        return valid_actions

    def get_successor(self, state: State, action: str) -> Tuple[State, int]:
        # Thuc hien hanh dong va tra ve trang thai ke tiep kem chi phi buoc di c = 1
        if action not in ACTIONS:
            raise ValueError(f"Hanh dong khong hop le: {action}")

        dr, dc = ACTIONS[action]
        ar, ac = state.player_pos
        new_agent_pos = (ar + dr, ac + dc)

        # Cap nhat toa do hop neu hanh dong la day hop
        if new_agent_pos in state.boxes_pos:
            new_box_pos = (new_agent_pos[0] + dr, new_agent_pos[1] + dc)
            new_boxes = set(state.boxes_pos)
            new_boxes.remove(new_agent_pos)
            new_boxes.add(new_box_pos)
            next_state = State(player_pos=new_agent_pos, boxes_pos=frozenset(new_boxes))
        else:
            next_state = State(player_pos=new_agent_pos, boxes_pos=state.boxes_pos)

        step_cost = 1
        return next_state, step_cost
