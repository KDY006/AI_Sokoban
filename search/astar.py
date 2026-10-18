"""
Module: search/astar.py
Phụ trách: Quý
Mô tả: Cài đặt thuật toán A* cho bài toán Sokoban (R2).
       Sử dụng hàm Heuristic h(n) được mô-đun hóa tại search/heuristic.py
       (Min-Cost Bipartite Matching kết hợp Hungarian BFS).
"""

import heapq
import time
from typing import Dict, List, Optional, Tuple

from core.problem import SokobanProblem
from core.state import State
from search.heuristic import SokobanHeuristic

__all__ = ["astar_search", "AStarNode", "SokobanHeuristic"]


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