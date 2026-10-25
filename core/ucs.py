"""
Module: core/ucs.py
Mo ta: Cai dat thuat toan Uniform Cost Search (UCS) tim loi giai co chi phi thap nhat cho Sokoban.
"""

import heapq
import time
import sys
from typing import List, Tuple, Optional, Dict
from core.state import State
from core.problem import SokobanProblem


class Node:
    def __init__(self, state: State, parent: Optional['Node'] = None, action: Optional[str] = None, cost: int = 0):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost


def ucs_search(problem: SokobanProblem) -> Tuple[Optional[List[str]], int, Dict]:
    start_time = time.perf_counter()

    start_node = Node(state=problem.initial_state, cost=0)
    counter = 0
    frontier: List[Tuple[int, int, Node]] = []
    heapq.heappush(frontier, (0, counter, start_node))

    # Bang luu chi phi toi uu da tim thay toi tung State
    cost_so_far: Dict[State, int] = {problem.initial_state: 0}

    expanded_nodes = 0
    max_frontier_size = 1
    last_print_time = start_time

    while frontier:
        max_frontier_size = max(max_frontier_size, len(frontier))
        current_cost, _, current_node = heapq.heappop(frontier)
        current_state = current_node.state

        # Bo qua neu da co duong di tot hon toi state nay
        if current_cost > cost_so_far.get(current_state, float('inf')):
            continue

        # In tien do dinh ky neu tim kiem lau
        now = time.perf_counter()
        if now - last_print_time > 3.0:
            sys.stdout.write(f"[UCS exploring...] Expanded: {expanded_nodes:,} | Frontier: {len(frontier):,} | Cost: {current_cost}\n")
            sys.stdout.flush()
            last_print_time = now

        # Kiem tra dich khi lay node ra khoi hang doi uu tien
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

        # Sinh cac trang thai ke tiep
        for action in problem.get_actions(current_state):
            next_state, step_cost = problem.get_successor(current_state, action)
            new_cost = current_node.cost + step_cost

            # Them vao frontier neu chua toi hoac co chi phi tot hon
            if next_state not in cost_so_far or new_cost < cost_so_far[next_state]:
                cost_so_far[next_state] = new_cost
                next_node = Node(state=next_state, parent=current_node, action=action, cost=new_cost)
                counter += 1
                heapq.heappush(frontier, (new_cost, counter, next_node))

    # Khong tim thay loi giai
    end_time = time.perf_counter()
    stats = {
        "expanded_nodes": expanded_nodes,
        "max_frontier_size": max_frontier_size,
        "time_ms": (end_time - start_time) * 1000,
        "total_cost": 0
    }
    return None, 0, stats
