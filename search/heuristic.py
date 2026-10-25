"""
Module: search/heuristic.py
Mo ta: Cai dat ham Heuristic h(n) su dung khoang cach BFS ket hop thuat toan Hungarian (linear_sum_assignment) va phat hien goc chet (deadlock).
"""

from collections import deque
from itertools import permutations
from typing import Dict, FrozenSet, List, Set, Tuple
import numpy as np

try:
    from scipy.optimize import linear_sum_assignment
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

from core.problem import SokobanProblem
from core.state import State


class SokobanHeuristic:
    INF = float("inf")
    LARGE_COST = 1_000_000

    def __init__(self, problem: SokobanProblem):
        self.problem = problem
        self.walls: FrozenSet[Tuple[int, int]] = problem.walls
        self.goals: List[Tuple[int, int]] = sorted(list(problem.goals))
        self.dist_matrix: Dict[Tuple[int, int], Dict[Tuple[int, int], int]] = {}

        # Tinh toan truoc ma tran khoang cach BFS tu tung dich
        self._precompute_bfs_distances()

        # Xac dinh cac vi tri deadlock goc chet
        self.deadlocks: Set[Tuple[int, int]] = self._find_corner_deadlocks()

    def _precompute_bfs_distances(self) -> None:
        # Tinh khoang cach ngan nhat tu moi o toi tung o dich bang BFS nguoc
        for goal in self.goals:
            self.dist_matrix[goal] = {}
            queue = deque([(goal, 0)])
            visited = {goal}

            while queue:
                curr, dist = queue.popleft()
                self.dist_matrix[goal][curr] = dist
                r, c = curr

                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    neighbor = (r + dr, c + dc)
                    if neighbor not in self.walls and neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((neighbor, dist + 1))

    def _find_corner_deadlocks(self) -> Set[Tuple[int, int]]:
        # Phat hien cac o goc chet khong the day hop ra ngoai
        deadlocks = set()
        all_coords = set(self.walls) | set(self.problem.goals)
        height = max((r for r, c in all_coords), default=0) + 2
        width = max((c for r, c in all_coords), default=0) + 2

        for r in range(height):
            for c in range(width):
                pos = (r, c)
                if pos in self.walls or pos in self.problem.goals:
                    continue

                up = (r - 1, c) in self.walls
                down = (r + 1, c) in self.walls
                left = (r, c - 1) in self.walls
                right = (r, c + 1) in self.walls

                # 4 goc vuong tao boi tuong
                if (up and left) or (up and right) or (down and left) or (down and right):
                    deadlocks.add(pos)

        return deadlocks

    def _solve_matching_fallback(self, cost_matrix: List[List[int]]) -> float:
        # Thuat toan ghep cap du phong neu moi truong chua cai dat SciPy
        n_boxes = len(cost_matrix)
        n_goals = len(cost_matrix[0]) if n_boxes > 0 else 0
        if n_boxes == 0 or n_goals == 0:
            return 0.0

        if n_boxes < n_goals:
            return self.INF

        min_total = self.LARGE_COST * n_goals
        for perm in permutations(range(n_boxes), n_goals):
            current_sum = sum(cost_matrix[perm[j]][j] for j in range(n_goals))
            if current_sum < min_total:
                min_total = current_sum

        return float(min_total)

    def calculate(self, state: State) -> float:
        # Kiem tra neu da dat trang thai dich
        if self.problem.is_goal(state):
            return 0.0

        boxes = list(state.boxes_pos)
        n_boxes = len(boxes)
        n_goals = len(self.goals)

        if n_goals == 0 or n_boxes < n_goals:
            return self.INF

        # Cat tia neu so luong hop khong bi deadlock nho hon so o dich
        deadlock_count = sum(1 for box in boxes if box in self.deadlocks)
        if n_boxes - deadlock_count < n_goals:
            return self.INF

        # Xay dung ma tran chi phi va giai Hungarian matching
        if HAS_SCIPY:
            cost_matrix = np.full((n_boxes, n_goals), self.LARGE_COST, dtype=float)
            for i, box in enumerate(boxes):
                for j, goal in enumerate(self.goals):
                    d = self.dist_matrix[goal].get(box, None)
                    if d is not None:
                        cost_matrix[i, j] = d

            row_ind, col_ind = linear_sum_assignment(cost_matrix)
            total_cost = float(cost_matrix[row_ind, col_ind].sum())

            if total_cost >= self.LARGE_COST:
                return self.INF
            return total_cost
        else:
            raw_matrix = []
            for box in boxes:
                row = []
                for goal in self.goals:
                    d = self.dist_matrix[goal].get(box, self.LARGE_COST)
                    row.append(d)
                raw_matrix.append(row)

            total_cost = self._solve_matching_fallback(raw_matrix)
            if total_cost >= self.LARGE_COST:
                return self.INF
            return total_cost
