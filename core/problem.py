"""
Module: core/problem.py
Phụ trách: Duy (Leader - Core Architecture)
Mô tả: Đóng gói bài toán Sokoban, logic di chuyển và kiểm tra đích theo R1.
"""

from typing import Tuple, List, FrozenSet
from core.state import State, ACTIONS


class SokobanProblem:
    """
    Mô hình hóa không gian trạng thái Sokoban theo R1.
    """
    def __init__(self, initial_state: State, walls: FrozenSet[Tuple[int, int]], goals: FrozenSet[Tuple[int, int]]):
        self.initial_state = initial_state
        self.walls = walls
        self.goals = goals

    def is_goal(self, state: State) -> bool:
        """
        Goal Test: Tất cả các hộp phải nằm tại các vị trí đích.
        """
        return state.boxes_pos == self.goals

    def get_actions(self, state: State) -> List[str]:
        """
        Trả về danh sách các hành động hợp lệ từ trạng thái hiện tại.
        Hành động hợp lệ:
        1. Di chuyển vào ô trống (không phải tường, không có hộp).
        2. Đẩy hộp nếu ô kế tiếp sau lưng hộp không phải tường và không có hộp khác.
        """
        valid_actions = []
        ar, ac = state.player_pos

        for action_name, (dr, dc) in ACTIONS.items():
            new_ar, new_ac = ar + dr, ac + dc
            target_pos = (new_ar, new_ac)

            # Trường hợp 1: Ô tới là tường -> Bị chặn
            if target_pos in self.walls:
                continue

            # Trường hợp 2: Ô tới có hộp -> Kiểm tra ô sau lưng hộp (Push)
            if target_pos in state.boxes_pos:
                behind_box_pos = (new_ar + dr, new_ac + dc)
                if behind_box_pos in self.walls or behind_box_pos in state.boxes_pos:
                    continue
                valid_actions.append(action_name)
            else:
                # Trường hợp 3: Ô trống -> Di chuyển bình thường (Move)
                valid_actions.append(action_name)

        return valid_actions

    def get_successor(self, state: State, action: str) -> Tuple[State, int]:
        """
        Transition Model: Thực hiện hành động và trả về (trạng thái kế tiếp, chi phí bước đi).
        Mỗi bước đi tốn chi phí c = 1.
        """
        if action not in ACTIONS:
            raise ValueError(f"Hành động không hợp lệ: {action}")

        dr, dc = ACTIONS[action]
        ar, ac = state.player_pos
        new_agent_pos = (ar + dr, ac + dc)

        # Nếu đẩy hộp
        if new_agent_pos in state.boxes_pos:
            new_box_pos = (new_agent_pos[0] + dr, new_agent_pos[1] + dc)
            new_boxes = set(state.boxes_pos)
            new_boxes.remove(new_agent_pos)
            new_boxes.add(new_box_pos)
            next_state = State(player_pos=new_agent_pos, boxes_pos=frozenset(new_boxes))
        else:
            # Di chuyển không đẩy hộp
            next_state = State(player_pos=new_agent_pos, boxes_pos=state.boxes_pos)

        step_cost = 1
        return next_state, step_cost