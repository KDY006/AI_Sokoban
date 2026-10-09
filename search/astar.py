"""
Module: search/astar.py
Phụ trách: Quý
Mô tả: Cài đặt thuật toán A* và hàm Heuristic h(n) đặc thù cho Sokoban (R2).
       Hàm Heuristic sử dụng BFS Shortest Path kết hợp thuật toán Hungarian 
       (Min-Cost Bipartite Matching) để ghép cặp tối ưu giữa Hộp và Đích, 
       hoàn toàn không dùng khoảng cách Manhattan hay Euclidean.
"""

import heapq
import time
from collections import deque
from itertools import permutations
from typing import Dict, FrozenSet, List, Optional, Set, Tuple
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

    INF = float('inf')
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


class AStarNode:
    """
    Nút trên cây tìm kiếm A* (Search Node).
    Lưu trữ trạng thái, đường đi và các giá trị hàm đánh giá: f = g + h.
    """
    def __init__(
        self,
        state: State,
        parent: Optional['AStarNode'] = None,
        action: Optional[str] = None,
        g_cost: int = 0,
        h_cost: float = 0.0
    ):
        self.state: State = state
        self.parent: Optional['AStarNode'] = parent
        self.action: Optional[str] = action
        self.g_cost: int = g_cost
        self.h_cost: float = h_cost
        self.f_cost: float = g_cost + h_cost

    def __lt__(self, other: 'AStarNode') -> bool:
        if self.f_cost == other.f_cost:
            return self.h_cost < other.h_cost
        return self.f_cost < other.f_cost


def astar_search(problem: SokobanProblem) -> Tuple[Optional[List[str]], int, Dict]:
    """
    Thực thi giải thuật A* Search với Heuristic Hungarian BFS.
    Đầu ra chuẩn:
        - actions: Danh sách hành động ['North', 'East', ...] hoặc None
        - total_cost: Tổng chi phí đường đi tối ưu
        - stats: Thống kê thực nghiệm (số node mở rộng, bộ nhớ đỉnh frontier, thời gian chạy ms)
    """
    start_time = time.perf_counter()
    heuristic_engine = SokobanHeuristic(problem)

    # Khởi tạo trạng thái ban đầu
    h0 = heuristic_engine.calculate(problem.initial_state)
    if h0 == float('inf'):
        end_time = time.perf_counter()
        elapsed_ms = (end_time - start_time) * 1000
        stats = {
            "expanded_nodes": 0,
            "nodes_expanded": 0,
            "max_frontier_size": 0,
            "time_ms": elapsed_ms,
            "execution_time_ms": elapsed_ms,
            "total_cost": 0
        }
        return None, 0, stats

    start_node = AStarNode(
        state=problem.initial_state,
        parent=None,
        action=None,
        g_cost=0,
        h_cost=h0
    )

    # Priority queue lưu tuple: (f_cost, h_cost, counter, node)
    counter = 0
    frontier: List[Tuple[float, float, int, AStarNode]] = []
    heapq.heappush(frontier, (start_node.f_cost, start_node.h_cost, counter, start_node))

    # Bảng lưu g_cost nhỏ nhất đã tìm thấy tới từng State
    cost_so_far: Dict[State, int] = {problem.initial_state: 0}

    expanded_nodes = 0
    max_frontier_size = 1
    last_print_time = start_time

    while frontier:
        max_frontier_size = max(max_frontier_size, len(frontier))
        current_f, current_h, _, current_node = heapq.heappop(frontier)
        current_state = current_node.state

        # Nếu đã tìm thấy đường đi tới current_state với g_cost tốt hơn trước đó -> Bỏ qua
        if current_node.g_cost > cost_so_far.get(current_state, float('inf')):
            continue

        # In log định kỳ mỗi 3 giây nếu tìm kiếm lâu
        now = time.perf_counter()
        if now - last_print_time > 3.0:
            print(f"[A* dang duyet...] So node mo rong: {expanded_nodes:,} | Frontier: {len(frontier):,} | f: {current_f:.1f} (g={current_node.g_cost}, h={current_h:.1f})")
            last_print_time = now

        # Goal Test: Kiểm tra đích khi LẤY NODE RA khỏi Frontier
        if problem.is_goal(current_state):
            end_time = time.perf_counter()
            elapsed_ms = (end_time - start_time) * 1000

            actions: List[str] = []
            curr = current_node
            while curr.parent is not None:
                actions.append(curr.action)
                curr = curr.parent
            actions.reverse()

            stats = {
                "expanded_nodes": expanded_nodes,
                "nodes_expanded": expanded_nodes,
                "max_frontier_size": max_frontier_size,
                "time_ms": elapsed_ms,
                "execution_time_ms": elapsed_ms,
                "total_cost": current_node.g_cost
            }
            return actions, current_node.g_cost, stats

        expanded_nodes += 1

        # Mở rộng các trạng thái kế tiếp
        for action in problem.get_actions(current_state):
            next_state, step_cost = problem.get_successor(current_state, action)
            new_g = current_node.g_cost + step_cost

            # Chỉ duyệt tiếp nếu tìm được đường đi ngắn hơn (g nhỏ hơn)
            if next_state not in cost_so_far or new_g < cost_so_far[next_state]:
                h_val = heuristic_engine.calculate(next_state)

                # Cắt tỉa nhánh bế tắc (Deadlock Pruning)
                if h_val == float('inf'):
                    continue

                cost_so_far[next_state] = new_g
                counter += 1
                child_node = AStarNode(
                    state=next_state,
                    parent=current_node,
                    action=action,
                    g_cost=new_g,
                    h_cost=h_val
                )
                heapq.heappush(frontier, (child_node.f_cost, child_node.h_cost, counter, child_node))

    # Không tìm thấy đường đi
    end_time = time.perf_counter()
    elapsed_ms = (end_time - start_time) * 1000
    stats = {
        "expanded_nodes": expanded_nodes,
        "nodes_expanded": expanded_nodes,
        "max_frontier_size": max_frontier_size,
        "time_ms": elapsed_ms,
        "execution_time_ms": elapsed_ms,
        "total_cost": 0
    }
    return None, 0, stats