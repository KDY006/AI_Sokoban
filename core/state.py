"""
Module: core/state.py
Mo ta: Dinh nghia lop State bieu dien trang thai Sokoban va ham parse_map de doc ban do tu file.
"""

from typing import Tuple, FrozenSet, Set

# 4 huong di chuyen co ban (North, South, West, East)
ACTIONS = {
    'North': (-1, 0),
    'South': (1, 0),
    'West': (0, -1),
    'East': (0, 1)
}


class State:
    """
    Bieu dien trang thai bat bien cua tro choi Sokoban.
    Bao gom toa do Agent va tap hop toa do cac Hop.
    """
    def __init__(self, player_pos: Tuple[int, int], boxes_pos: FrozenSet[Tuple[int, int]]):
        self.player_pos: Tuple[int, int] = player_pos
        self.boxes_pos: FrozenSet[Tuple[int, int]] = frozenset(boxes_pos)
        self._hash: int = hash((self.player_pos, self.boxes_pos))

    def __eq__(self, other) -> bool:
        if not isinstance(other, State):
            return False
        return self.player_pos == other.player_pos and self.boxes_pos == other.boxes_pos

    def __hash__(self) -> int:
        return self._hash

    def __repr__(self) -> str:
        return f"State(Agent={self.player_pos}, Boxes={set(self.boxes_pos)})"


def parse_map(file_path: str) -> Tuple[State, FrozenSet[Tuple[int, int]], FrozenSet[Tuple[int, int]], int, int]:
    """
    Doc file ban do Sokoban theo quy uoc ky tu de bai:
        % : Tuong (wall)
        A : Vi tri ban dau cua Agent
        B : Hop chua vao dich (box)
        D : Diem dich (goal)
        C : Hop da nam tren diem dich (box on goal)
        ' ': San trong
    """
    walls: Set[Tuple[int, int]] = set()
    goals: Set[Tuple[int, int]] = set()
    boxes: Set[Tuple[int, int]] = set()
    agent_pos: Tuple[int, int] | None = None

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = [line.rstrip('\r\n') for line in f.readlines()]

    max_row = len(lines)
    max_col = max(len(line) for line in lines) if lines else 0

    # Quet tung ky tu tren ban do
    for r, line in enumerate(lines):
        for c, char in enumerate(line):
            coord = (r, c)
            if char == '%':
                walls.add(coord)
            elif char == 'A':
                agent_pos = coord
            elif char == 'B':
                boxes.add(coord)
            elif char == 'D':
                goals.add(coord)
            elif char == 'C':
                boxes.add(coord)
                goals.add(coord)

    # Kiem tra vi tri Agent
    if agent_pos is None:
        raise ValueError("Loi: Khong tim thay vi tri Agent ('A') tren ban do!")

    initial_state = State(player_pos=agent_pos, boxes_pos=frozenset(boxes))
    return initial_state, frozenset(walls), frozenset(goals), max_row, max_col
