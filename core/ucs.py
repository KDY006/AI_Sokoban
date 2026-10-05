"""
Module: core/ucs.py
Phụ trách: Duy (Leader - Core Architecture)
Mô tả: Cài đặt giải thuật Uniform Cost Search (UCS) theo đúng R2.
"""

import heapq
import time
from typing import List, Tuple, Optional, Dict
from core.state import State
from core.problem import SokobanProblem


class Node:
    """
    Nút trên cây tìm kiếm (Search Tree Node).
    """
    def __init__(self, state: State, parent: Optional['Node'] = None, action: Optional[str] = None, cost: int = 0):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost


def ucs_search(problem: SokobanProblem) -> Tuple[Optional[List[str]], int, Dict]:
    """
    Thực thi giải thuật Uniform Cost Search (UCS).
    Đầu ra chuẩn:
        - actions: Danh sách hành động ['North', 'East', ...]
        - total_cost: Tổng chi phí
        - stats: Chỉ số thực nghiệm phục vụ R3 (expanded nodes, frontier, time)
    """
    start_time = time.perf_counter()

    start_node = Node(state=problem.initial_state, cost=0)
    
    # Priority Queue lưu: (cost, counter, node)
    # Counter đóng vai trò tie-breaker O(1), tránh lỗi so sánh State khi chi phí bằng nhau
    counter = 0
    frontier: List[Tuple[int, int, Node]] = []
    heapq.heappush(frontier, (0, counter, start_node))

    # Bảng chi phí tối ưu đã tìm thấy tới từng State: cost_so_far
    cost_so_far: Dict[State, int] = {problem.initial_state: 0}

    expanded_nodes = 0
    max_frontier_size = 1
    last_print_time = start_time

    while frontier:
        max_frontier_size = max(max_frontier_size, len(frontier))
        current_cost, _, current_node = heapq.heappop(frontier)
        current_state = current_node.state

        # Nếu chi phí của node này lớn hơn chi phí tối ưu đã lưu -> Bỏ qua
        if current_cost > cost_so_far.get(current_state, float('inf')):
            continue

        # In log tiến độ định kỳ (mỗi 3 giây) để theo dõi không gian duyệt của UCS
        now = time.perf_counter()
        if now - last_print_time > 3.0:
            print(f"[UCS đang duyệt...] Số node đã mở rộng: {expanded_nodes:,} | Frontier: {len(frontier):,} | Chi phí g(n): {current_cost}")
            last_print_time = now

        # Goal Test thực hiện khi LẤY NODE RA khỏi Frontier (đảm bảo tính tối ưu của UCS)
        if problem.is_goal(current_state):
            end_time = time.perf_counter()
            actions = []
            curr = current_node
            while curr.parent is not None:
                actions.append(curr.action)
                curr = curr.parent
            actions.reverse()

            stats = {
                "expanded_nodes": expanded_nodes,
                "max_frontier_size": max_frontier_size,
                "time_ms": (end_time - start_time) * 1000,
                "total_cost": current_node.cost
            }
            return actions, current_node.cost, stats

        expanded_nodes += 1

        # Sinh trạng thái kế tiếp
        for action in problem.get_actions(current_state):
            next_state, step_cost = problem.get_successor(current_state, action)
            new_cost = current_node.cost + step_cost

            if next_state not in cost_so_far or new_cost < cost_so_far[next_state]:
                cost_so_far[next_state] = new_cost
                next_node = Node(state=next_state, parent=current_node, action=action, cost=new_cost)
                counter += 1
                heapq.heappush(frontier, (new_cost, counter, next_node))

    # Không có lời giải
    end_time = time.perf_counter()
    stats = {
        "expanded_nodes": expanded_nodes,
        "max_frontier_size": max_frontier_size,
        "time_ms": (end_time - start_time) * 1000,
        "total_cost": 0
    }
    return None, 0, stats