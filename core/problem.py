"""
Module: core/problem.py
Phụ trách: Duy (Leader - Core Architecture)
Mô tả: Đóng gói bài toán Sokoban, logic di chuyển và kiểm tra đích.
"""

from typing import Tuple, List, FrozenSet
from core.state import State, ACTIONS


class SokobanProblem:
    """
    Định nghĩa bài toán không gian trạng thái cho Sokoban.
    """
    def __init__(self, initial_state: State, walls: FrozenSet[Tuple[int, int]], goals: FrozenSet[Tuple[int, int]]):
        self.initial_state = initial_state
        self.walls = walls
        self.goals = goals

    def is_goal(self, state: State) -> bool:
        """
        Kiểm tra trạng thái đích: Tất cả các hộp phải nằm tại các vị trí đích.
        """
        return state.boxes_pos == self.goals

    def get_actions(self, state: State) -> List[str]:
        """
        Trả về danh sách các hành động hợp lệ từ trạng thái hiện tại.
        Hành động hợp lệ khi:
        1. Đi vào ô trống (không phải tường, không có hộp).
        2. Đẩy hộp nếu ô sau lưng hộp không phải tường và không có hộp khác.
        """
        valid_actions = []
        ar, ac = state.player_pos

        for action_name, (dr, dc) in ACTIONS.items():
            new_ar, new_ac = ar + dr, ac + dc
            target_pos = (new_ar, new_ac)

            # Trường hợp 1: Ô đi tới là tường
            if target_pos in self.walls:
                continue

            # Trường hợp 2: Ô đi tới có hộp (hành động đẩy hộp - PUSH)
            if target_pos in state.boxes_pos:
                behind_box_pos = (new_ar + dr, new_ac + dc)
                # Kiểm tra sau lưng hộp có phải là tường hoặc có hộp khác chặn không
                if behind_box_pos in self.walls or behind_box_pos in state.boxes_pos:
                    continue
                valid_actions.append(action_name)
            else:
                # Trường hợp 3: Đi vào ô trống bình thường (MOVE)
                valid_actions.append(action_name)

        return valid_actions

    def get_successor(self, state: State, action: str) -> Tuple[State, int]:
        """
        Thực hiện hành động và trả về: (trạng thái mới, chi phí bước đi).
        Mỗi bước đi có chi phí mặc định là 1.
        """
        if action not in ACTIONS:
            raise ValueError(f"Hành động không hợp lệ: {action}")

        dr, dc = ACTIONS[action]
        ar, ac = state.player_pos
        new_agent_pos = (ar + dr, ac + dc)

        # Nếu ô di chuyển tới có hộp thì cập nhật vị trí mới của hộp
        if new_agent_pos in state.boxes_pos:
            new_box_pos = (new_agent_pos[0] + dr, new_agent_pos[1] + dc)
            new_boxes = set(state.boxes_pos)
            new_boxes.remove(new_agent_pos)
            new_boxes.add(new_box_pos)
            next_state = State(player_pos=new_agent_pos, boxes_pos=frozenset(new_boxes))
        else:
            # Di chuyển bình thường
            next_state = State(player_pos=new_agent_pos, boxes_pos=state.boxes_pos)

        step_cost = 1
        return next_state, step_cost