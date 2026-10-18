"""
Module: search/heuristic.py
Phụ trách: Quý
Mô tả: Cài đặt hàm Heuristic h(n) đặc thù cho bài toán Sokoban (R2).
       Hàm Heuristic sử dụng BFS Shortest Path kết hợp thuật toán Hungarian 
       (Min-Cost Bipartite Matching) để ghép cặp tối ưu giữa Hộp và Đích, 
       hoàn toàn không dùng khoảng cách Manhattan hay Euclidean theo yêu cầu đề bài.
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
    """
    Hàm Heuristic h(n) đặc thù cho Sokoban dựa trên Min-Cost Bipartite Matching:
    - Sử dụng BFS Shortest Path trên mê cung (né vật cản / tường '%') để tính khoảng cách thực tế.
    - Dùng thuật toán Hungarian (scipy.optimize.linear_sum_assignment) để tìm ghép cặp tối ưu Hộp - Đích.
    - Phát hiện góc chết tĩnh (Corner Deadlocks) để cắt tỉa các trạng thái không thể giải.
    """

    INF = float("inf")
    LARGE_COST = 1_000_000

    def __init__(self, problem: SokobanProblem):
        self.problem = problem
        self.walls: FrozenSet[Tuple[int, int]] = problem.walls
        self.goals: List[Tuple[int, int]] = sorted(list(problem.goals))
        self.dist_matrix: Dict[Tuple[int, int], Dict[Tuple[int, int], int]] = {}

        # 1. Tính toán trước ma trận khoảng cách BFS từ từng đích
        self._precompute_bfs_distances()

        # 2. Xác định tập các vị trí Deadlock góc chết
        self.deadlocks: Set[Tuple[int, int]] = self._find_corner_deadlocks()

    def _precompute_bfs_distances(self) -> None:
        """
        Duyệt BFS ngược từ từng đích g để tìm khoảng cách ngắn nhất né tường
        từ mọi ô hợp lệ trên bản đồ tới g.
        """
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
        """
        Xác định các ô góc chết (Corner Deadlock).
        Ô góc chết là ô không phải tường, không phải đích, và có 2 bờ tường
        vuông góc kề cạnh. Hộp rơi vào đây sẽ không bao giờ di chuyển được nữa.
        """
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

                # 4 hướng tạo góc vuông tường
                if (up and left) or (up and right) or (down and left) or (down and right):
                    deadlocks.add(pos)

        return deadlocks

    def _solve_matching_fallback(self, cost_matrix: List[List[int]]) -> float:
        """
        Giải thuật ghép cặp tối ưu dự phòng khi môi trường chưa cài đặt SciPy.
        """
        n = len(cost_matrix)
        m = len(cost_matrix[0]) if n > 0 else 0
        if n == 0 or m == 0:
            return 0.0

        min_total = self.LARGE_COST * n
        for perm in permutations(range(m), n):
            current_sum = sum(cost_matrix[i][perm[i]] for i in range(n))
            if current_sum < min_total:
                min_total = current_sum

        return float(min_total)

    def calculate(self, state: State) -> float:
        """
        Tính giá trị Heuristic h(n) cho trạng thái state.
        Trả về:
            - 0.0 nếu đã đạt trạng thái đích.
            - float('inf') nếu rơi vào deadlock hoặc không thể đưa hộp về đích.
            - Chi phí ghép cặp Hungarian nhỏ nhất giữa các hộp và các đích.
        """
        if state.boxes_pos == self.problem.goals:
            return 0.0

        # Kiểm tra Deadlock góc chết
        for box in state.boxes_pos:
            if box in self.deadlocks:
                return self.INF

        boxes = list(state.boxes_pos)
        n_boxes = len(boxes)
        n_goals = len(self.goals)

        if n_boxes == 0:
            return 0.0

        # Xây dựng ma trận chi phí C[i, j] = dist_BFS(box_i, goal_j)
        if HAS_SCIPY:
            cost_matrix = np.full((n_boxes, n_goals), self.LARGE_COST, dtype=float)
            for i, box in enumerate(boxes):
                for j, goal in enumerate(self.goals):
                    d = self.dist_matrix[goal].get(box, None)
                    if d is not None:
                        cost_matrix[i, j] = d

            # Giải ghép cặp cực tiểu bằng Hungarian Algorithm
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
